---
title: "U - Operation Quiet Ledger"
ctf: "UNI6CTF (event 47)"
date: 2026-08-15
category: forensics
difficulty: medium
points: 300
flag_format: "UNI6CTF{...}"
author: "Trivarna"
---

# U - Operation Quiet Ledger

## Summary

The encrypted PDF uses near-miss password candidates, a blue-channel LSB clue in its chart, a steghide payload, and a metadata-derived repeating XOR key.

## Solution

### Step 1: Open the PDF and recover the steghide clue

Combining the name and year portions of the supplied password candidates produces the valid PDF password `Knightshift_2025`. Object 2 contains the keyword `NGIzZTkxZDI3NzBh`, whose base64-decoded value is the hex key `4b3e91d2770a`.

The PDF's chart is object 10. Its bottom-row blue-channel LSBs decode to:

```text
CHECK STEGHIDE PASSPHRASE: nightshift
```

Converting the lossless PNG extraction to BMP preserves the pixel payload. Steghide then extracts `encrypted_flag.bin`.

### Step 2: Decode the final payload

The complete solver is in `solve.py`. Its final operation hex-decodes the metadata key and repeats it across the extracted blob with XOR:

```bash
python3 solve.py
```

Output:

```text
UNI6CTF{m3t4d4t4_wh1sp3rs_wh1l3_p1x3ls_h1d3}
```

Tools used: MuPDF `mutool`, ImageMagick, steghide, and Pillow.

## Flag

```text
UNI6CTF{m3t4d4t4_wh1sp3rs_wh1l3_p1x3ls_h1d3}
```
