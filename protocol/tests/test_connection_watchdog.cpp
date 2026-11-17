#include "../../luanti/src/cdda/connection_watchdog.h"
#include <stdexcept>
#include <iostream>
using namespace cdda_client;
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main() {
    using namespace std::chrono;
    const auto start=ConnectionWatchdog::Wall::time_point{};
    ConnectionWatchdog watchdog;CHECK(watchdog.retry_due(start));
    watchdog.begin_attempt(start);
    CHECK(!watchdog.retry_due(start+seconds(1)));CHECK(watchdog.retry_due(start+seconds(2)));
    // Repeated accepted resets/rejected full states never complete a world.
    for(int i=0;i<50;++i)CHECK(!watchdog.expired(start+milliseconds(100*i),false));
    CHECK(watchdog.expired(start+seconds(5),false));
    watchdog.failed(start+seconds(5));CHECK(!watchdog.retry_due(start+seconds(6)));
    CHECK(watchdog.retry_due(start+seconds(7)));
    watchdog.begin_attempt(start+seconds(7));CHECK(!watchdog.expired(start+seconds(8),true));
    // A later gap gets a fresh recovery budget. No gameplay dtime is involved.
    CHECK(!watchdog.expired(start+seconds(100),false));
    CHECK(!watchdog.expired(start+seconds(104),false));CHECK(watchdog.expired(start+seconds(105),false));
    CHECK(!watchdog.expired(start+seconds(106),true));
    std::cout<<"Bounded wall-time recovery, retry spacing and installed-world reset PASS\n";
}
