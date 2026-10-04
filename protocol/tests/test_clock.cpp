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
    CHECK(std::abs(a.charge_action(100,125)-.8)<1e-8); CHECK(!a.action_due());
    for(int i=1;i<=3;++i)a.sample(t(i*.25),true);
    CHECK(!a.action_due()); a.sample(t(.8),true); CHECK(a.action_due());
    a.charge_action(100,125); a.sample(t(1),true); CHECK(!a.action_due()); CHECK(a.tick_due());
    a.complete_tick(); CHECK(!a.tick_due());
    a.sample(t(1),false); a.sample(t(60),true); CHECK(!a.action_due());
    for(int i=1;i<=3;++i)a.sample(t(60+i*.2),true);
    CHECK(a.action_due()); CHECK(!a.tick_due());
    std::cout<<"Clock invariants PASS ("<<checks<<" checks)\n";
}
