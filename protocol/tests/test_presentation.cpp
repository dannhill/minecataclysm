#include "cwm/cwm_session.hpp"
#include <stdexcept>
#include <iostream>
using namespace CDDA::CWM;
using namespace cdda::cwm;
#define CHECK(x) do {if(!(x)) throw std::runtime_error(#x);} while(false)
int main() {
    for (int bad=0;bad<10;++bad) {
        flatbuffers::FlatBufferBuilder f;
        const auto cue=CreatePresentationEventDirect(f,bad==1?0:1,bad==2?static_cast<PresentationKind>(99):PresentationKind::SOUND,
            bad==3?42:0,bad==4?std::string(4097,'x').c_str():"East: bang", "gunfire",bad==5?201:25);
        std::vector<flatbuffers::Offset<PresentationEvent>> cues{cue};
        if (bad==6) cues.resize(129,cue); if (bad==7) cues.push_back(cue);
        if (bad==8) cues[0]=CreatePresentationEventDirect(f,1,PresentationKind::HURT,0,"","",0);
        const auto vector=f.CreateVector(cues);
        WorldSnapshotBuilder w(f); w.add_presentation_events(vector); w.add_full(bad==9);
        const auto world=w.Finish(); f.Finish(world);
        const auto* state=flatbuffers::GetRoot<WorldSnapshot>(f.GetBufferPointer());
        CHECK(valid_presentation(state)==(bad==0));
    }
    std::cout << "10 presentation bounds/privacy/replay checks passed\n";
}
