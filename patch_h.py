import re

with open("luanti/src/cdda/cdda_bridge.h", "r") as f:
    content = f.read()

# Add IGUIEnvironment to includes
content = content.replace("#include \"irr_v3d.h\"", "#include \"irr_v3d.h\"\n\nnamespace irr { namespace gui { class IGUIEnvironment; class IGUIStaticText; } }")

# Add Vehicle structs
vehicle_struct = """
struct VisualVehicleComponent {
    std::string name;
    v3f mount_offset;
    bool is_broken;
    bool is_open;
    void* scene_node{nullptr}; // Pointer to Irrlicht scene node
};

struct VisualVehicle {
    uint64_t id{0};
    std::string name;
    v3f current_pos;
    v3f target_pos;
    float rotation{0.0f};
    v3f velocity;
    std::vector<VisualVehicleComponent> components;
};
"""

content = content.replace("struct VisualEntity {", vehicle_struct + "\nstruct VisualEntity {")

# Add renderDebugOverlay
method = """
    // F3 Debug Overlay
    void renderDebugOverlay(irr::gui::IGUIEnvironment* guienv);
"""
content = content.replace("Metrics getMetrics() const;", "Metrics getMetrics() const;\n" + method)

with open("luanti/src/cdda/cdda_bridge.h", "w") as f:
    f.write(content)
