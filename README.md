# Computational-Photonics-Testbench

This is a Python project I built to simulate geometric optics. Instead of just calculating formulas on paper, this script traces light rays as they travel through different optical environments to see how they behave.

## How It Works

The simulation is broken down into three main physics models:

1. **Fiber Optics (Total Internal Reflection):** Simulates a light ray bouncing through a step-index fiber. It calculates the critical angle to show when the light stays inside the core and when it leaks out.
2. **The Prism (Chromatic Dispersion):** Takes white light and uses Snell's Law and a refractive index matrix to split it into a visible spectrum (400nm - 800nm), calculating the deviation angle for each color.
3. **The Eye (Lens Accommodation):** Models the human eye as a simple converging lens. It automatically calculates the lens power needed to focus the incoming light perfectly onto the retina.

## Folder Structure

```text
├── src/
│   ├── opticalfibers.py       # Phase 1: TIR and boundary collisions
│   ├── prism_disperser.py      # Phase 2: Refraction and color dispersion
│   ├── eye_target.py           # Phase 3: Focal length calculations
│   └── main_dashboard.py       # The UI that ties it all together
├── docs/                       # Math derivations and notes
└── README.md
