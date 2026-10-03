import re

with open("cdda/src/cwm/cwm_map_exporter.cpp", "r") as f:
    content = f.read()

field_logic = """
    // 5. Dynamic Fields (Fire, smoke, gas)
    std::vector<flatbuffers::Offset<CDDA::CWM::FieldState>> field_offsets;
    if (include_chunks) {
        for (int z_level = z_min; z_level <= z_max; ++z_level) {
"""

content = content.replace(
    "    // 5. Dynamic Fields (Fire, smoke, gas)\n    std::vector<flatbuffers::Offset<CDDA::CWM::FieldState>> field_offsets;\n    for (int z_level = z_min; z_level <= z_max; ++z_level) {",
    field_logic
)

close_field = """
                        field_offsets.push_back(field_snap);
                    }
                }
            }
        }
    }
"""

content = re.sub(
    r"                        field_offsets\.push_back\(field_snap\);\n                    }\n                }\n            }\n        }",
    close_field,
    content
)

with open("cdda/src/cwm/cwm_map_exporter.cpp", "w") as f:
    f.write(content)

