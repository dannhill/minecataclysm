-- CDDA owns all item state and gameplay.
-- This mod registers presentation-only item definitions.

cdda_items = rawget(_G, "cdda_items") or {}

minetest.register_craftitem("cdda_items:fallback_generic", {
    description = "CDDA item",
    inventory_image = "cdda_items_fallback.png",
    stack_max = 1,
})

local modpath = minetest.get_modpath("cdda_items")
local generated = modpath .. "/generated_mapping.lua"
local f = io.open(generated, "r")
if f then
    f:close()
    dofile(generated)
end

dofile(modpath .. "/local_water_mapping.lua")

minetest.log("action", "[CDDA] Item presentation definitions registered.")
