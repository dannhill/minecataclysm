import re

with open("cdda/src/cwm/cwm_map_exporter.cpp", "r") as f:
    text = f.read()

# First, remove the hack lines
text = text.replace("    }\n    }\n    return builder.finish_message(CDDA::CWM::Payload::WorldSnapshot, world_snap.Union());", "    return builder.finish_message(CDDA::CWM::Payload::WorldSnapshot, world_snap.Union());")
text = text.replace("    }\n    }\n    return builder.finish_message(CDDA::CWM::Payload::EntityState, state.Union());", "    return builder.finish_message(CDDA::CWM::Payload::EntityState, state.Union());")

# Now fix the fields brace matching
bad_field_loop = """
    if (include_chunks) {
        for (int z_level = z_min; z_level <= z_max; ++z_level) {

        for (int y = 0; y < 128; ++y) {
            for (int x = 0; x < 128; ++x) {
                tripoint p(x, y, z_level);
                if (m.has_field_at(p)) {
                    const field& fld = m.field_at(p);
                    for (const auto& pair : fld) {
                        const field_type_id& ftype = pair.first;
                        const field_entry& fentry = pair.second;
                        uint16_t fid = 1;
                        std::string fstr = ftype.id().str();
                        if (fstr.find("smoke") != std::string::npos) fid = 2;
                        else if (fstr.find("fire") != std::string::npos) fid = 1;
                        else fid = 3;

                        CDDA::CWM::Coord3i coord(p.x, p.y, p.z);
                        uint8_t density = static_cast<uint8_t>(fentry.get_field_intensity());
                        uint32_t age = static_cast<uint32_t>(to_turns<int>(fentry.get_field_age()));
                        field_offsets.push_back(CDDA::CWM::CreateFieldState(fbb, &coord, fid, density, age));
                    }
                }
            }
        }
    }
    auto fields_vec = fbb.CreateVector(field_offsets);
"""

good_field_loop = """
    if (include_chunks) {
        for (int z_level = z_min; z_level <= z_max; ++z_level) {
            for (int y = 0; y < 128; ++y) {
                for (int x = 0; x < 128; ++x) {
                    tripoint p(x, y, z_level);
                    if (m.has_field_at(p)) {
                        const field& fld = m.field_at(p);
                        for (const auto& pair : fld) {
                            const field_type_id& ftype = pair.first;
                            const field_entry& fentry = pair.second;
                            uint16_t fid = 1;
                            std::string fstr = ftype.id().str();
                            if (fstr.find("smoke") != std::string::npos) fid = 2;
                            else if (fstr.find("fire") != std::string::npos) fid = 1;
                            else fid = 3;

                            CDDA::CWM::Coord3i coord(p.x, p.y, p.z);
                            uint8_t density = static_cast<uint8_t>(fentry.get_field_intensity());
                            uint32_t age = static_cast<uint32_t>(to_turns<int>(fentry.get_field_age()));
                            field_offsets.push_back(CDDA::CWM::CreateFieldState(fbb, &coord, fid, density, age));
                        }
                    }
                }
            }
        }
    }
    auto fields_vec = fbb.CreateVector(field_offsets);
"""

text = text.replace(bad_field_loop.strip(), good_field_loop.strip())

with open("cdda/src/cwm/cwm_map_exporter.cpp", "w") as f:
    f.write(text)
