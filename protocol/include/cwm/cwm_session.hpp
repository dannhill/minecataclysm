// Backend-independent session state and bounded at-most-once command ledger.
#pragma once
#include "cwm_protocol.hpp"
#include "cwm_transport.hpp"
#include <algorithm>
#include <cmath>
#include <deque>
#include <limits>
#include <random>
#include <set>
#include <unordered_map>

namespace cdda::cwm {
inline uint64_t fresh_identity() {
    std::random_device random;
    const uint64_t value = (uint64_t(random()) << 32) ^ random();
    return value ? value : 1;
}
enum class SessionState { Disconnected, HelloSent, Accepted, Syncing, Running, Resyncing, Rejected };

inline bool valid_world(const CDDA::CWM::WorldSnapshot* world) {
    if (!world || !world->origin() || !world->state_id() || !world->entities() ||
        !world->vehicles() || !world->fields() || world->entities()->size() > 8192 ||
        world->vehicles()->size() > 8192 || world->fields()->size() > 65536) return false;
    if (world->full() && (!world->chunks() || !world->chunks()->size() || world->chunks()->size() > 1024)) return false;
    if (!world->full() && world->chunks() && world->chunks()->size()) return false;
    std::set<uint64_t> ids;
    std::unordered_map<uint64_t, const CDDA::CWM::EntityState*> actor_states;
    actor_states.reserve(world->entities()->size());
    bool player = false;
    for (const auto* actor : *world->entities()) {
        if (!actor || !actor->id() || !actor->pos() || !ids.insert(actor->id()).second) return false;
        if (actor->type() < CDDA::CWM::EntityType::PLAYER || actor->type() > CDDA::CWM::EntityType::MONSTER ||
            (actor->id() == 1) != (actor->type() == CDDA::CWM::EntityType::PLAYER) ||
            !std::isfinite(actor->rotation()) || actor->hp_percent() > 100) return false;
        const auto* p = actor->pos();
        if (!std::isfinite(p->x()) || !std::isfinite(p->y()) || !std::isfinite(p->z()) ||
            std::abs(p->x()) > 32767 || std::abs(p->y()) > 32767 || std::abs(p->z()) > 1024) return false;
        if (actor->id() == 1) player = true;
        actor_states.emplace(actor->id(), actor);
    }
    if (!player) return false;
    if (world->chunks()) for (const auto* chunk : *world->chunks()) {
        if (!chunk || !chunk->blocks() || !chunk->size_x() || !chunk->size_y() || !chunk->size_z() ||
            chunk->size_x() > 16 || chunk->size_y() > 16 || chunk->size_z() > 3 ||
            chunk->blocks()->size() != size_t(chunk->size_x())*chunk->size_y()*chunk->size_z() ||
            std::abs(int64_t(chunk->chunk_x())) > 1024 || std::abs(int64_t(chunk->chunk_y())) > 1024 ||
            std::abs(int64_t(chunk->chunk_z())) > 1024) return false;
    }
    if (world->tiles()) {
        if (world->tiles()->size() > 65536) return false;
        for (const auto* tile : *world->tiles()) if (!tile || !tile->coord() || !tile->block()) return false;
    }
    for (const auto* vehicle : *world->vehicles()) {
        if (!vehicle || !vehicle->pivot() || (vehicle->components() && vehicle->components()->size() > 1024)) return false;
        if (!std::isfinite(vehicle->pivot()->x()) || !std::isfinite(vehicle->pivot()->y()) ||
            !std::isfinite(vehicle->pivot()->z()) || !std::isfinite(vehicle->rotation())) return false;
        if (vehicle->components()) for (const auto* part : *vehicle->components())
            if (!part || !part->offset() || !std::isfinite(part->offset()->x()) ||
                !std::isfinite(part->offset()->y()) || !std::isfinite(part->offset()->z())) return false;
    }
    std::set<uint64_t> spawned_ids, removed_ids;
    if ((world->spawned() && world->spawned()->size() > world->entities()->size()) ||
        (world->removed() && world->removed()->size() > 8192)) return false;
    if (world->spawned()) for (const auto* spawn : *world->spawned()) {
        if (!spawn || !spawn->state() || !ids.count(spawn->state()->id()) ||
            !spawned_ids.insert(spawn->state()->id()).second) return false;
        const auto* declared = spawn->state();
        const auto* actor = actor_states.at(declared->id());
        const auto string_equal = [](const auto* a, const auto* b) {
            return a && b ? a->str() == b->str() : a == b;
        };
        if (!declared->pos() || actor->type() != declared->type() ||
            actor->pos()->x() != declared->pos()->x() || actor->pos()->y() != declared->pos()->y() ||
            actor->pos()->z() != declared->pos()->z() || actor->rotation() != declared->rotation() ||
            actor->animation_hint() != declared->animation_hint() || actor->hp_percent() != declared->hp_percent() ||
            actor->perceived() != declared->perceived() || actor->state_flags() != declared->state_flags() ||
            !string_equal(actor->type_id(), declared->type_id()) || !string_equal(actor->name(), declared->name())) return false;
    }
    if (world->removed()) for (const auto* removed : *world->removed())
        if (!removed || !removed->id() || ids.count(removed->id()) ||
            !removed_ids.insert(removed->id()).second) return false;
    return true;
}

class ClientSession {
public:
    const uint64_t client_id{fresh_identity()};
    Identity identity;
    SessionState state{SessionState::Disconnected};
    uint64_t revision{0}, sequence{0}, next_command{1}, resync_count{0};
    bool clear_world{false};

