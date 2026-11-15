"""
Automated script to upgrade 'Flame in Freefall - NASA Space Apps.pptx'
and export to 'Flame in Freefall - NASA Space Apps.pdf' using PowerPoint COM.
"""

import zipfile
import shutil
from pathlib import Path
from PIL import Image
import io

PPTX_PATH = Path("Flame in Freefall - NASA Space Apps.pptx")
BACKUP_PATH = Path("Flame in Freefall - NASA Space Apps (Original).pptx")
TEMP_PPTX = Path("Flame in Freefall - NASA Space Apps (Updated).pptx")
NEW_SLIDE4_IMG = Path("assets/slides/slide_4_physics_hud_and_conformal_curve.png")

# Text replacements map: (Slide number -> [(old_text, new_text)])
REPLACEMENTS = {
    1: [
        (" Stagnant flames choke, drafts trigger spread.", " Stagnant flames choke, drafts (1–10 cm/s) trigger rapid spread."),
        (" 3D simulation, ML prediction, air-gapped autonomy.", " Real-time 3D simulation, sub-2ms ML, air-gapped autonomy.")
    ],
    2: [
        (" High oxygen accelerates thermal diffusivity.", " Artemis atmosphere (56.5 kPa, 34% O₂) accelerates spread."),
        (" Lower pressure speeds conductive preheating.", " Lower pressure increases gas thermal diffusivity (α ∝ 1/P).")
    ],
    4: [
        (" Real-time Pe, Da, α, Gr scales.", " Real-time transport scales (Pe = 2.45, Da = 12.4, α, Gr = 0.00)."),
        (" RBF kernel with cross-validation.", " GPR RBF kernel with 5-fold grouped cross-validation."),
        (" Outperforms baseline (Log R² = 0.934).", " Sub-2ms latency (1.91 ms p95, Log R² = 0.934, MAE = 0.22).")
    ],
    5: [
        (" Instantly shifts to local autonomy.", " Circuit breaker severs cloud link for 100% offline autonomy."),
        (" Mathematically declines hallucinated advice.", " Calibrated refusal gate (τ = 0.7455, AUC = 0.986) stops hallucinations.")
    ],
    6: [
        (" 40% lighter cylinders reduce fatalities.", " 40% lighter (saves 13 lbs/firefighter), cutting cardiac deaths."),
        (" Cuts municipal firefighter burns by 60%.", " Project FIRES spacesuit PBI gear cuts burns by >60% (NFPA 1971).")
    ],
    7: [
        (" 1.91 ms latency, 394 MB footprint.", " Sub-2ms p95 latency (1.91 ms), 394 MB RAM, 100% air-gapped.")
    ]
}

def update_pptx():
    print(f"Reading {PPTX_PATH}...")
    
    # Load new slide 4 image
    img_data = NEW_SLIDE4_IMG.read_bytes()
    # Optimize image size slightly for PPTX
    im = Image.open(io.BytesIO(img_data))
    print(f"New Slide 4 image loaded: size={im.size}")
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    img_data = buf.getvalue()

    with zipfile.ZipFile(PPTX_PATH, "r") as src, zipfile.ZipFile(TEMP_PPTX, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            content = src.read(item.filename)
            
            # Replace image 15 (Slide 4 screenshot)
            if item.filename == "ppt/media/image15.png":
                print(f"Replacing {item.filename} with high-res composite chart...")
                dst.writestr(item, img_data)
                continue

            # Update slide text
            for slide_num, reps in REPLACEMENTS.items():
                if item.filename == f"ppt/slides/slide{slide_num}.xml":
                    xml_text = content.decode("utf-8")
                    for old_t, new_t in reps:
                        if old_t in xml_text:
                            print(f"Slide {slide_num}: replaced '{old_t.strip()}' -> '{new_t.strip()}'")
                            xml_text = xml_text.replace(old_t, new_t)
                        else:
                            print(f"WARNING: '{old_t}' not found in slide {slide_num}")
                    content = xml_text.encode("utf-8")

            dst.writestr(item, content)

    # Overwrite the original PPTX with the updated one
    shutil.move(TEMP_PPTX, PPTX_PATH)
    print(f"Successfully updated {PPTX_PATH}")

if __name__ == "__main__":
    update_pptx()

