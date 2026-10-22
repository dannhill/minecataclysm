#include "cdda/mission_journal.h"
#include <stdexcept>
#include <iostream>
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main() {
 cdda_client::MissionJournal j;j.view=4;j.selected=0;
 j.entries.push_back({0,0,false,false,"Title ] unsafe","A native description <action name=evil>bad</action>","Native objective","Giver","Deadline","Approximate time","Known coordinates"});
 auto f=j.form();CHECK(f.find("mission_0;")!=std::string::npos);CHECK(f.find("Track this mission")!=std::string::npos);CHECK(f.find("Title \\] unsafe")!=std::string::npos);CHECK(f.find("\\<action")!=std::string::npos);
 j.entries[0].tracked=true;CHECK(j.form().find(";track;")==std::string::npos);
 j.tab=1;CHECK(j.form().find("No known missions in this category.")!=std::string::npos);
 j.waiting=true;CHECK(j.form().find("Waiting for the native journal...")!=std::string::npos);
 std::cout<<"Journal tabs, native mission zero, escaping and explicit-only tracking PASS\n";
}
