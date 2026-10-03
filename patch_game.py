import re

with open("luanti/src/client/game.cpp", "r") as f:
    text = f.read()

# Add include
text = text.replace('#include "camera.h"', '#include "camera.h"\n#include "cdda/cdda_bridge.h"')

# Add initialization
init_str = """
		client = new Client(start_data.name.c_str(),
"""

init_replace = """
		client = new Client(start_data.name.c_str(),
"""

# Actually let's find a safe spot after client creation.
after_client_str = """
		client->connect(start_data.address,
				start_data.port,
				start_data.is_simple_singleplayer);
"""

after_client_replace = """
		client->connect(start_data.address,
				start_data.port,
				start_data.is_simple_singleplayer);

		// [CDDA-Mineclonia] Initialize presentation bridge
		cdda_client::CddaBridge::getInstance().initialize(client, "/tmp/cwm_bench_ipc.sock");
"""
text = text.replace(after_client_str, after_client_replace)

# Add update hook
update_str = """
		client->getEnv().updateFrameTime(m_is_paused);
"""

update_replace = """
		client->getEnv().updateFrameTime(m_is_paused);

		// [CDDA-Mineclonia] Update Bridge & Entities
		cdda_client::CddaBridge::getInstance().update(dtime);
"""
text = text.replace(update_str, update_replace)

# Add overlay render hook (say, inside F3 key handling or just every frame)
# We can just put it in updateFrame too, or draw function.
# Wait, renderDebugOverlay uses IGUIStaticText so it just needs to be called to create/update the text!
# Let's just put it in updateFrame.

update_ui_str = """
		client->step(dtime);
"""

update_ui_replace = """
		client->step(dtime);
		
		// [CDDA-Mineclonia] Update F3 Debug Overlay
		cdda_client::CddaBridge::getInstance().renderDebugOverlay(m_game_ui->getGUIEnvironment());
"""
text = text.replace(update_ui_str, update_ui_replace)

# Add shutdown
shutdown_str = """
	delete client;
"""

shutdown_replace = """
	// [CDDA-Mineclonia] Shutdown Bridge
	cdda_client::CddaBridge::getInstance().shutdown();
	delete client;
"""
text = text.replace(shutdown_str, shutdown_replace)

with open("luanti/src/client/game.cpp", "w") as f:
    f.write(text)

