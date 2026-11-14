# Lee Load-All II Bushings

Regenerated source files and STL exports for a 200-piece Lee Load-All II bushing set.

## Contents

- `lee_bushing.scad` — OpenSCAD source used by the batch generator.
- `lee_bushing_customizer.scad` — Customizer source for parameterized models.
- `generate_all.py` — generates the 200 numbered STL files and CSV chart in `lee_sand_bushings_oem_fit/` (requires the OpenSCAD command-line application).
- `generate_renders.py` — generates selected preview images from the OpenSCAD source.
- `lee_sand_bushings_oem_fit/` — the 200 STL exports and `bushing_sand_chart.csv`.

The chart’s mass estimates are based on the sand density constant in `generate_all.py`; they describe the documented sand test material and are not propellant measurements or loading data.

## Regenerate the STL set

From the repository root, with OpenSCAD installed and available as `openscad` on `PATH`:

```sh
python3 generate_all.py
```

This rewrites the STL files and chart in `lee_sand_bushings_oem_fit/`.
