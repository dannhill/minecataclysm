-- Presentation-only terrain comparison. Native CDDA owns all terrain state.
local function cube(name, tiles)
    minetest.register_node("cdda_nodes:demo_" .. name, {
        description = "Terrain comparison: " .. name,
        tiles = tiles,
        walkable = true,
        pointable = false,
        diggable = false,
        groups = {not_in_creative_inventory = 1},
    })
end

for i = 0, 2 do
    local tints = {"#568c37:75", "#638a42:85", "#487b32:75"}
    local top = "mcl_core_grass_block_top.png^[colorize:" .. tints[i + 1]
    local side = "default_dirt.png^(mcl_core_grass_block_side_overlay.png^[colorize:" .. tints[i + 1] .. ")"
    cube("grass_" .. i, {top, "default_dirt.png", side})
    local dirt = i == 1 and "mcl_core_coarse_dirt.png" or "default_dirt.png"
    cube("dirt_" .. i, {dirt .. (i == 2 and "^[colorize:#68513d:45" or "")})
end
cube("sand", {"default_sand.png"})
cube("sidewalk", {"default_stone.png^[colorize:#c9c7be:145"})
cube("asphalt", {"default_stone.png^[colorize:#242930:190"})
cube("tree", {"default_tree_top.png", "default_tree_top.png", "default_tree.png"})

minetest.register_node("cdda_nodes:demo_leaves", {
    description = "Terrain comparison: tree crown",
    drawtype = "allfaces_optional",
    tiles = {"default_leaves.png^[colorize:#487a32:100"},
    paramtype = "light",
    walkable = true,
    pointable = false,
    diggable = false,
    groups = {not_in_creative_inventory = 1},
})

-- Only placed for native shrub / long-grass terrain, never random obstacles.
for _, entry in ipairs({{"shrub", 0.75}, {"tall_grass", 0.4}}) do
    minetest.register_node("cdda_nodes:demo_" .. entry[1], {
        description = "Terrain comparison: " .. entry[1],
        drawtype = "plantlike",
        tiles = {"default_leaves.png^[colorize:#557d32:110"},
        visual_scale = entry[2],
        paramtype = "light",
        sunlight_propagates = true,
        walkable = false,
        pointable = false,
        diggable = false,
        groups = {not_in_creative_inventory = 1},
    })
end

-- One surface node, no independent fluid simulation. Animation is visual only.
minetest.register_node("cdda_nodes:demo_water", {
    description = "Terrain comparison: water surface",
    tiles = {{name = "default_water_source_animated.png",
        animation = {type = "vertical_frames", aspect_w = 16, aspect_h = 16, length = 2.0}}},
    paramtype = "light",
    walkable = false,
    pointable = false,
    diggable = false,
    groups = {not_in_creative_inventory = 1},
})
