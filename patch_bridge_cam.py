import re

with open("luanti/src/cdda/cdda_bridge.cpp", "r") as f:
    text = f.read()

update_search = """
        // Interpolate visual entities
        for (auto& [id, ent] : entities_) {
            v3f diff = ent.target_pos - ent.current_pos;
            ent.current_pos += diff * std::min(1.0f, dtime * 12.0f);
        }
"""

update_replace = """
        // Interpolate visual entities
        for (auto& [id, ent] : entities_) {
            v3f diff = ent.target_pos - ent.current_pos;
            ent.current_pos += diff * std::min(1.0f, dtime * 12.0f);
            
            // Sync Luanti camera to CDDA player (id == 1)
            if (id == 1 && client_) {
                auto* local_player = client_->getEnv().getLocalPlayer();
                if (local_player) {
                    // BS = 10.0f. Player camera typically is +1.5 blocks up, but CDDA handles Z
                    local_player->setPosition(ent.current_pos * 10.0f);
                }
            }
        }
"""

text = text.replace(update_search, update_replace)

# Also ensure localplayer header is included
includes = """
#include "client/client.h"
#include "client/clientmap.h"
"""

includes_replace = """
#include "client/client.h"
#include "client/clientmap.h"
#include "client/clientenvironment.h"
#include "client/localplayer.h"
"""
text = text.replace(includes, includes_replace)

with open("luanti/src/cdda/cdda_bridge.cpp", "w") as f:
    f.write(text)

