// Tests empty storage, rebasing and clearing on the actual renderer cache type.
#include "cdda/ground_item_projection.h"
#include <stdexcept>
#include <iostream>
#define CHECK(x) do { if(!(x))throw std::runtime_error(#x); }while(false)
int main() {
    using namespace cdda_client;
    GroundItemProjection p;const v3s16 retained(61,0,-60),exiting(5,0,-60),lower(61,-3,-60);
    p.apply(retained,{},true,"locker");p.apply(exiting,{},true,"crate");p.apply(lower,{},true,"cabinet");
    CHECK(p.size()==0);CHECK(p.storage(retained)&&*p.storage(retained)=="locker");
    p.pruneWindow(v3s32(1012,2000,-1),v3s32(1000,2000,-1));
    CHECK(p.storage(retained));CHECK(p.storage(lower));CHECK(!p.storage(exiting));
    p.apply(retained,{},false);CHECK(!p.storage(retained));
    p.apply(retained,{{0,"rock","rock",0,false}},true,"locker");CHECK(p.get(retained)&&p.storage(retained));
    p.apply(retained,{},true,"locker");CHECK(!p.get(retained)&&p.storage(retained));
    p.clear();CHECK(!p.storage(retained)&&!p.storage(lower)&&p.size()==0);
    std::cout<<"Empty storage, item removal, negative-Z rebase and resync clear PASS\n";
}
