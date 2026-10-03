import re

with open("cdda/src/cwm/cwm_map_exporter.h", "r") as f:
    content = f.read()

content = content.replace("game& g", "game& g,\n        bool include_chunks = true")

with open("cdda/src/cwm/cwm_map_exporter.h", "w") as f:
    f.write(content)

with open("cdda/src/cwm/cwm_map_exporter.cpp", "r") as f:
    content = f.read()

content = content.replace("game& g\n) {", "game& g,\n    bool include_chunks\n) {")
content = content.replace("game& g) {", "game& g, bool include_chunks) {")

chunk_logic = """
    std::vector<flatbuffers::Offset<CDDA::CWM::ChunkSnapshot>> chunk_offsets;

    int z_min = u_pos.z - 1;
    int z_max = u_pos.z + 1;

    if (include_chunks) {
        for (int z_level = z_min; z_level <= z_max; ++z_level) {
"""

content = re.sub(
    r"    std::vector<flatbuffers::Offset<CDDA::CWM::ChunkSnapshot>> chunk_offsets;\n\n    int z_min = u_pos\.z - 1;\n    int z_max = u_pos\.z \+ 1;\n\n    for \(int z_level = z_min; z_level <= z_max; \+\+z_level\) \{",
    chunk_logic,
    content
)

# Also close the if block right after chunks are processed and before chunks_vec = ...
close_if = """
                chunk_offsets.push_back(chunk_snap);
            }
        }
    }

    auto chunks_vec = include_chunks ? fbb.CreateVector(chunk_offsets) : 0;
"""

content = re.sub(
    r"                chunk_offsets\.push_back\(chunk_snap\);\n            }\n        }\n    }\n\n    auto chunks_vec = fbb\.CreateVector\(chunk_offsets\);",
    close_if,
    content
)


with open("cdda/src/cwm/cwm_map_exporter.cpp", "w") as f:
    f.write(content)

# Update cwm_server.cpp to pass false for MoveRequest
with open("cdda/src/cwm/cwm_server.cpp", "r") as f:
    content = f.read()

content = content.replace(
    "auto snap = CwmMapExporter::export_world_snapshot(sequence_counter_++, world_revision_, u, m, g);",
    "auto snap = CwmMapExporter::export_world_snapshot(sequence_counter_++, world_revision_, u, m, g, false);"
)

# Except for initial snapshot, we want it to be true
content = content.replace(
    "if (!snapshot_sent_) {\n        auto snap = CwmMapExporter::export_world_snapshot(sequence_counter_++, world_revision_, u, m, g, false);",
    "if (!snapshot_sent_) {\n        auto snap = CwmMapExporter::export_world_snapshot(sequence_counter_++, world_revision_, u, m, g, true);"
)

content = content.replace(
    "// Push fresh snapshot on handshake\n            auto snap = CwmMapExporter::export_world_snapshot(sequence_counter_++, world_revision_, u, m, g, false);",
    "// Push fresh snapshot on handshake\n            auto snap = CwmMapExporter::export_world_snapshot(sequence_counter_++, world_revision_, u, m, g, true);"
)

# And for InteractRequest, if USE
content = content.replace(
    "if (req->action() == CDDA::CWM::InteractAction::USE) {\n                    auto snap = CwmMapExporter::export_world_snapshot(sequence_counter_++, world_revision_, u, m, g, false);",
    "if (req->action() == CDDA::CWM::InteractAction::USE) {\n                    auto snap = CwmMapExporter::export_world_snapshot(sequence_counter_++, world_revision_, u, m, g, true);"
)

with open("cdda/src/cwm/cwm_server.cpp", "w") as f:
    f.write(content)

