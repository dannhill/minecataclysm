-- CDDA Nodes: Visual node registrations for 3D presentation
-- Pure presentation definitions - zero survival or crafting mechanics

minetest.register_node("cdda_nodes:dirt", {
    description = "Dirt",
    tiles = {"default_dirt.png"},
    groups = {crumbly = 3},
    walkable = true,
})

minetest.register_node("cdda_nodes:grass_block", {
    description = "Grass Block",
    tiles = {"default_grass.png", "default_dirt.png", "default_dirt.png"},
    groups = {crumbly = 3},
    walkable = true,
})

minetest.register_node("cdda_nodes:brick_wall", {
    description = "Brick Wall",
    tiles = {"default_brick.png"},
    groups = {cracky = 2},
    walkable = true,
})

minetest.register_node("cdda_nodes:wood_planks", {
    description = "Wood Planks",
    tiles = {"default_wood.png"},
    groups = {choppy = 2},
    walkable = true,
})

minetest.register_node("cdda_nodes:door_wood_closed", {
    description = "Wooden Door (Closed)",
    tiles = {"door_wood.png"},
    drawtype = "nodebox",
    paramtype = "light",
    paramtype2 = "facedir",
    node_box = {
        type = "fixed",
        fixed = {-0.5, -0.5, -0.1, 0.5, 1.5, 0.1},
    },
    walkable = true,
})

minetest.register_node("cdda_nodes:door_wood_open", {
    description = "Wooden Door (Open)",
    tiles = {"door_wood.png"},
    drawtype = "nodebox",
    paramtype = "light",
    paramtype2 = "facedir",
    node_box = {
        type = "fixed",
        fixed = {-0.5, -0.5, -0.5, -0.3, 1.5, 0.5},
    },
    walkable = false,
})

minetest.register_node("cdda_nodes:glass", {
    description = "Glass Window",
    drawtype = "glasslike",
    tiles = {"default_glass.png"},
    paramtype = "light",
    sunlight_propagates = true,
    walkable = true,
})

minetest.register_node("cdda_nodes:stone", {
    description = "Stone Pavement",
    tiles = {"default_stone.png"},
    groups = {cracky = 3},
    walkable = true,
})

minetest.register_node("cdda_nodes:furniture_wood", {
    description = "Wooden Furniture",
    tiles = {"default_wood.png"},
    drawtype = "nodebox",
    node_box = {
        type = "fixed",
        fixed = {-0.4, -0.5, -0.4, 0.4, 0.4, 0.4},
    },
    walkable = true,
})

minetest.log("action", "[CDDA] Pruned visual voxel nodes registered successfully.")

-- CDDA is the only world authority: force an empty Luanti mapgen.
minetest.set_mapgen_setting("mg_name", "singlenode", true)
minetest.register_alias("mapgen_stone", "air")
minetest.register_alias("mapgen_water_source", "air")
minetest.register_alias("mapgen_river_water_source", "air")

-- Luanti physics has no authority: CDDA moves the player.
minetest.register_on_joinplayer(function(player)
    player:set_physics_override({speed = 0, jump = 0, gravity = 0})
end)

-- Keep Luanti's sky at daytime; real lighting comes from CDDA per tile.
minetest.register_on_mods_loaded(function()
    minetest.settings:set("time_speed", "0")
end)
minetest.after(0, function() minetest.set_timeofday(0.5) end)
