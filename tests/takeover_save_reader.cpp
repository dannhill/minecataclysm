// Test-only canonical fixture and semantic reader. Linked to pristine upstream core.
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include "avatar.h"
#include "cached_options.h"
#include "calendar.h"
#include "color.h"
#include "debug.h"
#include "filesystem.h"
#include "game.h"
#include "item.h"
#include "json.h"
#include "loading_ui.h"
#include "map.h"
#include "monster.h"
#include "npc.h"
#include "options.h"
#include "overmap.h"
#include "overmapbuffer.h"
#include "path_info.h"
#include "rng.h"
#include "units.h"
#include "vehicle.h"
#include "weather.h"
#include "worldfactory.h"

int main(int argc, const char *argv[]) {
    std::string userdir, datadir, output, character, world_name = "audit_fixture";
    bool create = false;
    bool create_ledge = false;
    bool create_exploration = false;
    bool create_vertical = false;
    bool create_actors = false;
    bool resave = false;
    for (int i = 1; i < argc; ++i) {
        std::string arg(argv[i]);
        if (arg == "--create") create = true;
        else if (arg == "--create-ledge") { create = true; create_ledge = true; }
        else if (arg == "--create-exploration") { create = true; create_exploration = true; }
        else if (arg == "--create-vertical") { create = true; create_vertical = true; }
        else if (arg == "--create-actors") { create = true; create_vertical = true; create_actors = true; }
        else if (arg == "--resave") resave = true;
        else if (i + 1 < argc && arg == "--userdir") userdir = argv[++i];
        else if (i + 1 < argc && arg == "--datadir") datadir = argv[++i];
        else if (i + 1 < argc && arg == "--output") output = argv[++i];
        else if (i + 1 < argc && arg == "--world") world_name = argv[++i];
        else if (i + 1 < argc && arg == "--expect-character") character = argv[++i];
        else { std::cerr << "Unknown argument: " << arg << '\n'; return 2; }
    }
    if (userdir.empty() || datadir.empty() || output.empty()) return 2;
    if (datadir.back() != '/') datadir += '/';
    test_mode = true;
    rng_set_engine_seed(42);
    assure_dir_exist(userdir);
    PATH_INFO::init_base_path("");
    PATH_INFO::init_user_dir(userdir);
    PATH_INFO::set_standard_filenames();
    PATH_INFO::set_datadir(datadir);
    assure_dir_exist(PATH_INFO::config_dir());
    assure_dir_exist(PATH_INFO::savedir());
    assure_dir_exist(PATH_INFO::templatedir());
    setupDebug(DebugOutput::file);
    get_options().init();
    get_options().load();
    init_colors();
    g = std::make_unique<game>();
    g->new_game = true;
    g->load_static_data();
    world_generator->set_active_world(nullptr);
    world_generator->init();

    if (create) {
        auto *world = world_generator->make_new_world(world_name, {mod_id("dda")});
        if (!world) return 3;
        world_generator->set_active_world(world);
        loading_ui ui(false);
        g->load_core_data(ui);
        g->load_world_modfiles(ui);
        auto &u = get_avatar();
        u = avatar();
        u.create(character_type::NOW);
        u.name = "Audit Survivor";
        u.setID(g->assign_npc_id(), false);
        get_map() = map();
        overmap_special_batch specials(point_abs_om{});
        overmap_buffer.create_custom_overmap(point_abs_om{}, specials);
        auto &m = get_map();
        m.load(tripoint_abs_sm(m.get_abs_sub()), false);
        for (int y = 48; y <= 76; ++y) {
            for (int x = 48; x <= 76; ++x) {
                m.ter_set(tripoint(x,y,0), ter_str_id("t_floor"));
                m.furn_set(tripoint(x,y,0), furn_str_id("f_null"));
                // Canonical load fills roofs above supported floors. Make the
                // fixture internally consistent before taking its baseline.
                m.ter_set(tripoint(x,y,1), ter_str_id("t_wood_treated_roof"));
                m.furn_set(tripoint(x,y,1), furn_str_id("f_null"));
            }
        }
        m.ter_set(tripoint(61,60,0), ter_str_id("t_door_c"));
        if (create_ledge) {
            // Native add_roofs() fills plain t_open_air above floor on load.
            // This native ledge variant explicitly preserves an opening.
            m.ter_set(tripoint(60,59,0), ter_str_id("t_open_air_rooved"));
            m.ter_set(tripoint(60,59,-1), ter_str_id("t_floor"));
        }
        m.furn_set(tripoint(60,62,0), furn_str_id("f_chair"));
        u.move_to(tripoint_abs_ms(tripoint(60,60,0)));
        calendar::turn = calendar::turn_zero + 36_hours;
        u.i_add(item(itype_id("rock"), calendar::turn));
        if (create_vertical) {
            // Canonical multi-Z fixture, built by the pristine pinned core.
            // No production exporter, projection or CWM server creates it.
            for (int z = -2; z <= 2; ++z) {
                for (int y = 48; y <= 76; ++y) {
                    for (int x = 48; x <= 76; ++x) {
                        m.ter_set(tripoint(x,y,z), ter_str_id("t_floor"));
                        m.furn_set(tripoint(x,y,z), furn_str_id("f_null"));
                    }
                }
            }
            m.ter_set(tripoint(60,59,0), ter_str_id("t_stairs_up"));
            m.ter_set(tripoint(60,59,1), ter_str_id("t_stairs_down"));
            m.ter_set(tripoint(61,59,1), ter_str_id("t_door_c"));
            m.ter_set(tripoint(60,61,0), ter_str_id("t_stairs_down"));
            m.ter_set(tripoint(60,61,-1), ter_str_id("t_stairs_up"));
            m.ter_set(tripoint(61,60,0), ter_str_id("t_ladder_up"));
            m.ter_set(tripoint(61,60,1), ter_str_id("t_ladder_up_down"));
            m.ter_set(tripoint(61,60,2), ter_str_id("t_ladder_down"));
            m.ter_set(tripoint(68,59,0), ter_str_id("t_stairs_up"));
            m.ter_set(tripoint(70,59,1), ter_str_id("t_stairs_down"));
            m.ter_set(tripoint(62,60,0), ter_str_id("t_water_dp"));
            m.ter_set(tripoint(62,60,-1), ter_str_id("t_water_cube"));
            m.ter_set(tripoint(62,60,-2), ter_str_id("t_water_cube"));
            u.remove_weapon();
            u.set_skill_level(skill_id("swimming"),10);
        }
        if (create_actors) {
            // Long canonical corridor for genuine bubble departure/return.
            // Save the initial map before editing overlapping native tinymaps.
            m.save();
            for (int sx = 0; sx <= 14; sx += 2) {
                tinymap section;
                section.load(tripoint_abs_sm(sx,4,0), false);
                for (int y = 0; y < 24; ++y) for (int x = 0; x < 24; ++x) {
                    section.ter_set(tripoint(x,y,0), ter_str_id("t_floor"));
                    section.furn_set(tripoint(x,y,0), furn_str_id("f_null"));
                    section.ter_set(tripoint(x,y,1), ter_str_id("t_wood_treated_roof"));
                    section.furn_set(tripoint(x,y,1), furn_str_id("f_null"));
                }
                section.save();
            }
            m.load(tripoint_abs_sm(0,0,0), false);
            m.ter_set(tripoint(60,59,0), ter_str_id("t_stairs_up"));
            m.ter_set(tripoint(60,59,1), ter_str_id("t_stairs_down"));
            calendar::turn = calendar::turn_zero + 1_hours;
            for (const auto& entry : {std::pair<const char*,tripoint>{"mon_zombie",tripoint(63,58,0)},
                                     {"mon_dog",tripoint(65,58,0)}}) {
                auto* actor = g->place_critter_at(mtype_id(entry.first),entry.second);
                if (!actor) return 10;
                actor->friendly = -1;
                actor->add_effect(efftype_id("stunned"), 10_days, true);
            }
            auto guy = make_shared_fast<npc>();
            guy->normalize();
            guy->randomize();
            guy->name = "Lifecycle NPC";
            guy->set_fac(faction_id("no_faction"));
            guy->set_attitude(NPCATT_NULL);
            guy->spawn_at_precise(tripoint_abs_ms(m.getabs(tripoint(60,64,0))));
            guy->add_effect(efftype_id("stunned"), 10_days, true);
            overmap_buffer.insert_npc(guy);
            g->load_npcs();
        }
        if (create_exploration) {
            m.ter_set(tripoint(60,59,0), ter_str_id("t_water_dp"));
            m.ter_set(tripoint(60,61,0), ter_str_id("t_water_sh"));
            m.ter_set(tripoint(59,60,0), ter_str_id("t_window_no_curtains"));
            m.ter_set(tripoint(59,59,0), ter_str_id("t_wall"));
            m.ter_set(tripoint(59,61,0), ter_str_id("t_wall"));
            u.remove_weapon();
            item matches(itype_id("matches"), calendar::turn);
            if (!u.wield(matches)) return 9;
            u.set_skill_level(skill_id("swimming"),10);
            get_weather().update_weather();
            if (!g->save()) return 5;
        } else if (!create_vertical) {
        g->place_critter_at(mtype_id("mon_zombie"), tripoint(65,65,0));
        auto guy = make_shared_fast<npc>();
        guy->normalize();
        guy->randomize();
        guy->set_fac(faction_id("no_faction"));
        guy->spawn_at_precise(tripoint_abs_ms(m.getabs(tripoint(67,67,0))));
        overmap_buffer.insert_npc(guy);
        g->load_npcs();
        if (!m.add_vehicle(vproto_id("bicycle"),tripoint(60,66,0),0_degrees,0,0)) return 4;
        get_weather().update_weather();
        if (!g->save()) return 5;
        }
        if (create_vertical) {
            get_weather().update_weather();
            if (!g->save()) return 5;
        }
    } else if (!g->load(world_name)) {
        std::cerr << "Canonical game::load(world) failed\n";
        return 6;
    }
    if (!create && !character.empty() && get_avatar().name != character) return 8;
    // Explicit native load/save control for canonical on_load catch-up effects.
    // Ordinary reader invocations remain read-only.
    if (resave && !g->save()) return 9;

    std::ofstream file(output);
    JsonOut json(file, true);
    auto &u = get_avatar();
    auto &m = get_map();
    tripoint center = m.getabs(u.pos());
    json.start_object();
    json.member("time", to_turn<int>(calendar::turn));
    json.member("player_abs", std::vector<int>{center.x,center.y,center.z});
    json.member("player"); u.serialize(json);
    json.member("terrain_and_furniture"); json.start_array();
    for (int z = center.z-1; z <= center.z+1; ++z) {
        for (int y = center.y-12; y <= center.y+12; ++y) {
            for (int x = center.x-12; x <= center.x+12; ++x) {
                tripoint absolute(x,y,z), local=m.getlocal(absolute);
                json.start_array();
                json.write(x); json.write(y); json.write(z);
                json.write(m.ter(local).id().str());
                json.write(m.furn(local).id().str());
                json.end_array();
            }
        }
    }
    json.end_array();
    json.member("monsters"); json.start_array();
    for (monster &who : g->all_monsters()) who.serialize(json);
    json.end_array();
    json.member("npcs"); json.start_array();
    for (npc &who : g->all_npcs()) who.serialize(json);
    json.end_array();
    json.member("vehicles"); json.start_array();
    for (const wrapped_vehicle &wv : m.get_vehicles()) if (wv.v) wv.v->serialize(json);
    json.end_array();
    json.end_object();
    file << '\n';
    // Preserve the complete canonical player/world projection as additional evidence.
    std::ofstream canonical(output + ".canonical");
    g->serialize(canonical);
    std::cout << "Canonical " << (create ? "fixture created" : "world loaded") << "; semantic projection: " << output << '\n';
    return file.good() && canonical.good() ? 0 : 7;
}
