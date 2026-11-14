import csv
import math
import os
import subprocess

OPENSCAD_PATH = "openscad"

# --- Batch Configuration ---
START_NUM = 1
END_NUM = 200
OUTPUT_DIR = "lee_sand_bushings_oem_fit"

# --- Stock Lee Bushing Outer Dimensions (mm) ---
BARREL_OD_MM = 15.22
BARREL_HEIGHT_MM = 25.11
OVERALL_LENGTH_MM = 21.85  # Back of barrel to front tip of raised numbers

# --- Empirically Calibrated Sand Density ---
# Validated on your hardware/PETG prints:
#   095 (6.607 mm bore) -> 12.0 gr
#   120 (7.939 mm bore) -> 17.4 gr
#   127 (8.312 mm bore) -> 19.0 gr
SAND_GRAINS_PER_CC = 13.9391
GRAINS_PER_GRAM = 15.4323584

# --- Bore Progression (001 to 200) ---
# 1.60 mm (~0.7 gr) up to 12.20 mm (~40.9 gr, leaving 1.51 mm wall thickness)
MIN_BORE_MM = 1.60
MAX_BORE_MM = 12.20


def get_bore_mm(index):
    """Linearly scales inner bore diameter from MIN_BORE_MM (001) to MAX_BORE_MM (200)."""
    step = (MAX_BORE_MM - MIN_BORE_MM) / (END_NUM - START_NUM)
    return round(MIN_BORE_MM + (index - START_NUM) * step, 3)


def get_sand_metrics(bore_mm):
    """Returns (volume_cc, grains, grams) for a straight cylinder of height BARREL_HEIGHT_MM."""
    vol_mm3 = math.pi * ((bore_mm / 2.0) ** 2) * BARREL_HEIGHT_MM
    vol_cc = vol_mm3 / 1000.0
    grains = vol_cc * SAND_GRAINS_PER_CC
    grams = grains / GRAINS_PER_GRAM
    return vol_cc, grains, grams


# --- OpenSCAD Template ---
OPENSCAD_TEMPLATE = """
$fn = 128;

// --- Stock Lee Outer Dimensions (mm) ---
barrel_od      = {barrel_od};      // 15.22 mm main cylinder diameter
barrel_height  = {barrel_height};  // 25.11 mm overall height
overall_length = {overall_length}; // 21.85 mm back of barrel to front of tab

// Side Rectangular Index Tab (matched to OEM proportions)
tab_width      = 12.50;            // Narrower than 15.22 mm barrel, matching OEM step
tab_height     = 8.20;             // ~1/3 of 25.11 mm barrel height
text_extrude   = 0.55;             // 0.55 mm raised number depth

// Calculated distance from cylinder center to front face of tab (keeps total length = 21.85 mm)
tab_front_from_center = overall_length - (barrel_od / 2) - text_extrude;

// Dynamic Bore & Embossed Front Text
label          = "{label}";
bore_d         = {bore_mm};
text_size      = 4.8;
font_style     = "Liberation Sans:style=Bold";

difference() {{
    union() {{
        // 1. Main Cylindrical Barrel
        cylinder(h = barrel_height, d = barrel_od);

        // 2. Rectangular Side Index Tab (Protruding along -Y axis)
        translate([-tab_width / 2, -tab_front_from_center, 0])
            cube([tab_width, tab_front_from_center, tab_height]);

        // 3. Embossed (Raised) 3-Digit Number on Front Vertical Face of Tab
        translate([0, -tab_front_from_center + 0.05, tab_height / 2])
            rotate([90, 0, 0])
                linear_extrude(height = text_extrude)
                    text(
                        text   = label,
                        size   = text_size,
                        font   = font_style,
                        halign = "center",
                        valign = "center"
                    );
    }}

    // 4. Center Straight Through-Bore
    translate([0, 0, -1])
        cylinder(h = barrel_height + 2, d = bore_d);

    // 5. Top & Bottom Lead-In Chamfers for smooth sand flow
    translate([0, 0, barrel_height - 0.6])
        cylinder(h = 0.61, d1 = bore_d, d2 = bore_d + 0.8);
    translate([0, 0, -0.01])
        cylinder(h = 0.61, d1 = bore_d + 0.8, d2 = bore_d);
}}
"""


def generate_all_bushings():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_scad = os.path.join(OUTPUT_DIR, "temp_lee_bushing.scad")
    csv_path = os.path.join(OUTPUT_DIR, "bushing_sand_chart.csv")

    print(f"Generating Calibrated OEM-Fit Lee Bushings ({START_NUM:03d} to {END_NUM:03d})...\n")

    with open(csv_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Bushing_Num", "Bore_mm", "Volume_cc", "Est_Grains", "Est_Grams", "Filename"])

        for i in range(START_NUM, END_NUM + 1):
            label = f"{i:03d}"
            bore_mm = get_bore_mm(i)
            vol_cc, grains, grams = get_sand_metrics(bore_mm)

            filename = f"lee_bushing_{label}_bore_{bore_mm:.2f}mm_{grains:.1f}gr.stl"
            output_stl_path = os.path.join(OUTPUT_DIR, filename)

            writer.writerow([label, f"{bore_mm:.3f}", f"{vol_cc:.5f}", f"{grains:.2f}", f"{grams:.3f}", filename])

            scad_code = OPENSCAD_TEMPLATE.format(
                barrel_od=BARREL_OD_MM,
                barrel_height=BARREL_HEIGHT_MM,
                overall_length=OVERALL_LENGTH_MM,
                label=label,
                bore_mm=bore_mm
            )

            with open(temp_scad, "w") as f:
                f.write(scad_code)

            cmd = [OPENSCAD_PATH, "-o", output_stl_path, temp_scad]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"[{i:03d}/{END_NUM:03d}] {filename}")
            else:
                print(f"[{i:03d}/{END_NUM:03d}] Error generating {filename}:\n{result.stderr}")

    if os.path.exists(temp_scad):
        os.remove(temp_scad)

    print(f"\nDone! STLs and '{csv_path}' saved to '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    generate_all_bushings()
