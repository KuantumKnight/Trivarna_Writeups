---
title: "U - Independence Secret"
ctf: "Trivarna"
date: 2026-08-15
category: forensics
difficulty: hard
points: 450
flag_format: "UNI6CTF{...}"
author: "Solver"
---

# U - Independence Secret

## Summary

Follow a QR/Drive chain, ignore the prompt-injection decoy, and combine three fragments recovered through low-contrast text, Base62, steghide, ROT8000, URL decoding, PNG LSB extraction, and ROT47.

## Solution

### Step 1: Recover Part 1 and follow the image chain

The first custom QR resolves to `image1.png`. Increasing contrast in its lower-right corner reveals `UNI6CTF{Y1s`. Its blue-channel LSB contains `https://bit.ly/trivarna2026`, leading to the next QR. The repeated metadata value `UNI6CTF{th1s_1s_4_d3c0y}` is explicitly a decoy.

The text stage contains a 112-character Base62 value. Decoding it with the standard `0-9A-Za-z` alphabet gives the Drive URL for `image4.bin`, which is actually a JPEG. The supplied MD5 password hash cracks with John the Ripper's `best64` rules:

```bash
printf '%s\n' 7f5f743ac34344aeb26849015b4b3dae > hash.txt
john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt --rules=best64 hash.txt
# Unrecognized
steghide extract -sf image4.bin -p Unrecognized -xf payload.txt
```

### Step 2: Decode Parts 2 and 3

This compact script decodes the two machine-readable fragments and prints the final flag. The last PNG is the file at the doubly URL-encoded Drive link in `payload.txt`.

```python
from pathlib import Path
from urllib.parse import unquote
import subprocess

part1 = "UNI6CTF{Y1s"  # low-contrast text in image1.png

lines = Path("payload.txt").read_text().splitlines()
rot8000 = lines[0].split(": ", 1)[1]
part2 = "".join(chr(ord(c) - 31753) if c != " " else c for c in rot8000)

url = unquote(unquote(lines[-1]))
print("Final Drive URL:", url)

# Save the final downloaded PNG as final.png.
hidden = subprocess.check_output(
    ["zsteg", "-E", "b1,b,lsb,xy", "final.png"]
).split(b"\0", 1)[0].decode()
rot47 = "".join(
    chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c
    for c in hidden
)
part3 = rot47.split(": ", 1)[1]
print(part1 + part2 + part3)
```

Output:

```text
UNI6CTF{Y1s_1nd4pe1enc6_S4cre1_0ut}
```

## Flag

```text
UNI6CTF{Y1s_1nd4pe1enc6_S4cre1_0ut}
```
