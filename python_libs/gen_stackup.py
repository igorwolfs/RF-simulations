import FreeCAD as App
import Part

# ==========================================
# User parameters
# ==========================================

pcb_width  = 100   # mm
pcb_height = 100   # mm

layers = [
    ("Top_Copper",     0.035),
    ("Prepreg_1",      0.21040),
    ("Inner_L2_Cu",    0.0152),
    ("Core",           1.065),
    ("Inner_L3_Cu",    0.0152),
    ("Prepreg_2",      0.21040),
    ("Bottom_Copper",  0.035)
]

box_extra_height = 2.0    # Extra height ABOVE and BELOW PCB stack (mm)
transparent_value = 70    # 0 = opaque, 100 = fully transparent


# ==========================================
# Ensure active document
# ==========================================
doc = App.ActiveDocument
if doc is None:
    raise RuntimeError("No active document. Please open a document before running the macro.")


# ==========================================
# Helper: get or create object by name
# ==========================================
def get_or_create(name, shape):
    obj = doc.getObject(name)
    if obj:
        obj.Shape = shape
    else:
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
    return obj


# ==========================================
# Helper: apply transparency if pattern matches
# ==========================================
def apply_transparency(obj):
    name = obj.Name.lower()
    if ("prepreg" in name) or ("core" in name) or (name == "box"):
        obj.ViewObject.Transparency = transparent_value
    else:
        obj.ViewObject.Transparency = 0


# ==========================================
# Build PCB layers
# ==========================================
current_z = 0.0
total_height = sum(th for _, th in layers)

for name, thickness in layers:
    shape = Part.makeBox(
        pcb_width,
        pcb_height,
        thickness,
        App.Vector(0, 0, current_z)
    )
    obj = get_or_create(name, shape)
    apply_transparency(obj)
    current_z += thickness
    


# ==========================================
# Create enclosing BOX
# ==========================================

box_height = total_height + 2 * box_extra_height
box_z = -box_extra_height  # center the PCB vertically

box_shape = Part.makeBox(
    pcb_width,
    pcb_height,
    box_height,
    App.Vector(0, 0, box_z)
)

box_obj = get_or_create("Box", box_shape)
apply_transparency(box_obj)


# ==========================================
# Final recompute
# ==========================================
doc.recompute()

print("✓ Layers created/updated and transparency applied.")
