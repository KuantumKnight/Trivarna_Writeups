#!/usr/bin/env python3
import base64
import itertools
import re
import subprocess
from pathlib import Path

from PIL import Image


ZIP = Path("attachments_Og9CGgW.zip")
PDF = Path("UNI6CTF_Quarterly_Report.pdf")


def run(*args, capture=False):
    return subprocess.run(
        args,
        check=True,
        text=capture,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


if not PDF.exists():
    run("unzip", "-o", str(ZIP))

# Combine the name/year components from the near-miss password candidates.
lines = [
    line.strip()
    for line in Path("candidate_passwords.txt").read_text().splitlines()
    if line.strip() and not line.startswith("#")
]
names = {line.rsplit("_", 1)[0] for line in lines}
years = {line.rsplit("_", 1)[1] for line in lines}
password = None
for candidate in (f"{name}_{year}" for name in names for year in years):
    result = subprocess.run(
        ["mutool", "info", "-p", candidate, str(PDF)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        password = candidate
        break
if password is None:
    raise RuntimeError("PDF password not found")

# The PDF keyword is base64 text containing the repeating XOR key in hex.
info = run("mutool", "show", "-p", password, str(PDF), "2", capture=True).stdout
keyword = re.search(r"/Keywords \(([^)]*)\)", info).group(1)
xor_key = bytes.fromhex(base64.b64decode(keyword).decode())

# Extract the chart and read its bottom-row blue-channel LSB message.
run("mutool", "extract", "-p", password, "-r", "-N", str(PDF), "10")
image = Image.open("image-0010.png").convert("RGB")
passphrase = None
for y in range(image.height):
    bits = [image.getpixel((x, y))[2] & 1 for x in range(image.width)]
    row = bytes(
        sum(bits[i + j] << (7 - j) for j in range(8))
        for i in range(0, len(bits) - 7, 8)
    )
    match = re.search(rb"STEGHIDE PASSPHRASE: ([A-Za-z0-9_-]+)", row)
    if match:
        passphrase = match.group(1).decode()
        break
if passphrase is None:
    raise RuntimeError("Steghide passphrase not found")

# PNG is losslessly converted to a steghide-supported carrier format.
run("magick", "image-0010.png", "BMP3:chart.bmp")
run("steghide", "extract", "-sf", "chart.bmp", "-p", passphrase, "-f")

blob = Path("encrypted_flag.bin").read_bytes()
flag = bytes(value ^ xor_key[i % len(xor_key)] for i, value in enumerate(blob))
print(flag.decode())
