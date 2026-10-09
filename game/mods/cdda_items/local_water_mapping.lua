-- One explicit user-requested correction, independent of generated batch mappings.
-- water_clean is a liquid; use the project's attributed water glyph, never food art.
local name = "cdda_items:i_4d1c937c927b4d26"
local definition = {description = "CDDA visual: clean water", inventory_image = "cdda_status_water.png", stack_max = 1,
    groups = {not_in_creative_inventory = 1}}
if minetest.registered_items[name] then
    minetest.override_item(name, definition)
else
    minetest.register_craftitem(name, definition)
end
cdda_items.visual_by_cdda_id["water_clean"] = name
