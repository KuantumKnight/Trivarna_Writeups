# U - Independence Secret

Challenge Name: U - Independence Secret
Platform: UNI6CTF / Trivarna
Category: Steganography / Forensics
Difficulty: Hard
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Recover three flag fragments hidden across a QR/image chain and concatenate them into the final Independence Day flag.

## 2) Key Clues

- The first QR leads to `image1.png`.
- Low-contrast text gives the beginning of the flag.
- Blue-channel LSB data contains the next URL.
- The chain includes Base62, steghide, ROT8000, URL decoding, PNG LSB extraction, and ROT47.
- Repeated metadata flag text is an explicit decoy.

## 3) Plan

- Decode the first image visually and inspect its channels.
- Follow each link while preserving file formats and hidden data.
- Decode each fragment independently, then concatenate only at the end.

## 4) Steps

1. **Action:** Increase contrast in the lower-right of `image1.png`.

   **Result:** Part 1 was `UNI6CTF{Y1s`.

2. **Action:** Extract the blue-channel LSB stream.

   **Result:** It yielded `https://bit.ly/trivarna2026`, which led to the next image.

3. **Action:** Decode the long text stage as Base62.

   **Result:** It produced a Google Drive URL for `image4.bin`.

4. **Action:** Treat `image4.bin` as a JPEG and extract its steghide payload.

   ```bash
   steghide extract -sf image4.bin -p Unrecognized -xf payload.txt
   ```

   **Result:** The payload contained Part 2 encoded with ROT8000 and a doubly URL-encoded link to the final PNG.

5. **Action:** Decode the final PNG’s LSB payload and apply ROT47.

   **Result:** Part 3 was recovered. Concatenating all three parts produced the flag.

## 5) Solution Summary

This was a chain-following steganography challenge. Each stage supplied enough information to locate the next layer, but decoy metadata was designed to make stopping early look plausible. The flag became valid only after all three independently decoded fragments were joined.

## 6) Flag

```text
UNI6CTF{Y1s_1nd4pe1enc6_S4cre1_0ut}
```

## 7) Lessons Learned

- Preserve lossless image data before extracting LSB payloads.
- Distinguish navigation clues from flag fragments.
- Keep exact spelling and leetspeak when joining fragments.
