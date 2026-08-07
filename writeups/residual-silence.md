# Residual Silence

Challenge Name: Residual Silence
Platform: UNI6CTF / Trivarna
Category: Forensics / Crypto
Difficulty: Medium
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Recover a flag hidden across noisy key fragments, nested encrypted archives, and trailing data in image files.

## 2) Key Clues

- `key1.txt` through `key7.txt` and `halfkey.txt` are Base64 fragments.
- The outer archive contains an encrypted `secret.7z`.
- The 7z payload contains an encrypted `secret.rar`.
- The final useful data is appended to one of the extracted JPEGs.

## 3) Plan

- Decode all key fragments and test which candidate validates the archive.
- Extract the nested RAR and inspect every image for appended bytes.
- Reassemble and Base64-decode the final hidden fragment.

## 4) Steps

1. **Action:** Decode and compare the fragments.

   **Result:** `key6.txt` supplied the valid password for the encrypted archive.

2. **Action:** Extract `secret.rar` from `secret.7z` and use the same password for the RAR.

   **Result:** Seven JPEGs were recovered; the RAR verifier confirmed the password.

3. **Action:** Inspect file sizes and trailing data after the JPEG end markers.

   **Result:** One image contained a complete Base64 fragment while other visible strings were decoys.

4. **Action:** Decode the complete fragment and assemble the flag.

   **Result:** The final output matched the expected `UNI6{...}` wrapper.

## 5) Solution Summary

The challenge used several layers of misleading fragmentation. The correct key was selected by archive validation, not by appearance. Once the nested archive was extracted, the real payload was outside the normal JPEG image data.

## 6) Flag

```text
UNI6{dalbir_singh_suhag_arup_raha_sunil_lanba_uri_surgical_strike}
```

## 7) Lessons Learned

- Validate candidate passwords against the encrypted container.
- Inspect bytes after expected file end markers.
- Do not assume every fragment contributes equally; some are deliberate noise.
