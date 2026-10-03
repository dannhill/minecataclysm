import re

with open("luanti/src/client/game.cpp", "r") as f:
    text = f.read()

# Let's find where key presses are checked for movement, or just do it in updatePlayerControl
search_input = """
	client->setPlayerControl(control);
"""

replace_input = """
	client->setPlayerControl(control);

	// [CDDA-Mineclonia] Send Movement Commands
	static float move_cooldown = 0.0f;
	if (move_cooldown > 0.0f) move_cooldown -= 1.0f / 60.0f; // Approx dtime

	if (move_cooldown <= 0.0f) {
		int cdda_dir = 8; // NONE
		if (control.up) cdda_dir = 0; // NORTH
		else if (control.down) cdda_dir = 2; // SOUTH
		else if (control.left) cdda_dir = 3; // WEST
		else if (control.right) cdda_dir = 1; // EAST

		if (cdda_dir != 8) {
			cdda_client::CddaBridge::getInstance().handleMoveInput(cdda_dir);
			move_cooldown = 0.2f; // CDDA is turn based, limit to 5 steps/sec
		}
	}
"""

text = text.replace(search_input, replace_input)

with open("luanti/src/client/game.cpp", "w") as f:
    f.write(text)

