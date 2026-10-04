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

-- Two cell-sized halves share one door image. Geometry never extends into
-- a neighboring cell, so mesh visibility is the same from inside and outside.
local function register_door(name, is_open, top)
    minetest.register_node("cdda_nodes:" .. name, {
        description = is_open and "Wooden Door (Open)" or "Wooden Door (Closed)",
        tiles = {"door_wood.png^[sheet:1x2:0," .. (top and "0" or "1")},
        drawtype = "nodebox",
        paramtype = "light",
        paramtype2 = "facedir",
        node_box = {
            type = "fixed",
            fixed = is_open and {-0.5, -0.5, -0.5, -0.3, 0.5, 0.5}
                or {-0.5, -0.5, -0.1, 0.5, 0.5, 0.1},
        },
        walkable = not is_open,
    })
end
register_door("door_wood_closed", false, false)
register_door("door_wood_closed_top", false, true)
register_door("door_wood_open", true, false)
register_door("door_wood_open_top", true, true)

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

minetest.register_node("cdda_nodes:water", {
    description = "Water Surface",
    tiles = {"default_stone.png^[colorize:#307ac6:160"},
    walkable = false,
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

-- Compact visual entries for CDDA's one-tile vertical connections. Input and
-- native stairfinding choose the destination; these nodes never move a player.
local steps = {}
for i = 0, 5 do
    steps[#steps + 1] = {-0.48, -0.5, -0.5 + i / 6, 0.48, -0.5 + (i + 1) / 6, -0.5 + (i + 1) / 6}
end
minetest.register_node("cdda_nodes:stairs_entry", {
    description = "Native stairs up",
    drawtype = "nodebox", paramtype = "light", tiles = {"default_stone.png"},
    node_box = {type = "fixed", fixed = steps}, walkable = false,
})
local well = {
    {-0.5, -0.5, -0.5, -0.38, 0.5, 0.5}, {0.38, -0.5, -0.5, 0.5, 0.5, 0.5},
    {-0.38, -0.5, -0.5, 0.38, 0.5, -0.38}, {-0.38, -0.5, 0.38, 0.38, 0.5, 0.5},
}
for i = 0, 5 do
    well[#well + 1] = {-0.38, -0.5, -0.38 + i * 0.76 / 6,
        -0.12, 0.5 - (i + 1) / 6, -0.38 + (i + 1) * 0.76 / 6}
end
minetest.register_node("cdda_nodes:stairwell", {
    description = "Native stairs down",
    drawtype = "nodebox", paramtype = "light", tiles = {"default_stone.png"},
    node_box = {type = "fixed", fixed = well}, walkable = false,
})
for _, half in ipairs({"lower", "upper"}) do
    local rungs = {{-0.4, -0.5, 0.32, -0.3, 0.5, 0.42}, {0.3, -0.5, 0.32, 0.4, 0.5, 0.42}}
    for i = 0, 3 do
        rungs[#rungs + 1] = {-0.3, -0.43 + i / 4, 0.32, 0.3, -0.36 + i / 4, 0.42}
    end
    minetest.register_node("cdda_nodes:ladder_" .. half, {
        description = "Native ladder up", drawtype = "nodebox", paramtype = "light",
        tiles = {"default_wood.png"}, node_box = {type = "fixed", fixed = rungs}, walkable = false,
    })
end

minetest.log("action", "[CDDA] Pruned visual voxel nodes registered successfully.")
dofile(minetest.get_modpath("cdda_nodes") .. "/terrain-demo.lua")

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
