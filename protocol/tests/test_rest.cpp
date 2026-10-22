#include "cwm/cwm_session.hpp"
#include <iostream>
#include <stdexcept>
using namespace CDDA::CWM;using namespace cdda::cwm;
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main(){
 MessageBuilder wire(1,1);auto bytes=wire.build_rest_request(8,9);auto* r=GetCwmMessage(bytes.data())->payload_as_RestRequest();CHECK(r && r->command_id()==8 && r->expected_token()==9);
 for(int bad=0;bad<6;++bad){MessageBuilder b(1,1);auto& f=b.builder();auto state=CreateRestState(f,bad==1?0:1,bad==2?RestPhase(3):RestPhase::SLEEPING,bad==3,false,bad==4?101:bad==5?0:-1);Coord3i origin(0,0,0);WorldSnapshotBuilder wb(f);wb.add_world_revision(1);wb.add_origin(&origin);wb.add_rest(state);auto data=b.finish_message(Payload::WorldSnapshot,wb.Finish().Union());CHECK(MessageVerifier::verify(data.data(),data.size()));auto rest=GetCwmMessage(data.data())->payload_as_WorldSnapshot()->rest();CHECK(valid_rest(rest)==(bad==0));}
 std::cout<<"Rest request identity, phase, generation and honest sleeping state PASS\n";
}
