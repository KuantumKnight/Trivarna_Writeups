# U - Echoes of Freedom

Challenge Name: U - Echoes of Freedom
Platform: UNI6CTF / Trivarna
Category: Forensics / Audio
Difficulty: Hard
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Decode three audio files, combine their outputs to unlock a second archive, and recover the real flag from the final audio file.

## 2) Key Clues

- `Part1.wav`, `Part2.wav`, and `Part3.wav` each provide one password component.
- The readme says the three parts combine to open `challenge.zip`.
- The final MP3 contains both visible metadata decoys and a private ID3 field.

## 3) Plan

- Use the signal type suggested by each audio file: Morse, DTMF, and spectrogram.
- Test the combined password against the inner ZIP.
- Inspect private metadata, not only the normal title/comment fields.

## 4) Steps

1. **Action:** Decode `Part1.wav` as Morse.

   **Result:** `INDIA`.

2. **Action:** Decode the DTMF sequence in `Part2.wav`.

   **Result:** The apparent 56 digits were concatenated frequency values. Pairing them into DTMF tones produced `19472026`.

3. **Action:** Inspect `Part3.wav` with a spectrogram.

   **Result:** `Freedom`.

4. **Action:** Join the parts and open the inner archive.

   ```text
   INDIA19472026Freedom
   ```

   **Result:** `audio.mp3` and `backup.txt` were extracted.

5. **Action:** Inspect the MP3’s private `WM/Mood` ID3 frame and ROT13-decode its UTF-16 text.

   **Result:** This exposed the real flag. The normal title/comment/subtitle produced `UNI6CTF{Fre3_1nd1a_2026}`, which was a decoy.

## 5) Solution Summary

The archive password was a three-part audio chain. The second part itself had a second DTMF layer, and the final flag was hidden in private metadata rather than ordinary ID3 fields. Separating signal content from decoy metadata was the key decision.

## 6) Flag

```text
UNI6CTF{fre4domaud1ocra3kedin2026}
```

## 7) Lessons Learned

- Use spectrograms and metadata together when analyzing audio challenges.
- DTMF digits may themselves encode frequencies or another numeric layer.
- Do not trust the first readable flag-shaped metadata value.
