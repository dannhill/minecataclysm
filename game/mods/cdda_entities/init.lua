-- CDDA Entities: Visual entity registrations for 3D presentation
-- Pure visual representation: no Luanti AI, mob spawning, or hunger

minetest.register_entity("cdda_entities:player", {
    initial_properties = {
        visual = "mesh",
        mesh = "character.b3d",
        textures = {"character.png"},
        visual_size = {x = 1, y = 1},
        collisionbox = {-0.3, 0.0, -0.3, 0.3, 1.8, 0.3},
        physical = false, -- CDDA is physical authority!
        pointable = false,
    },
    on_activate = function(self)
        self.object:set_armor_groups({immortal = 1})
    end,
})

minetest.register_entity("cdda_entities:zombie", {
    initial_properties = {
        visual = "mesh",
        mesh = "zombie.b3d",
        textures = {"zombie.png"},
        visual_size = {x = 1, y = 1},
        collisionbox = {-0.3, 0.0, -0.3, 0.3, 1.8, 0.3},
        physical = false, -- CDDA is physical authority!
        pointable = true,
    },
    on_activate = function(self)
        self.object:set_armor_groups({immortal = 1})
    end,
})

minetest.log("action", "[CDDA] Visual entity definitions registered successfully.")
