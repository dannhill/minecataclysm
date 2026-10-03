import re

with open("cdda/src/cwm/cwm_main.cpp", "r") as f:
    text = f.read()

# Comment out custom overmap generation
search = """    get_map() = map();
    overmap_special_batch empty_specials(point_abs_om{});
    overmap_buffer.create_custom_overmap(point_abs_om{}, empty_specials);

    map& here = get_map();"""

replace = """    get_map() = map();
    
    // Milestone 6: Real World Generation (bypassing the mock empty overmap)
    // overmap_special_batch empty_specials(point_abs_om{});
    // overmap_buffer.create_custom_overmap(point_abs_om{}, empty_specials);

    map& here = get_map();"""

if search in text:
    text = text.replace(search, replace)
    with open("cdda/src/cwm/cwm_main.cpp", "w") as f:
        f.write(text)
        print("Patched cwm_main.cpp")
else:
    print("Could not find the target string in cwm_main.cpp")