    void disconnected() { state = SessionState::Disconnected; tx_ = 0; sequence = 0; }
    bool begin(CwmTransport& channel) {
        disconnected(); state = SessionState::HelloSent;
        MessageBuilder builder(++tx_, 0);
        auto body = builder.build_hello_request("luanti-cwm-2", client_id);
        return channel.send_message(body.data(), body.size());
    }
    MessageBuilder builder() { return MessageBuilder(++tx_, revision, identity); }
    bool ready() const { return state == SessionState::Running; }
    bool request_resync(CwmTransport& channel) {
        if (state == SessionState::Resyncing) return true;
        state = SessionState::Resyncing; ++resync_count;
        expected_resync_ = ++request_id_;
        auto b = builder();
        auto bytes = b.finish_message(CDDA::CWM::Payload::ResyncRequest,
            CDDA::CWM::CreateResyncRequest(b.builder(), expected_resync_).Union());
        return channel.send_message(bytes.data(), bytes.size());
    }
    // True allows the adapter to apply a supported message. World state must
    // be committed only after successful complete ingestion on the main thread.
    bool accept(const CDDA::CWM::CwmMessage& msg, CwmTransport& channel) {
        using CDDA::CWM::Payload;
        if (state == SessionState::HelloSent) {
            const auto* hello = msg.payload_as_HelloResponse();
            if (!hello || !hello->accepted() || hello->protocol_version_major() != PROTOCOL_VERSION_MAJOR ||
                hello->protocol_version_minor() != PROTOCOL_VERSION_MINOR || msg.sequence_number() != 1 ||
                !msg.session_id() || !msg.player_id() || !msg.connection_id() || !hello->next_command_id()) {
                state = SessionState::Rejected; channel.close(); return false;
            }
            clear_world = identity.session && (identity.session != msg.session_id() || identity.player != msg.player_id());
            if (clear_world) { revision = 0; actor_types_.clear(); }
            identity = {msg.session_id(), msg.player_id(), msg.connection_id()};
            next_command = std::max(next_command, hello->next_command_id());
            sequence = 1; expected_resync_ = 0; state = SessionState::Accepted;
            return true;
        }
        if (msg.session_id() != identity.session || msg.player_id() != identity.player ||
            msg.connection_id() != identity.connection) { channel.close(IpcCloseReason::InvalidFrame); return false; }
        if (state == SessionState::Resyncing) {
            const auto* reset = msg.payload_as_WorldReset();
            if (!reset || reset->request_id() != expected_resync_ || msg.sequence_number() <= sequence) return false;
            sequence = msg.sequence_number(); state = SessionState::Syncing; return true;
        }
        if (msg.sequence_number() != sequence + 1) { request_resync(channel); return false; }
        sequence = msg.sequence_number();
        if (msg.payload_type() == Payload::WorldReset) {
            const auto* reset = msg.payload_as_WorldReset();
            if (!reset || reset->request_id() != expected_resync_) { request_resync(channel); return false; }
            state = SessionState::Syncing; return true;
        }
        if (msg.payload_type() == Payload::WorldSnapshot) {
            const auto* world = msg.payload_as_WorldSnapshot();
            const bool syncing = state == SessionState::Syncing;
            if ((!syncing && !ready()) || !valid_world(world) || world->world_revision() != msg.world_revision() ||
                world->world_revision() < revision || (syncing && (!world->full() || world->resync_id() != expected_resync_)) ||
                (!syncing && world->base_revision() != revision)) {
                request_resync(channel); return false;
            }
            // Evolution may change archetype, but an existing native ID
            // cannot silently switch between player, NPC and monster.
            for (const auto* actor : *world->entities()) {
                const auto previous = actor_types_.find(actor->id());
                if (previous != actor_types_.end() && previous->second != actor->type()) {
                    request_resync(channel); return false;
                }
            }
            return true;
        }
        if (msg.payload_type() == Payload::HeartbeatAck) return true;
        if (ready() && (msg.payload_type() == Payload::CommandAck || msg.payload_type() == Payload::DecisionPrompt)) return true;
        request_resync(channel); return false;
    }
    bool commit(const CDDA::CWM::WorldSnapshot& world, CwmTransport& channel) {
        actor_types_.clear();
        for (const auto* actor : *world.entities()) actor_types_.emplace(actor->id(), actor->type());
        revision = world.world_revision(); state = SessionState::Running;
        if (!world.full()) return true;
        auto b = builder();
        auto bytes = b.finish_message(CDDA::CWM::Payload::SnapshotAck,
            CDDA::CWM::CreateSnapshotAck(b.builder(), world.state_id()).Union());
        return channel.send_message(bytes.data(), bytes.size());
    }
private:
    uint64_t tx_{0}, request_id_{0}, expected_resync_{0};
    std::unordered_map<uint64_t, CDDA::CWM::EntityType> actor_types_;
};

struct CommandOutcome { uint64_t id{0}; bool accepted{false}; std::string error; uint64_t revision{0}; };
class CommandLedger {
public:
    enum class Status { Fresh, Pending, Complete, Expired, Conflict, Invalid };
    struct Entry { uint64_t owner; std::string signature; bool complete{false}; CommandOutcome outcome; };
    explicit CommandLedger(size_t capacity = 1024) : capacity_(capacity) {}
    uint64_t next_id() const { return high_water_ + 1; }
    size_t size() const { return entries_.size(); }
    const Entry* find(uint64_t id) const {
        const auto found = entries_.find(id); return found == entries_.end() ? nullptr : &found->second;
    }
    Status begin(uint64_t owner, uint64_t id, const std::string& signature) {
        if (!owner || !id || id == std::numeric_limits<uint64_t>::max()) return Status::Invalid;
        if (const auto* old = find(id)) {
            if (old->owner != owner || old->signature != signature) return Status::Conflict;
            return old->complete ? Status::Complete : Status::Pending;
        }
        if (id <= high_water_) return Status::Expired;
        high_water_ = id;
        while (entries_.size() >= capacity_) {
            const auto victim = std::find_if(order_.begin(), order_.end(), [&](uint64_t key) { return entries_.at(key).complete; });
            if (victim == order_.end()) return Status::Expired;
            entries_.erase(*victim); order_.erase(victim);
        }
        entries_.emplace(id, Entry{owner, signature, false, {id, false, "", 0}}); order_.push_back(id);
        return Status::Fresh;
    }
    void complete(const CommandOutcome& outcome) {
        const auto it = entries_.find(outcome.id);
        if (it != entries_.end() && !it->second.complete) {
            it->second.complete = true; it->second.outcome = outcome;
        }
    }
private:
    size_t capacity_;
    uint64_t high_water_{0};
    std::unordered_map<uint64_t, Entry> entries_;
    std::deque<uint64_t> order_;
};
}
