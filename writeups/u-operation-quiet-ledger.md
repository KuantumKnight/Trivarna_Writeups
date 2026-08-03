# U - Operation Quiet Ledger

Challenge Name: U - Operation Quiet Ledger
Platform: UNI6CTF / Trivarna
Category: Steganography / PDF
Difficulty: Medium
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Open the encrypted quarterly report, recover the hidden steghide payload, and decrypt the final flag blob using a key hidden in PDF metadata.

## 2) Key Clues

- `UNI6CTF_Quarterly_Report.pdf` is password-protected.
- The candidate list contains near-miss passwords.
- The chart image carries a blue-channel LSB message.
- PDF object metadata contains a Base64 value that becomes a hex XOR key.

## 3) Plan

- Combine the password-list fragments and test the PDF password.
- Inspect embedded objects and the chart’s pixel planes.
- Extract the steghide payload and XOR it with the decoded metadata key.

## 4) Steps

1. **Action:** Test the candidate combinations against the PDF.

   **Result:** `Knightshift_2025` opened the report.

2. **Action:** Inspect the embedded chart and read the blue-channel LSBs.

   **Result:** The footer said `CHECK STEGHIDE PASSPHRASE: nightshift`.

3. **Action:** Convert the lossless chart extraction to BMP and run steghide.

   ```bash
   steghide extract -sf chart.bmp -p nightshift -xf encrypted_flag.bin
   ```

   **Result:** `encrypted_flag.bin` was extracted.

4. **Action:** Read the PDF metadata value `NGIzZTkxZDI3NzBh`, Base64-decode it to `4b3e91d2770a`, and repeat those bytes across the payload.

   **Result:** XOR decryption produced a complete flag.

## 5) Solution Summary

The report used multiple independent layers: a near-miss password puzzle, pixel-level steganography, steghide, and a metadata-derived repeating XOR key. The important pivot was checking the embedded chart instead of stopping after opening the PDF.

## 6) Flag

```text
UNI6CTF{m3t4d4t4_wh1sp3rs_wh1l3_p1x3ls_h1d3}
```

## 7) Lessons Learned

- Preserve chart pixels exactly when extracting steganographic data.
- Near-miss password lists often encode the correct combination.
- PDF metadata can be an active data layer, not just descriptive information.
