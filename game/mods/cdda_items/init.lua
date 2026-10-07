-- CDDA owns all item state and gameplay.
-- This mod registers presentation-only item definitions.

cdda_items = rawget(_G, "cdda_items") or {}
cdda_items.visual_by_cdda_id = {}

minetest.register_craftitem("cdda_items:fallback_generic", {
    description = "CDDA item",
    inventory_image = "cdda_items_fallback.png",
    stack_max = 1,
})

local generated = minetest.get_modpath("cdda_items") .. "/generated_mapping.lua"
local f = io.open(generated, "r")
if f then
    f:close()
    dofile(generated)
end

function cdda_items.resolve_visual(cdda_id)
    return cdda_items.visual_by_cdda_id[cdda_id] or "cdda_items:fallback_generic"
end

minetest.log("action", "[CDDA] Item presentation definitions registered.")
