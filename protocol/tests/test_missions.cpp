#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
using namespace CDDA::CWM;using namespace cdda::cwm;
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main() {
 for(int bad=0;bad<13;++bad) {
  MessageBuilder wire(1,1);auto& f=wire.builder();Coord3i target(4,5,-1);
  auto row=CreateMissionEntry(f,bad==1?-1:0,bad==2?MissionState(3):bad==3?MissionState::FAILED:MissionState::ACTIVE,true,
   f.CreateString(bad==4?"":"Native title"),f.CreateString(bad==5?std::string(16385,'d'):"Description"),f.CreateString("Objective"),f.CreateString("Known giver"),
   f.CreateString(bad==6?"":"Deadline"),f.CreateString("Approximately two hours"),bad==7?nullptr:&target,f.CreateString("Known target"));
  std::vector<flatbuffers::Offset<MissionEntry>> rows{row};if(bad==8)rows.push_back(row);
  auto v=CreateMissionView(f,bad==9?0:1,bad==10?0:4,bad==11?-1:bad==12?2:0,f.CreateVector(rows),false,f.CreateString(""));
  auto data=wire.finish_message(Payload::MissionView,v.Union());CHECK(MessageVerifier::verify(data.data(),data.size()));CHECK(valid_missions(GetCwmMessage(data.data())->payload_as_MissionView())==(bad==0));
 }
 MessageBuilder wire(1,1);auto bytes=wire.build_mission_query(8);CHECK(GetCwmMessage(bytes.data())->payload_as_MissionQueryRequest()->query_id()==8);
 bytes=wire.build_mission_track(9,4,0,-1);auto* r=GetCwmMessage(bytes.data())->payload_as_MissionTrackRequest();CHECK(r->command_id()==9 && r->mission_id()==0 && r->expected_tracked_id()==-1);
 std::cout<<"Mission ID zero, bounded histories, tracking identity and native target metadata PASS\n";
}
