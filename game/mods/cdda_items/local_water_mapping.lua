-- Explicit liquid overrides independent of generated batch mappings.
-- water_clean and water are liquids; use the project's attributed water glyph, never food art.
local hidden_groups = {not_in_creative_inventory = 1}
local overrides = {
    ["cdda_items:i_4d1c937c927b4d26"] = {
        description = "CDDA visual: clean water",
        inventory_image = "cdda_status_water.png",
        stack_max = 1,
        groups = hidden_groups,
    },
    ["cdda_items:i_d3cacd4c82e5be70"] = {
        description = "CDDA visual: untreated water",
        inventory_image = "cdda_status_water.png^[colorize:#A08040:60",
        stack_max = 1,
        groups = hidden_groups,
    },
}

for name, def in pairs(overrides) do
    if minetest.registered_items[name] then
        minetest.override_item(name, def)
    else
        minetest.register_craftitem(name, def)
    end
end
