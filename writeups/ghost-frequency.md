# Ghost Frequency

Challenge Name: Ghost Frequency
Platform: CSEMA / Trivarna
Category: Forensics / Audio
Difficulty: Easy
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Decode a flag from a WAV generated in fixed-size spectral blocks.

## 2) Key Clues

- The WAV is mono, 8000 Hz, and divides into 1024-sample blocks.
- Every block contains a 500 Hz reference tone.
- An amplitude-based channel produces a readable but intentional decoy.
- The meaningful bit is encoded in the phase of the 500 Hz bin.

## 3) Plan

- Split the audio into exact 1024-sample blocks.
- Compute an FFT for each block.
- Read the phase of the 500 Hz coefficient and group bits into bytes.

## 4) Steps

1. **Action:** Inspect the WAV format and calculate `8000 / 1024` bin spacing.

   **Result:** 500 Hz lands on an exact FFT bin, making block-by-block analysis stable.

2. **Action:** For every block, compute the FFT and inspect the 500 Hz phase.

   **Result:** Phase near `0` represented `0`; phase near `π` represented `1`.

3. **Action:** Group the bits into bytes and decode as ASCII.

   **Result:** A complete flag appeared.

4. **Action:** Compare with the amplitude channel.

   **Result:** The amplitude result `CSEMA{n07_h3r3_k33p_l1sn1ng}` was the decoy; phase was the intended channel.

## 5) Solution Summary

The signal carried information in phase, not simply in whether a tone was loud. Fixed block size and an exact reference frequency made the phase bitstream recoverable with a short FFT script.

## 6) Flag

```text
CSEMA{ph4s3_h1d3s_wh4t_4mpl1tud3_sh0ws}
```

## 7) Lessons Learned

- Analyze amplitude, frequency, and phase independently.
- Exact block/bin alignment is often an intentional clue.
- A readable first result may be a planted decoy in signal challenges.
