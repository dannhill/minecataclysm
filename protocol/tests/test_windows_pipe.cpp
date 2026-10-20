#include "cwm/ipc_transport.hpp"
#include <iostream>
#include <stdexcept>
using namespace cdda::cwm;
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main(){
 try{
  const std::string name="\\\\.\\pipe\\Minecataclysm-test-"+std::to_string(GetCurrentProcessId())+"-"+std::to_string(GetTickCount64());
  IpcLimits limits;limits.read_bytes_per_pump=1024;limits.write_bytes_per_pump=1024;limits.frames_per_pump=2;
  IpcServer server(name,limits);CHECK(server.start());auto client=IpcClient::connect_unix(name,0);CHECK(client);
  CHECK(server.poll_accept());CHECK(!IpcClient::connect_unix(name,0));
  std::vector<uint8_t> payload(256*1024);for(size_t i=0;i<payload.size();++i)payload[i]=uint8_t(i);
  CHECK(client->send_message(payload.data(),payload.size()));
  std::vector<std::vector<uint8_t>> frames,unused;
  for(int i=0;i<10000 && frames.empty();++i){CHECK(client->poll_and_receive(unused));CHECK(server.client()->poll_and_receive(frames));CHECK(server.client()->last_work().read_bytes<=1024);if(i%100==0)Sleep(1);}
  CHECK(frames.size()==1 && frames[0]==payload);std::cout<<"PASS fragmented bounded delivery\n";
  for(int i=0;i<9;++i){payload.resize(17);payload[0]=uint8_t(i);CHECK(server.client()->send_message(payload.data(),payload.size()));}
  frames.clear();for(int i=0;i<10000 && frames.size()<9;++i){CHECK(server.client()->poll_and_receive(unused));CHECK(client->poll_and_receive(frames));CHECK(server.client()->last_work().written_bytes<=1024);if(i%100==0)Sleep(1);}
  CHECK(frames.size()==9);for(size_t i=0;i<9;++i)CHECK(frames[i][0]==i);std::cout<<"PASS ordered complete frames\n";
  client->close();bool eof=false;for(int i=0;i<1000&&!eof;++i){eof=!server.client()->poll_and_receive(unused);if(i%100==0)Sleep(1);}CHECK(eof);std::cout<<"PASS peer EOF and pending read cancellation\n";
  server.poll_accept();auto second=IpcClient::connect_unix(name,0);CHECK(second);CHECK(server.poll_accept());std::cout<<"PASS same endpoint reconnect, no live-peer replacement\n";
  second->close();server.stop();CHECK(server.start());
  HANDLE raw=CreateFileW(pipe_wide(name).c_str(),GENERIC_READ|GENERIC_WRITE,0,nullptr,OPEN_EXISTING,0,nullptr);CHECK(raw!=INVALID_HANDLE_VALUE);CHECK(server.poll_accept());
  const uint8_t truncated[]{0,0,0,100,1,2,3};DWORD written=0;CHECK(WriteFile(raw,truncated,sizeof(truncated),&written,nullptr));CloseHandle(raw);
  eof=false;for(int i=0;i<1000&&!eof;++i){eof=!server.client()->poll_and_receive(unused);if(i%100==0)Sleep(1);}
  CHECK(eof && server.client()->close_reason()==IpcCloseReason::TruncatedFrame);std::cout<<"PASS truncated frame rejection\n";
  server.stop();CHECK(server.start());raw=CreateFileW(pipe_wide(name).c_str(),GENERIC_READ|GENERIC_WRITE,0,nullptr,OPEN_EXISTING,0,nullptr);CHECK(raw!=INVALID_HANDLE_VALUE);CHECK(server.poll_accept());
  const uint8_t invalid[]{0,0,0,0};CHECK(WriteFile(raw,invalid,sizeof(invalid),&written,nullptr));CloseHandle(raw);eof=false;
  for(int i=0;i<1000&&!eof;++i){eof=!server.client()->poll_and_receive(unused);if(i%100==0)Sleep(1);}
  CHECK(eof && server.client()->close_reason()==IpcCloseReason::InvalidFrame);std::cout<<"PASS malformed frame rejection\n";
  server.stop();IpcLimits small;small.max_output_bytes=32;IpcServer bounded(name,small);CHECK(bounded.start());auto peer=IpcClient::connect_unix(name,0);CHECK(peer);CHECK(bounded.poll_accept());
  std::vector<uint8_t> message(20,42);CHECK(bounded.client()->send_message(message.data(),message.size()));CHECK(!bounded.client()->send_message(message.data(),message.size()));CHECK(bounded.client()->close_reason()==IpcCloseReason::OutputLimit);std::cout<<"PASS bounded queue disconnect instead of delta loss\n";
  std::cout<<"7 Windows named-pipe checks passed\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}
}
