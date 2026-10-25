#include "cwm/cwm_clock.hpp"
#include <iostream>
#include <limits>
#include <stdexcept>
using cdda::cwm::SimulationClock;
static int checks=0;
#define CHECK(x) do { ++checks; if(!(x)) throw std::runtime_error(#x); } while(false)
int main() {
    using namespace std::chrono;
    const auto epoch=SimulationClock::Wall::time_point{};
    auto t=[&](double seconds){return epoch+duration_cast<SimulationClock::Wall::duration>(duration<double>(seconds));};
    SimulationClock c; c.sample(t(0),true);
    for(int i=1;i<=4;++i)c.sample(t(i*.25),true);
    CHECK(c.tick_due()); CHECK(std::abs(c.elapsed()-1.)<1e-8);
    c.complete_tick(); CHECK(!c.tick_due());
    c.sample(t(1),false); c.sample(t(30),false); c.sample(t(31),true);
    CHECK(std::abs(c.elapsed()-1.)<1e-8); CHECK(!c.tick_due());
    c.sample(t(31.25),true); CHECK(std::abs(c.elapsed()-1.25)<1e-8);
    CHECK(c.set_scale(2)); c.sample(t(31.5),true); CHECK(std::abs(c.elapsed()-1.75)<1e-8);
    c.sample(t(31.75),true); CHECK(c.tick_due()); c.complete_tick(); CHECK(!c.tick_due());
    CHECK(!c.set_scale(0)); CHECK(!c.set_scale(5)); CHECK(!c.set_scale(std::numeric_limits<double>::quiet_NaN()));
    CHECK(!c.set_scale(std::numeric_limits<double>::infinity())); CHECK(c.scale()==2);
    c.sample(t(300),true); CHECK(std::abs(c.elapsed()-2.75)<1e-8); CHECK(!c.tick_due());
    const auto before=c.elapsed(); c.sample(t(299),true); CHECK(c.elapsed()==before);
    SimulationClock a; a.sample(t(0),true);
    CHECK(std::abs(a.charge_action(100,125)-.8)<1e-8); CHECK(!a.action_due()); CHECK(std::abs(a.remaining_work()-.8)<1e-8);
    for(int i=1;i<=3;++i)a.sample(t(i*.25),true);
    CHECK(!a.action_due()); CHECK(std::abs(a.remaining_work()-.05)<1e-8); a.sample(t(.8),true); CHECK(a.action_due()); CHECK(a.remaining_work()==0);
    a.charge_action(100,125); a.sample(t(1),true); CHECK(!a.action_due()); CHECK(a.tick_due());
    a.complete_tick(); CHECK(!a.tick_due());
    a.sample(t(1),false); a.sample(t(60),true); CHECK(!a.action_due());
    for(int i=1;i<=3;++i)a.sample(t(60+i*.2),true);
    CHECK(a.action_due()); CHECK(!a.tick_due());
    // Native actors consume credit before publishing completion. Their exact
    // debit remains payable after interruption, including sub-turn final work.
    SimulationClock work; work.sample(t(0),true);
    CHECK(work.charge_work(0,100)==0); CHECK(work.action_due());
    CHECK(work.charge_work(40,100)==.4); CHECK(!work.action_due());
    work.sample(t(.25),true); CHECK(!work.action_due());
    work.sample(t(.4),true); CHECK(work.action_due());
    work.charge_work(250,100); CHECK(!work.action_due());
    work.sample(t(.4),false); work.sample(t(90),false); work.sample(t(90.1),true);
    CHECK(!work.action_due());
    for(int i=1;i<=9;++i) work.sample(t(90.1+i*.25),true);
    CHECK(!work.action_due()); work.sample(t(92.6),true); CHECK(work.action_due());
    CHECK(work.charge_work(-100,100)==0); CHECK(work.action_due());
    SimulationClock rest;CHECK(rest.set_scale(2));rest.set_rest_context(true);
    CHECK(rest.rest_context());CHECK(rest.scale()==1024);
    rest.sample(t(0),true);rest.sample(t(.25),true);
    CHECK(std::abs(rest.elapsed()-256)<1e-8);CHECK(rest.tick_due());
    int ticks=0;while(rest.tick_due() && ticks<100){rest.complete_tick();++ticks;}
    CHECK(ticks>=32 && ticks<=34);
    CHECK(rest.set_scale(4096,true));CHECK(rest.scale()==4096);CHECK(rest.set_scale(1024,true));CHECK(!rest.set_scale(4,false));CHECK(rest.scale()==1024);
    CHECK(!rest.set_scale(4097,true));CHECK(rest.set_scale(1,true));
    CHECK(rest.scale()==1);const auto frozen=rest.elapsed();
    rest.sample(t(.25),false);rest.sample(t(900),false);CHECK(rest.elapsed()==frozen);
    rest.sample(t(901),true);rest.sample(t(901.25),true);CHECK(std::abs(rest.elapsed()-frozen-.25)<1e-8);
    rest.set_rest_context(false);CHECK(!rest.rest_context());CHECK(rest.scale()==2);
    CHECK(!rest.set_scale(4,true));CHECK(!rest.set_scale(256,false));CHECK(rest.scale()==2);
    rest.set_rest_context(true);CHECK(rest.scale()==1); // The last rest choice is an alternative, not a factor.
    CHECK(SimulationClock::next_scale(4,false)==.5);CHECK(SimulationClock::next_scale(4,true)==64);
    CHECK(SimulationClock::next_scale(256,true)==1024);CHECK(SimulationClock::next_scale(1024,true)==4096);CHECK(SimulationClock::next_scale(4096,true)==1);
    // Changing context never clears already charged work.
    SimulationClock debt;debt.sample(t(0),true);debt.charge_work(500,100);
    const auto owed=debt.remaining_work();debt.set_rest_context(true);debt.set_rest_context(false);CHECK(debt.remaining_work()==owed);
    std::cout<<"Clock invariants PASS ("<<checks<<" checks)\n";
}
