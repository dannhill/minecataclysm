import re

with open("luanti/src/cdda/cdda_bridge.h", "r") as f:
    content = f.read()

# Add vehicles_count to metrics
content = content.replace("uint32_t entities_count{0};", "uint32_t entities_count{0};\n        uint32_t vehicles_count{0};")

with open("luanti/src/cdda/cdda_bridge.h", "w") as f:
    f.write(content)
