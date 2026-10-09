#include "cwm/cwm_session.hpp"
#include <iostream>
#include <stdexcept>
using namespace cdda::cwm;
using namespace CDDA::CWM;
#define CHECK(...) do { if (!(__VA_ARGS__)) throw std::runtime_error(#__VA_ARGS__); } while(false)
std::vector<uint8_t> world(int defect) {
    MessageBuilder wire(1, 7, {11,22,33}); auto& f = wire.builder();
    std::vector<flatbuffers::Offset<QuickSlot>> slots;
    for (int n = 1; n <= (defect == 1 ? 8 : 9); ++n) {
        const bool occupied = n == 1 || (defect == 3 && n == 2);
        slots.push_back(CreateQuickSlotDirect(f, defect == 2 ? 1 : n,
            occupied ? (defect == 4 ? "bad" : "0123456789abcdef0123456789abcdef") : "",
            occupied ? "rock" : "", occupied || defect == 5 ? "Stone" : "", "",
            0, false, occupied && defect == 6, occupied && defect == 6, defect == 7 ? 128 : 0, false));
    }
    auto actors = f.CreateVector(std::vector<flatbuffers::Offset<EntityState>>{});
    auto vehicles = f.CreateVector(std::vector<flatbuffers::Offset<VehicleState>>{});
    auto fields = f.CreateVector(std::vector<flatbuffers::Offset<FieldState>>{});
    auto quick = f.CreateVector(slots); Coord3i origin(0,0,0);
    WorldSnapshotBuilder snapshot(f);
    snapshot.add_world_revision(7); snapshot.add_state_id(1); snapshot.add_origin(&origin);
    snapshot.add_entities(actors); snapshot.add_vehicles(vehicles); snapshot.add_fields(fields);
    snapshot.add_quick_slots(quick);
    return wire.finish_message(Payload::WorldSnapshot, snapshot.Finish().Union());
}
int main() {
    for (int defect = 0; defect <= 7; ++defect) {
        const auto bytes = world(defect);
        CHECK(MessageVerifier::verify(bytes.data(), bytes.size()));
        CHECK(valid_world(GetCwmMessage(bytes.data())->payload_as_WorldSnapshot()) == (defect == 0));
    }
    MessageBuilder wire;
    const std::string identity = "0123456789abcdef0123456789abcdef";
    const auto bind = wire.build_quickbar_bind(9, 3, 22, 7, identity);
    const auto* assignment = GetCwmMessage(bind.data())->payload_as_QuickbarBindRequest();
    CHECK(assignment && assignment->command_id() == 9 && assignment->slot() == 3 &&
          assignment->view_id() == 22 && assignment->item_id() == 7 && assignment->expected_binding_id()->str() == identity);
    const auto use = wire.build_quickbar_use(10, 3, identity, EquipmentAction::CONSUME);
    const auto* command = GetCwmMessage(use.data())->payload_as_QuickbarUseRequest();
    CHECK(command && command->command_id() == 10 && command->slot() == 3 &&
          command->binding_id()->str() == identity && command->action() == EquipmentAction::CONSUME);
    std::cout << "Quickbar identity, bounds, uniqueness, empty-slot semantics and commands PASS\n";
}
