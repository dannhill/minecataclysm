#include "cwm/cwm_session.hpp"
#include <iostream>
#include <stdexcept>
using namespace CDDA::CWM;using namespace cdda::cwm;
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main(){
 MessageBuilder wire(1,1);auto bytes=wire.build_rest_request(8,9);auto* r=GetCwmMessage(bytes.data())->payload_as_RestRequest();CHECK(r && r->command_id()==8 && r->expected_token()==9);
 for(int bad=0;bad<6;++bad){MessageBuilder b(1,1);auto& f=b.builder();auto state=CreateRestState(f,bad==1?0:1,bad==2?RestPhase(3):RestPhase::SLEEPING,bad==3,false,bad==4?101:bad==5?0:-1,1);Coord3i origin(0,0,0);WorldSnapshotBuilder wb(f);wb.add_world_revision(1);wb.add_origin(&origin);wb.add_rest(state);auto data=b.finish_message(Payload::WorldSnapshot,wb.Finish().Union());CHECK(MessageVerifier::verify(data.data(),data.size()));auto rest=GetCwmMessage(data.data())->payload_as_WorldSnapshot()->rest();CHECK(valid_rest(rest)==(bad==0));}
 for(unsigned factor:{1u,64u,256u,1024u,0u,2u,1025u}) {
  MessageBuilder b(1,1);auto& f=b.builder();auto state=CreateRestState(f,1,RestPhase::SLEEPING,false,false,-1,factor);
  WorldSnapshotBuilder wb(f);wb.add_rest(state);auto data=b.finish_message(Payload::WorldSnapshot,wb.Finish().Union());
  CHECK(valid_rest(GetCwmMessage(data.data())->payload_as_WorldSnapshot()->rest())==(factor==1));
 }
 for(int bad=0;bad<7;++bad) {
  MessageBuilder b(1,1);auto& f=b.builder();Coord3i origin(0,0,0);Vec3f pos(0,0,0);
  const auto context=bad==3?SpeedContext(2):bad==1?SpeedContext::PLAY:SpeedContext::REST;
  const auto rest=bad==2?flatbuffers::Offset<RestState>{}:CreateRestState(f,1,RestPhase::SLEEPING,false,true,-1,1);
  const auto clock=CreateSimulationState(f,bad!=6,0,bad==4?4097.f:bad==5?0.f:256.f,false,context);
  std::vector<flatbuffers::Offset<EntityState>> actors{CreateEntityState(f,1,EntityType::PLAYER,0,&pos)};
  std::vector<flatbuffers::Offset<VehicleState>> vehicles;std::vector<flatbuffers::Offset<FieldState>> fields;
  const auto av=f.CreateVector(actors);const auto vv=f.CreateVector(vehicles);const auto fv=f.CreateVector(fields);
  WorldSnapshotBuilder wb(f);wb.add_state_id(1);wb.add_origin(&origin);wb.add_entities(av);wb.add_vehicles(vv);wb.add_fields(fv);wb.add_rest(rest);wb.add_clock(clock);
  auto bytes=b.finish_message(Payload::WorldSnapshot,wb.Finish().Union());CHECK(valid_world(GetCwmMessage(bytes.data())->payload_as_WorldSnapshot())==(bad==0));
 }
 {MessageBuilder b(1,1);auto& f=b.builder();auto req=CreateSimulationControlRequest(f,7,SimulationControl::SET_SPEED,1024,SpeedContext::REST);
  auto bytes=b.finish_message(Payload::SimulationControlRequest,req.Union());const auto* parsed=GetCwmMessage(bytes.data())->payload_as_SimulationControlRequest();
  CHECK(parsed->command_id()==7 && parsed->speed_context()==SpeedContext::REST && parsed->time_scale()==1024);}
 std::cout<<"Rest request identity, phase, generation and honest sleeping state PASS\n";
}
