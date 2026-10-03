import re

with open("luanti/src/cdda/cdda_bridge.cpp", "r") as f:
    content = f.read()

# Fix VehicleComponentState methods
content = content.replace("vc.name = comp->name() ? comp->name()->str() : \"\";", "vc.name = comp->part_id() ? comp->part_id()->str() : \"\";")
content = content.replace("vc.mount_offset = v3f(comp->mount_offset()->x(), 0.0f, -comp->mount_offset()->y());", "vc.mount_offset = v3f(comp->offset()->x(), 0.0f, -comp->offset()->y());")
content = content.replace("vc.is_broken = comp->is_broken();", "vc.is_broken = comp->broken();")
content = content.replace("vc.is_open = comp->is_open();", "vc.is_open = comp->open();")

# Fix addCubeSceneNode
content = content.replace("irr::scene::ISceneNode* node = smgr_->addCubeSceneNode(10.0f);", "irr::scene::ISceneNode* node = smgr_->addEmptySceneNode();")
content = content.replace("node->setMaterialFlag(irr::video::EMF_LIGHTING, false);", "// node->getMaterial(0).setFlag(irr::video::EMF_LIGHTING, false);")

# Move renderDebugOverlay into namespace cdda_client
content = content.replace("void CddaBridge::renderDebugOverlay(irr::gui::IGUIEnvironment* guienv) {", "namespace cdda_client {\nvoid CddaBridge::renderDebugOverlay(irr::gui::IGUIEnvironment* guienv) {")

content = content + "\n} // namespace cdda_client\n"

with open("luanti/src/cdda/cdda_bridge.cpp", "w") as f:
    f.write(content)

