// Backend-independent session state and bounded at-most-once command ledger.
#pragma once
#include "cwm_protocol.hpp"
#include "product_language.hpp"
#include "cwm_transport.hpp"
#include "tile_semantics.hpp"
#include <algorithm>
#include <cmath>
#include <deque>
#include <limits>
#include <optional>
#include <random>
#include <set>
#include <string>
#include <string_view>
#include <tuple>
#include <unordered_map>

namespace cdda::cwm {

inline uint64_t fresh_identity() {
    std::random_device random;
    const uint64_t value = (uint64_t(random()) << 32) ^ random();
    return value ? value : 1;
}

inline std::string_view fb_string_view(const flatbuffers::String* s) {
    return s ? std::string_view(s->c_str(), s->size()) : std::string_view{};
}

inline bool valid_cwm_string(const flatbuffers::String* s, size_t max_len, bool allow_empty = true) {
    return s && s->size() <= max_len && (allow_empty || s->size() > 0) &&
           fb_string_view(s).find('\0') == std::string_view::npos;
}

struct CancelActivityInfo {
    uint64_t command_id{0};
    uint64_t activity_token{0};
    CDDA::CWM::ActivityKind kind{CDDA::CWM::ActivityKind::NONE};
};

inline std::optional<CancelActivityInfo> extract_cancel_request(const CDDA::CWM::CwmMessage& msg) {
    using CDDA::CWM::ActivityKind;
    if (const auto* r = msg.payload_as_CancelActivityRequest())
        return CancelActivityInfo{r->command_id(), r->activity_token(), r->kind()};
    if (const auto* r = msg.payload_as_CancelConsumptionRequest())
        return CancelActivityInfo{r->command_id(), r->activity_token(), ActivityKind::CONSUME};
    if (const auto* r = msg.payload_as_CancelFirstAidRequest())
        return CancelActivityInfo{r->command_id(), r->activity_token(), ActivityKind::FIRST_AID};
    if (const auto* r = msg.payload_as_CancelCraftingRequest())
        return CancelActivityInfo{r->command_id(), r->activity_token(), ActivityKind::CRAFT};
    if (const auto* r = msg.payload_as_CancelReloadRequest())
        return CancelActivityInfo{r->command_id(), r->activity_token(), ActivityKind::RELOAD};
    if (const auto* r = msg.payload_as_CancelItemTransferRequest())
        return CancelActivityInfo{r->command_id(), r->activity_token(), ActivityKind::ITEM_TRANSFER};
    if (const auto* r = msg.payload_as_CancelReadingRequest())
        return CancelActivityInfo{r->command_id(), r->activity_token(), ActivityKind::READ};
    if (const auto* r = msg.payload_as_CancelDisassemblyRequest())
        return CancelActivityInfo{r->command_id(), r->activity_token(), ActivityKind::DISASSEMBLE};
    if (const auto* r = msg.payload_as_CancelLiquidTransferRequest())
        return CancelActivityInfo{r->command_id(), r->activity_token(), ActivityKind::LIQUID_TRANSFER};
    return std::nullopt;
}

struct ActiveWorkState {
    CDDA::CWM::ActivityKind kind{CDDA::CWM::ActivityKind::NONE};
    uint64_t token{0};
    int32_t total{0};
    int32_t remaining{0};
    bool inserting{false};
    bool skimming{false};
    std::string name;
    std::string progress_text;

    bool active() const { return token != 0 && kind != CDDA::CWM::ActivityKind::NONE; }
    bool is(CDDA::CWM::ActivityKind k) const { return active() && kind == k; }

