import re

with open("luanti/src/cdda/cdda_bridge.cpp", "r") as f:
    content = f.read()

# Includes
new_includes = """
#include <IGUIEnvironment.h>
#include <IGUIStaticText.h>
#include <ISceneManager.h>
#include <IMeshSceneNode.h>
"""
content = content.replace("#include \"nodedef.h\"", "#include \"nodedef.h\"\n" + new_includes)

# Vehicle parsing inside process_message
# Locate WorldSnapshot parsing
search_str = """
                // Sync entities
                if (snap->entities()) {"""

replace_str = """
                // Sync vehicles
                if (snap->vehicles()) {
                    metrics_.vehicles_count = snap->vehicles()->size();
                    for (size_t i = 0; i < snap->vehicles()->size(); ++i) {
                        const auto* veh_state = snap->vehicles()->Get(i);
                        uint64_t vid = veh_state->id();
                        v3f target = v3f(
                            veh_state->pivot()->x(),
                            veh_state->pivot()->z() * 3.0f,
                            -veh_state->pivot()->y()
                        );

                        auto it = vehicles_.find(vid);
                        if (it == vehicles_.end()) {
                            VisualVehicle vv;
                            vv.id = vid;
                            vv.name = veh_state->name() ? veh_state->name()->str() : "";
                            vv.current_pos = target;
                            vv.target_pos = target;
                            vv.rotation = veh_state->rotation();
                            if (veh_state->components()) {
                                for (size_t ci = 0; ci < veh_state->components()->size(); ++ci) {
                                    const auto* comp = veh_state->components()->Get(ci);
                                    VisualVehicleComponent vc;
                                    vc.name = comp->name() ? comp->name()->str() : "";
                                    vc.mount_offset = v3f(comp->mount_offset()->x(), 0.0f, -comp->mount_offset()->y());
                                    vc.is_broken = comp->is_broken();
                                    vc.is_open = comp->is_open();
                                    vc.scene_node = nullptr; // Initialize lazily
                                    vv.components.push_back(vc);
                                }
                            }
                            vehicles_[vid] = vv;
                        } else {
                            it->second.target_pos = target;
                            it->second.rotation = veh_state->rotation();
                            // Assuming components don't change frequently for this prototype, or update them here
                        }
                    }
                }

                // Sync entities
                if (snap->entities()) {"""
content = content.replace(search_str, replace_str)

# In CddaBridge::Impl, add vehicles_ map, GUI text pointer
impl_search = "std::unordered_map<uint64_t, VisualEntity> entities_;"
impl_replace = "std::unordered_map<uint64_t, VisualEntity> entities_;\n    std::unordered_map<uint64_t, VisualVehicle> vehicles_;\n    irr::gui::IGUIStaticText* debug_text_{nullptr};\n    irr::scene::ISceneManager* smgr_{nullptr};"
content = content.replace(impl_search, impl_replace)

# Modify update to do LERP for vehicles and draw their nodes
update_search = """
        // Interpolate visual entities
        for (auto& [id, ent] : entities_) {
            v3f diff = ent.target_pos - ent.current_pos;
            ent.current_pos += diff * std::min(1.0f, dtime * 12.0f);
        }
"""
update_replace = """
        // Interpolate visual entities
        for (auto& [id, ent] : entities_) {
            v3f diff = ent.target_pos - ent.current_pos;
            ent.current_pos += diff * std::min(1.0f, dtime * 12.0f);
        }

        // Interpolate visual vehicles and manage scene nodes
        if (client_ && !smgr_) {
            smgr_ = client_->getSceneManager();
        }

        for (auto& [id, veh] : vehicles_) {
            v3f diff = veh.target_pos - veh.current_pos;
            veh.current_pos += diff * std::min(1.0f, dtime * 12.0f);

            if (smgr_) {
                for (auto& comp : veh.components) {
                    if (!comp.scene_node) {
                        // Create a simple cube node for the vehicle component
                        // BS (Block Size) is 10.0f
                        irr::scene::ISceneNode* node = smgr_->addCubeSceneNode(10.0f);
                        if (node) {
                            node->setMaterialFlag(irr::video::EMF_LIGHTING, false);
                            if (comp.is_broken) {
                                // Maybe darker color, just handle node creation
                            }
                            comp.scene_node = node;
                        }
                    }
                    if (comp.scene_node) {
                        irr::scene::ISceneNode* node = static_cast<irr::scene::ISceneNode*>(comp.scene_node);
                        
                        // Calculate world position based on pivot and rotation
                        // CDDA rotations: 0 is East, 90 is South, etc.
                        float rad = veh.rotation * irr::core::DEGTORAD;
                        float cos_r = std::cos(rad);
                        float sin_r = std::sin(rad);
                        
                        // Apply rotation to mount offset
                        // Mount offset X is forward/back, Y is left/right in CDDA
                        float ox = comp.mount_offset.X;
                        float oz = comp.mount_offset.Z;
                        
                        float rx = ox * cos_r - oz * sin_r;
                        float rz = ox * sin_r + oz * cos_r;
                        
                        v3f world_pos(
                            (veh.current_pos.X + rx) * 10.0f, // Luanti uses BS=10.0f
                            (veh.current_pos.Y) * 10.0f,
                            (veh.current_pos.Z + rz) * 10.0f
                        );
                        
                        node->setPosition(world_pos);
                        node->setRotation(v3f(0.0f, -veh.rotation, 0.0f));
                    }
                }
            }
        }
"""
content = content.replace(update_search, update_replace)

with open("luanti/src/cdda/cdda_bridge.cpp", "w") as f:
    f.write(content)

