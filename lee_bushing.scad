// OEM-Fit Parametric Lee Load-All II Bushing (Calibrated for Silica Sand)
// Outer dimensions matched to stock Lee bushing:
//   - 15.22 mm cylinder OD
//   - 25.11 mm overall height
//   - 21.85 mm back of barrel to front tip of raised numbers
//
// Calibrated on PETG prints (13.9391 gr/cc effective density):
//   - 7.939 mm bore (Bushing 120) -> 17.4 grains
//   - 8.312 mm bore (Bushing 127) -> 19.0 grains

$fn = 128;

// --- Stock Lee Outer Dimensions (mm) ---
barrel_od      = 15.22; // Main cylinder diameter (mm)
barrel_height  = 25.11; // Overall height (mm)
overall_length = 21.85; // Back of barrel to front tip of raised numbers (mm)

// --- Side Rectangular Index Tab ---
tab_width      = 12.50; // Width across front face (mm)
tab_height     = 8.20;  // Height of side block (mm)
text_extrude   = 0.55;  // Raised number depth (mm)

// Calculated distance from cylinder center to front face of tab
tab_front_from_center = overall_length - (barrel_od / 2) - text_extrude;

// --- Number Marking Settings ---
text_size      = 4.8;
font_style     = "Liberation Sans:style=Bold";

// --- Core Bushing Module ---
module numbered_bushing(label, id_bore) {
    difference() {
        union() {
            // 1. Main Cylindrical Barrel
            cylinder(h = barrel_height, d = barrel_od);

            // 2. Rectangular Side Index Tab (Protruding along -Y axis)
            translate([-tab_width / 2, -tab_front_from_center, 0])
                cube([tab_width, tab_front_from_center, tab_height]);

            // 3. Embossed (Raised) Label on Front Vertical Face of Tab
            translate([0, -tab_front_from_center + 0.05, tab_height / 2])
                rotate([90, 0, 0])
                    linear_extrude(height = text_extrude)
                        text(
                            text   = str(label),
                            size   = text_size,
                            font   = font_style,
                            halign = "center",
                            valign = "center"
                        );
        }

        // 4. Center Straight Through-Bore
        translate([0, 0, -1])
            cylinder(h = barrel_height + 2, d = id_bore);

        // 5. Top & Bottom Lead-In Chamfers for smooth sand flow
        translate([0, 0, barrel_height - 0.6])
            cylinder(h = 0.61, d1 = id_bore, d2 = id_bore + 0.8);
        translate([0, 0, -0.01])
            cylinder(h = 0.61, d1 = id_bore + 0.8, d2 = id_bore);
    }
}

// --- Validated Production Bushings ---
// [Label, id_bore (mm)]
bushing_set = [
    ["17.4", 7.939], // Matches Bushing 120 -> 17.4 grains
    ["19.0", 8.312]  // Matches Bushing 127 -> 19.0 grains
];

spacing = barrel_od + 8;

for (i = [0 : len(bushing_set) - 1]) {
    translate([i * spacing, 0, 0])
        numbered_bushing(
            label   = bushing_set[i][0],
            id_bore = bushing_set[i][1]
        );
}
