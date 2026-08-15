from pathlib import Path

import numpy as np
from PIL import Image


SOURCE = Path("stage2_download")
OUT = Path("stage2_custom")
OUT.mkdir(exist_ok=True)

rgb = np.asarray(Image.open(SOURCE).convert("RGB"), dtype=np.uint8)


def save(name: str, array: np.ndarray) -> None:
    Image.fromarray(array.astype(np.uint8), mode="L").save(OUT / name)


for bit in range(8):
    planes = [((rgb[:, :, channel] >> bit) & 1) for channel in range(3)]
    save(f"bit{bit}_r_xor_g.png", (planes[0] ^ planes[1]) * 255)
    save(f"bit{bit}_r_xor_b.png", (planes[0] ^ planes[2]) * 255)
    save(f"bit{bit}_g_xor_b.png", (planes[1] ^ planes[2]) * 255)
    save(
        f"bit{bit}_rgb_parity.png",
        (planes[0] ^ planes[1] ^ planes[2]) * 255,
    )

for left, right, label in ((0, 1, "r_g"), (0, 2, "r_b"), (1, 2, "g_b")):
    delta = rgb[:, :, left].astype(np.int16) - rgb[:, :, right].astype(np.int16)
    save(f"diff_{label}_signed.png", np.clip(delta + 128, 0, 255))
    save(f"diff_{label}_absolute.png", np.clip(np.abs(delta) * 4, 0, 255))

for channel, label in enumerate("rgb"):
    spectrum = np.log1p(
        np.abs(np.fft.fftshift(np.fft.fft2(rgb[:, :, channel].astype(float))))
    )
    spectrum -= spectrum.min()
    spectrum *= 255.0 / max(spectrum.max(), 1.0)
    save(f"fft_{label}.png", spectrum)

print(f"wrote {len(list(OUT.glob('*.png')))} images to {OUT}")