    const char* trace_label() const {
        using CDDA::CWM::ActivityKind;
        switch (kind) {
            case ActivityKind::LIQUID_TRANSFER: return "filling_liquid";
            case ActivityKind::DISASSEMBLE:     return "disassembling";
            case ActivityKind::READ:            return "reading";
            case ActivityKind::ITEM_TRANSFER:   return "transferring";
            case ActivityKind::CRAFT:           return "crafting";
            case ActivityKind::FIRST_AID:       return "first_aid";
            case ActivityKind::RELOAD:          return "reloading";
            case ActivityKind::CONSUME:         return "consuming";
            default:                            return "none";
        }
    }
};

inline ActiveWorkState extract_active_work(const CDDA::CWM::WorldSnapshot& world) {
    using CDDA::CWM::ActivityKind;
    ActiveWorkState out;
    if (const auto* liquid = world.liquid_transfer()) {
        out.kind = ActivityKind::LIQUID_TRANSFER;
        out.token = liquid->token();
    } else if (const auto* dis = world.disassembly()) {
        out.kind = ActivityKind::DISASSEMBLE;
        out.token = dis->token();
        out.total = 10000000;
        out.remaining = 10000000 - dis->progress();
        if (dis->name()) out.name = dis->name()->str();
    } else if (const auto* read = world.reading()) {
        out.kind = ActivityKind::READ;
        out.token = read->token();
        out.total = read->total_moves();
        out.remaining = read->remaining_moves();
        out.skimming = read->skimming();
        if (read->book_name()) out.name = read->book_name()->str();
        if (read->progress()) out.progress_text = read->progress()->str();
    } else if (const auto* tr = world.item_transfer()) {
        out.kind = ActivityKind::ITEM_TRANSFER;
        out.token = tr->token();
        out.total = tr->total_moves();
        out.remaining = tr->remaining_moves();
        out.inserting = tr->inserting();
    } else if (const auto* cr = world.crafting()) {
        out.kind = ActivityKind::CRAFT;
        out.token = cr->token();
        out.total = 10000000;
        out.remaining = 10000000 - cr->progress();
    } else if (const auto* aid = world.first_aid()) {
        out.kind = ActivityKind::FIRST_AID;
        out.token = aid->token();
        out.total = aid->total_moves();
        out.remaining = aid->remaining_moves();
    } else if (const auto* rel = world.reload()) {
        out.kind = ActivityKind::RELOAD;
        out.token = rel->token();
        out.total = rel->total_moves();
        out.remaining = rel->remaining_moves();
    } else if (const auto* con = world.consumption()) {
        out.kind = ActivityKind::CONSUME;
        out.token = con->token();
        out.total = con->total_moves();
        out.remaining = con->remaining_moves();
    }
    return out;
}

inline bool valid_rest(const CDDA::CWM::RestState* rest) {
    return rest && rest->speed_multiplier()==1 && rest->token() && int(rest->phase())>=0 && int(rest->phase())<=2 && rest->progress()>=-1 && rest->progress()<=100 &&
        (rest->phase()==CDDA::CWM::RestPhase::WAITING || rest->progress()==-1) &&
        (rest->phase()!=CDDA::CWM::RestPhase::SLEEPING || !rest->interruptible());
}
inline bool valid_missions(const CDDA::CWM::MissionView* v) {
    if(!v || !v->query_id() || v->tracked_id() < -1 || !v->entries() || v->entries()->size()>2048 || !valid_cwm_string(v->error(),4096))return false;
    if(v->error()->size())return !v->view_id() && !v->entries()->size() && v->tracked_id()==-1 && !v->truncated();
    if(!v->view_id())return false;
    std::set<int> ids;unsigned tracked=0;
    for(const auto* e:*v->entries()) {
        if(!e || e->id()<0 || !ids.insert(e->id()).second || unsigned(e->state())>2 ||
           !valid_cwm_string(e->title(),4096,false) || !valid_cwm_string(e->description(),16384) || !valid_cwm_string(e->objective(),4096) ||
           !valid_cwm_string(e->giver(),4096) || !valid_cwm_string(e->deadline(),4096) || !valid_cwm_string(e->remaining(),4096) || !valid_cwm_string(e->target_text(),4096) ||
           (!e->deadline()->size() && e->remaining()->size()) || (!e->target() && e->target_text()->size()) ||
           (e->target() && !e->target_text()->size()))return false;
        if(e->tracked() && (e->state()!=CDDA::CWM::MissionState::ACTIVE || e->id()!=v->tracked_id() || ++tracked>1))return false;
    }
    return v->tracked_id()==-1 ? !tracked : tracked==1 || v->truncated();
}
inline bool valid_trade(const CDDA::CWM::TradeView* v) {
    if(!v || !v->trade_id() || !v->quote_id() || !(v->npc_id()>>63) ||
       !valid_cwm_string(v->name(),4096,false) || !valid_cwm_string(v->title(),4096) || !valid_cwm_string(v->error(),4096) ||
       !v->entries() || v->entries()->size()>2048 || v->your_value()<0 || v->your_value()>INT32_MAX ||
       v->their_value()<0 || v->their_value()>INT32_MAX || v->balance()<INT32_MIN || v->balance()>INT32_MAX ||
       v->remembered_balance()<INT32_MIN || v->remembered_balance()>INT32_MAX || v->credit_limit()<0 ||
       v->credit_limit()>INT32_MAX || v->service_cost()<INT32_MIN || v->service_cost()>INT32_MAX)return false;
    uint32_t id=0;
    for(const auto* e:*v->entries()) {
        if(!e || e->id()!=++id || e->parent_id()>v->entries()->size() || e->parent_id()==id ||
           !valid_cwm_string(e->type_id(),1024,false) || !valid_cwm_string(e->name(),16384,false) ||
           !valid_cwm_string(e->category(),1024) || !valid_cwm_string(e->source(),4096) || !valid_cwm_string(e->reason(),4096) ||
           e->available()<=0 || e->selected()<0 || e->selected()>e->available() || e->unit_price()<0 || e->unit_price()>INT32_MAX)return false;
    }
    // Parent links must stay in one party and cannot form cycles.
    for(const auto* e:*v->entries()) {
        auto p=e->parent_id();unsigned depth=0;
        while(p) {
            const auto* parent=v->entries()->Get(p-1);
            if(++depth>64 || parent->trader()!=e->trader())return false;
            p=parent->parent_id();
        }
    }
    return true;
}
inline bool valid_decision(const CDDA::CWM::DecisionPrompt* prompt) {
    if(!prompt || !prompt->decision_id() || !valid_cwm_string(prompt->text(),16384) || !prompt->choices() ||
        !prompt->choices()->size() || prompt->choices()->size()>9 || prompt->cancel_choice() < -1 ||
        prompt->cancel_choice()>=int(prompt->choices()->size()))return false;
    for(const auto* label:*prompt->choices())if(!valid_cwm_string(label,16384,false))return false;
    if (const auto* c = prompt->conversation()) {
        if (prompt->medical() || !(c->npc_id() & (uint64_t(1)<<63)) ||
            !valid_cwm_string(c->speaker(),4096,false) ||
            !valid_cwm_string(c->topic(),1024,false) || !valid_cwm_string(c->history(),262144) ||
            prompt->cancel_choice()!=int(prompt->choices()->size())-1) return false;
    }
    if (prompt->medical()) {
        if (prompt->medical()->size() > 128) return false;
        std::set<std::string_view> ids; std::set<int> choices;
        for (const auto* p : *prompt->medical()) {
            if (!p || !valid_cwm_string(p->body_id(),128,false) || !ids.insert(fb_string_view(p->body_id())).second ||
                !valid_cwm_string(p->name(),512,false) || !valid_cwm_string(p->description(),16384) || !valid_cwm_string(p->health_text(),512) ||
                p->choice() < -1 || p->choice() >= int(prompt->choices()->size()) || (p->choice() >= 0 && p->choice() == prompt->cancel_choice()) ||
                (p->choice() >= 0 && !choices.insert(p->choice()).second) || p->health_quarters() < -1 || p->health_quarters() > 20 ||
                p->hp_current() < -1 || p->hp_max() < -1 || (p->hp_current() == -1) != (p->hp_max() == -1) ||
                (p->hp_max() >= 0 && (p->hp_max() == 0 || p->hp_current() > p->hp_max() || p->health_quarters() < 0))) return false;
        }
    }
    return true;
}
inline bool valid_inventory(const CDDA::CWM::InventoryView* view) {
    if (!view || !view->query_id() || !view->entries() || !view->pockets() ||
        view->entries()->size() > 2048 || view->pockets()->size() > 8192 || !valid_cwm_string(view->error(), 2048)) return false;
    if (view->error()->size()) return !view->view_id() && !view->entries()->size() && !view->pockets()->size();
    if (!view->view_id() || view->weight_grams() < 0 || view->weight_capacity_grams() < 0 ||
        view->volume_ml() < 0 || view->volume_capacity_ml() < 0) return false;
    if (view->external_coord()) {
        if (!valid_cwm_string(view->external_label(),2048,false) || view->external_coord()->z() < -1024 || view->external_coord()->z()>1024 ||
            view->external_capacity_ml()<0 || view->external_remaining_ml()<0 || view->external_remaining_ml()>view->external_capacity_ml())return false;
    } else if (view->external_capacity_ml() || view->external_remaining_ml()) return false;
    std::vector<unsigned> depths(1, 0);
    std::vector<bool> external(1,false);
    depths.reserve(view->entries()->size() + 1);
    external.reserve(view->entries()->size() + 1);
    uint32_t id = 0;
    for (const auto* entry : *view->entries()) {
        if (!entry || entry->id() != ++id || entry->parent_id() >= id || entry->pocket_index() < -1 ||
            (!entry->parent_id() && entry->pocket_index() != -1) ||
            (entry->parent_id() && (entry->worn() || entry->wielded())) ||
            (entry->worn() && entry->wielded()) || entry->quick_slot() > 9 || entry->ui_order() > 2048 ||
            entry->weight_grams() < 0 || entry->volume_ml() < 0 || entry->length_mm() < 0 || entry->access_moves() < 0 ||
            !valid_cwm_string(entry->type_id(), 1024, false) || !valid_cwm_string(entry->name(), 16384, false) || !valid_cwm_string(entry->category(), 1024) ||
            !entry->reasons() || entry->reasons()->size() != 8 || entry->consume_moves() < 0 ||
            !valid_cwm_string(entry->consume_label(), 128) || !valid_cwm_string(entry->consume_warning(), 2048) || !valid_cwm_string(entry->transfer_reason(), 2048)) return false;
        for (unsigned i = 0; i < 8; ++i)
            if (!valid_cwm_string(entry->reasons()->Get(i), 2048) ||
                bool(entry->actions() & (1 << i)) == bool(entry->reasons()->Get(i)->size())) return false;
        if ((entry->actions() & 16) && (!entry->consume_moves() || !entry->consume_label()->size())) return false;
        if ((entry->actions() & 64) && (!entry->book() || !entry->book()->chapter_moves())) return false;
        if ((entry->actions() & 128) && !entry->disassembly()) return false;
        if(entry->seal() && (!valid_cwm_string(entry->seal()->reason(),2048) || entry->external() || !entry->container()))return false;
        if(entry->liquid() && (!valid_cwm_string(entry->liquid()->reason(),2048)))return false;
        if (const auto* work=entry->disassembly())
            if (work->estimated_moves()<0 || work->progress()<0 || work->progress()>10000000 ||
                (!work->resume() && work->progress()) ||
                ((entry->actions() & 128) && work->estimated_moves()>INT32_MAX)) return false;
        if (const auto* book=entry->book())
            if(book->chapter_moves()<0 || !valid_cwm_string(book->summary(),2048,false))return false;
        if (entry->external() && (!view->external_coord() || entry->worn() || entry->wielded() || entry->actions() || entry->quick_slot() || entry->ui_order())) return false;
        if(entry->parent_id() && entry->external()!=external[entry->parent_id()])return false;
        external.push_back(entry->external());
        depths.push_back(entry->parent_id() ? depths[entry->parent_id()] + 1 : 0);
        if (depths.back() > 32) return false;
    }
    std::set<std::pair<uint32_t,uint32_t>> pockets;
    for (const auto* pocket : *view->pockets()) {
        if (!pocket || !pocket->owner_id() || pocket->owner_id() > id || pocket->index() >= 8192 ||
            !valid_cwm_string(pocket->name(), 2048) || pocket->capacity_ml() < 0 || pocket->capacity_grams() < 0 ||
            pocket->max_length_mm() < 0 || pocket->access_moves() < 0 ||
            !pockets.emplace(pocket->owner_id(), pocket->index()).second) return false;
    }
    for (const auto* entry : *view->entries())
        if (entry->pocket_index() >= 0 && !pockets.count({entry->parent_id(), uint32_t(entry->pocket_index())})) return false;
    return true;
}
inline bool valid_crafting(const CDDA::CWM::CraftingView* view) {
    if (!view || !view->query_id() || !view->batch() || view->batch() > 20 || !view->entries() ||
        view->entries()->size() > 256 || int(view->filter()) > 3 || !valid_cwm_string(view->error(), 2048)) return false;
    if (view->error()->size()) return !view->view_id() && !view->entries()->size();
    if (!view->view_id()) return false;
    uint32_t id = 0;
    for (const auto* e : *view->entries())
        if (!e || e->id() != ++id || !valid_cwm_string(e->recipe_id(), 1024, false) || !valid_cwm_string(e->result_type(), 1024, false) ||
            !valid_cwm_string(e->name(), 16384, false) || !valid_cwm_string(e->requirements(), 16384) || !valid_cwm_string(e->reason(), 2048) ||
            e->recent_rank() > 20 || (view->filter()==CDDA::CWM::CraftingFilter::UNFINISHED && !e->resume()) || (view->filter()==CDDA::CWM::CraftingFilter::FAVORITES && !e->favorite()) ||
            (view->filter()==CDDA::CWM::CraftingFilter::RECENT && !e->recent_rank()) || e->expected_moves() < 0 || e->progress() < 0 || e->progress() > 10000000 || (!e->resume() && e->progress())) return false;
    return true;
}
enum class SessionState { Disconnected, HelloSent, Accepted, Syncing, Running, Resyncing, Rejected };

inline bool valid_presentation(const CDDA::CWM::WorldSnapshot* world) {
    const auto* cues = world->presentation_events();
    if (!cues) return true;
    if (cues->size()>128 || (world->full() && cues->size())) return false;
    uint64_t previous=0;
    for (const auto* cue : *cues) {
        if (!cue || cue->id()<=previous || cue->kind()<CDDA::CWM::PresentationKind::ATTACK ||
            cue->kind()>CDDA::CWM::PresentationKind::SOUND || cue->heard_volume()>200 ||
            !valid_cwm_string(cue->description(), 4096) ||
            !valid_cwm_string(cue->sound_category(), 128)) return false;
        if (cue->kind()==CDDA::CWM::PresentationKind::SOUND ? cue->actor()!=0 : cue->actor()==0) return false;
        previous=cue->id();
    }
    return true;
}
inline bool valid_world(const CDDA::CWM::WorldSnapshot* world) {
    if (!world || !valid_presentation(world) || !world->origin() || !world->state_id() || !world->entities() ||
        !world->vehicles() || !world->fields() || world->entities()->size() > 8192 ||
        world->vehicles()->size() > 8192 || world->fields()->size() > 65536) return false;
    if (world->full() && (!world->chunks() || !world->chunks()->size() || world->chunks()->size() > 1024)) return false;
    if (!world->full() && world->chunks() && world->chunks()->size()) return false;
    if (world->inventory_work() && (!world->inventory_work()->command_id() ||
        world->inventory_work()->remaining_time_ms() > world->inventory_work()->total_time_ms())) return false;
    if (const auto* slots = world->quick_slots()) {
        if (slots->size() != 9) return false;
        std::set<std::string_view> identities;
        unsigned n = 0;
        for (const auto* slot : *slots) {
            if (!slot || slot->slot() != ++n || !slot->binding_id() ||
                !valid_cwm_string(slot->type_id(), 1024) ||
                !valid_cwm_string(slot->name(), 16384) ||
                !valid_cwm_string(slot->category(), 1024) ||
                (slot->actions() & ~127) || (slot->worn() && slot->wielded())) return false;
            const auto id = fb_string_view(slot->binding_id());
            if (!id.empty() && (id.size() != 32 || !std::all_of(id.begin(), id.end(), [](char c) {
                return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
            }) || !identities.insert(id).second || !slot->type_id()->size() || !slot->name()->size())) return false;
            if (id.empty() && (slot->type_id()->size() || slot->name()->size() || slot->category()->size() ||
                slot->charges() || slot->count_by_charges() || slot->worn() || slot->wielded() || slot->actions() || slot->rotten())) return false;
        }
    }
    const auto valid_items = [](const auto* items) {
        if (!items || items->size() > 8192) return false;
        uint32_t index = 0;
        for (const auto* item : *items) {
            if (!item || item->stack_index() != index++ || !item->type_id() ||
                item->type_id()->size() == 0 || item->type_id()->size() > 1024 ||
                !item->name() || item->name()->size() > 16384) return false;
        }
        return true;
    };
    if(world->rest() && !valid_rest(world->rest()))return false;
    if(world->liquid_transfer() && !world->liquid_transfer()->token())return false;
    if (const auto* consumption = world->consumption()) {
        if (!consumption->token() || consumption->total_moves() <= 0 ||
            consumption->remaining_moves() < 0 || consumption->remaining_moves() > consumption->total_moves()) return false;
    }
    if (int(bool(world->consumption())) + int(bool(world->first_aid())) + int(bool(world->crafting())) + int(bool(world->reload())) + int(bool(world->item_transfer())) + int(bool(world->reading())) + int(bool(world->disassembly())) + int(bool(world->rest())) + int(bool(world->liquid_transfer())) > 1) return false;
    if (const auto* work=world->disassembly()) {
        if (!work->token() || work->progress()<0 || work->progress()>10000000 ||
            !valid_cwm_string(work->name(), 16384, false)) return false;
    }
    if (const auto* reading=world->reading()) {
        if(!reading->token() || reading->total_moves()<=0 || reading->remaining_moves()<0 ||
            reading->remaining_moves()>reading->total_moves() || !valid_cwm_string(reading->book_name(),16384,false) ||
            !valid_cwm_string(reading->progress(),2048))return false;
    }
    if (const auto* transfer = world->item_transfer()) {
        if (!transfer->token() || transfer->total_moves() < 0 || transfer->remaining_moves() < 0 ||
            transfer->remaining_moves() > transfer->total_moves() || (transfer->inserting() && !transfer->total_moves())) return false;
    }
    if (const auto* reload = world->reload()) {
        if (!reload->token() || reload->total_moves() <= 0 || reload->remaining_moves() < 0 ||
            reload->remaining_moves() > reload->total_moves()) return false;
    }
    if (const auto* gun = world->ranged_weapon()) {
        if (!gun->token() || !valid_cwm_string(gun->name(), 16384, false) || !valid_cwm_string(gun->reason(), 16384) ||
            gun->ammo() < 0 || gun->range() < 0 || !std::isfinite(gun->recoil()) ||
            gun->recoil() < 0 || gun->recoil() > 1000000) return false;
    }
    if (const auto* craft = world->crafting()) {
        if (!craft->token() || craft->progress() < 0 || craft->progress() > 10000000) return false;
    }
    if (const auto* aid = world->first_aid()) {
        if (!aid->token() || aid->total_moves() <= 0 || aid->remaining_moves() < 0 ||
            aid->remaining_moves() > aid->total_moves()) return false;
    }
    if (world->owned_items() && !valid_items(world->owned_items())) return false;
    if (const auto* status = world->avatar_status()) {
        const auto valid_value = [&](const auto* value) {
            return value && valid_cwm_string(value->id(), 128, false) &&
                valid_cwm_string(value->label(), 256, false) && valid_cwm_string(value->text(), 2048) &&
                valid_cwm_string(value->color(), 64, false) &&
                value->perceived_level() >= -1 && value->perceived_level() <= 10;
        };
        if (!valid_value(status->stamina()) || fb_string_view(status->stamina()->id()) != "stamina" ||
            !status->needs() || status->needs()->size() > 32 ||
            !status->body_parts() || status->body_parts()->size() > 64) return false;
        std::set<std::string_view> needs, parts;
        for (const auto* need : *status->needs())
            if (!valid_value(need) || !needs.insert(fb_string_view(need->id())).second) return false;
        for (const auto* part : *status->body_parts())
            if (!part || !valid_cwm_string(part->id(), 128, false) ||
                !valid_cwm_string(part->label(), 256, false) || !valid_value(part->health()) ||
                !valid_value(part->temperature()) || !parts.insert(fb_string_view(part->id())).second) return false;
        for (const auto* part : *status->body_parts()) if (part->conditions()) {
            if (part->conditions()->size() > 64) return false;
            for (const auto* condition : *part->conditions())
                if (!valid_cwm_string(condition, 2048, false)) return false;
        }
    }
    if (world->ground_item_tiles()) {
        if (world->ground_item_tiles()->size() > 65536) return false;
        std::set<std::tuple<int, int, int>> coords;
        for (const auto* tile : *world->ground_item_tiles()) {
            if (!tile || !tile->coord() || !valid_items(tile->items()) ||
                (tile->storage() && !valid_cwm_string(tile->storage_label(), 2048, false))) return false;
            const auto* p = tile->coord();
            if (p->x() < 0 || p->x() >= 132 || p->y() < 0 || p->y() >= 132 ||
                p->z() < -1024 || p->z() > 1024 ||
                !coords.emplace(p->x(), p->y(), p->z()).second) return false;
        }
    }
    if (const auto* clock = world->clock()) {
        if (!std::isfinite(clock->time_scale()) || clock->time_scale() < .25f || clock->time_scale() > (clock->speed_context()==CDDA::CWM::SpeedContext::REST?4096.f:4.f) ||
            int(clock->speed_context())<0 || int(clock->speed_context())>1 ||
            (clock->speed_context()==CDDA::CWM::SpeedContext::REST && (!clock->realtime() || !world->rest())) ||
            (clock->pause_reasons() & ~uint32_t(31)) ||
            (clock->continuous_motion() && !clock->realtime())) return false;
    }
    if(world->clock() && world->rest() && world->rest()->accelerated()!=
        (world->clock()->speed_context()==CDDA::CWM::SpeedContext::REST && world->clock()->time_scale()>4.f))return false;
    std::unordered_map<uint64_t, const CDDA::CWM::EntityState*> actor_states;
    actor_states.reserve(world->entities()->size());
    bool player = false;
    for (const auto* actor : *world->entities()) {
        if (!actor || !actor->id() || !actor->pos() || !actor_states.emplace(actor->id(), actor).second) return false;
        if (actor->type() < CDDA::CWM::EntityType::PLAYER || actor->type() > CDDA::CWM::EntityType::MONSTER ||
            (actor->id() == 1) != (actor->type() == CDDA::CWM::EntityType::PLAYER) ||
            !std::isfinite(actor->rotation()) || actor->hp_percent() > 100 ||
            !std::isfinite(actor->motion_seconds()) || actor->motion_seconds() < .01f || actor->motion_seconds() > 60.f) return false;
        const auto* p = actor->pos();
        if (!std::isfinite(p->x()) || !std::isfinite(p->y()) || !std::isfinite(p->z()) ||
            std::abs(p->x()) > 32767 || std::abs(p->y()) > 32767 || std::abs(p->z()) > 1024) return false;
        const uint32_t posture = actor->state_flags() & (RUNNING | CROUCHING | PRONE);
        if (posture && ((posture & (posture - 1)) || actor->id() != 1)) return false;
        if (actor->id() == 1) player = true;
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
        if (!spawn || !spawn->state() || !actor_states.count(spawn->state()->id()) ||
            !spawned_ids.insert(spawn->state()->id()).second) return false;
        const auto* declared = spawn->state();
        const auto* actor = actor_states.at(declared->id());
        const auto string_equal = [](const auto* a, const auto* b) {
            return a && b ? fb_string_view(a) == fb_string_view(b) : a == b;
        };
        if (!declared->pos() || actor->type() != declared->type() ||
            actor->pos()->x() != declared->pos()->x() || actor->pos()->y() != declared->pos()->y() ||
            actor->pos()->z() != declared->pos()->z() || actor->rotation() != declared->rotation() ||
            actor->animation_hint() != declared->animation_hint() || actor->hp_percent() != declared->hp_percent() ||
            actor->perceived() != declared->perceived() || actor->state_flags() != declared->state_flags() ||
            actor->motion_seconds() != declared->motion_seconds() ||
            !string_equal(actor->type_id(), declared->type_id()) || !string_equal(actor->name(), declared->name())) return false;
    }
    if (world->removed()) for (const auto* removed : *world->removed())
        if (!removed || !removed->id() || actor_states.count(removed->id()) ||
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
        if (ready() && msg.payload_type() == Payload::CraftingView) {
            if (!valid_crafting(msg.payload_as_CraftingView())) { request_resync(channel); return false; }
            return true;
        }
        if (ready() && msg.payload_type() == Payload::InventoryView) {
            if (!valid_inventory(msg.payload_as_InventoryView())) { request_resync(channel); return false; }
            return true;
        }
        if (ready() && msg.payload_type() == Payload::LanguageState) {
            const auto* value = msg.payload_as_LanguageState();
            if (!value || !value->request_id() || !value->code() ||
                !::cwm::product_language(value->code()->str()) ||
                !valid_cwm_string(value->error(), 2048) ||
                value->accepted() == bool(value->error()->size())) {
                request_resync(channel); return false;
            }
            return true;
        }
        if (msg.payload_type() == Payload::HeartbeatAck) return true;
        if (ready() && msg.payload_type() == Payload::MissionView) {
            if(!valid_missions(msg.payload_as_MissionView())) {request_resync(channel);return false;}
            return true;
        }
        if (ready() && msg.payload_type() == Payload::TradeView) {
            if(!valid_trade(msg.payload_as_TradeView())) {request_resync(channel);return false;}
            return true;
        }
        if (ready() && msg.payload_type() == Payload::TradeClosed) {
            const auto* v=msg.payload_as_TradeClosed();
            if(!v || !v->trade_id() || !valid_cwm_string(v->error(), 4096)) {
                request_resync(channel);return false;
            }
            return true;
        }
        if (ready() && msg.payload_type() == Payload::DecisionPrompt) {
            if(!valid_decision(msg.payload_as_DecisionPrompt())) {request_resync(channel);return false;}
            return true;
        }
        if (ready() && msg.payload_type() == Payload::CommandAck) return true;
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
} // namespace cdda::cwm
