# U - Tiranga of freedom

Challenge Name: U - Tiranga of freedom
Platform: UNI6CTF / Trivarna
Category: Steganography / Misc
Difficulty: Medium
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Repair a terminal/image capture wrapped at the wrong width and read the hidden flag banner in the realigned output.

## 2) Key Clues

- `Challenge_misc.txt` is a ZIP archive despite its text extension.
- The image data is wrapped at the wrong geometry.
- The repaired image uses 128 columns and 45 rows.
- Several flag-shaped strings are decoys; the pixel banner is authoritative.

## 3) Plan

- Detect the archive from its magic bytes and extract the actual payload.
- Test plausible row widths and inspect the resulting bitmap.
- Use the geometry that reconstructs the Tiranga and gives a coherent five-row banner.

## 4) Steps

1. **Action:** Run `file` on `Challenge_misc.txt`.

   **Result:** It was a ZIP archive containing the real challenge material.

2. **Action:** Extract and realign the wrapped byte/pixel stream.

   **Result:** A `128 × 45` layout reconstructed the Indian tricolor cleanly.

3. **Action:** Read the banner rows in the repaired image.

   **Result:** The characters formed a complete `UNIGCTF{...}` string.

4. **Action:** Check the spelling against the rendered image rather than relying on OCR guesses.

   **Result:** The body was `r3sizing_7h3_indi4n_fl4g`.

## 5) Solution Summary

The payload was not encrypted; it was displayed with incorrect row geometry. Finding the correct width restored both the tricolor image and the text banner. The unusual `G` in `UNIGCTF` is part of the recovered challenge output and is preserved exactly.

## 6) Flag

```text
UNIGCTF{r3sizing_7h3_indi4n_fl4g}
```

## 7) Lessons Learned

- Check file signatures before trusting extensions.
- For wrapped terminal captures, test dimensions using visual coherence.
- Verify unusual flag prefixes exactly; do not silently normalize them.
