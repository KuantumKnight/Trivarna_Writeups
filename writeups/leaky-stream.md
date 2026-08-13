# Leaky Stream

Challenge Name: Leaky Stream
Platform: CSEMA / Trivarna
Category: Crypto
Difficulty: Easy
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Decrypt a ciphertext produced by XORing the output of two 16/17-bit LFSRs. The expected result is a CTF flag.

## 2) Key Clues

- `cipher_spec.json` defines two maximal-length LFSRs and the tap positions.
- `export.bin` contains the XOR-combined ciphertext.
- The plaintext has a known flag header.

## 3) Plan

- Recover the keystream from the known plaintext prefix.
- Separate the combined stream into the two LFSR sequences.
- Reconstruct both registers, decrypt, and verify the seeds.

## 4) Steps

1. **Action:** Read the cipher specification and ciphertext.

   **Result:** The stream was the plain XOR of a 16-bit and a 17-bit LFSR output.

2. **Action:** XOR the ciphertext prefix with the expected `CSEMA{` header.

   **Result:** This exposed enough keystream bits to solve the two-register recurrence.

3. **Action:** Fit the standard tap positions and validate the state transitions.

   **Result:** The seeds were `0xACE1` and `0x1B4F7`.

4. **Action:** Generate the full combined keystream and XOR it with `export.bin`.

   **Result:** The complete plaintext was a valid flag.

## 5) Solution Summary

Although the two LFSRs were combined, the known flag prefix leaked the initial keystream. The recurrence constraints then separated the two sequences and recovered their seeds. Once the states were known, decryption was a simple XOR.

## 6) Flag

```text
CSEMA{xor_c0mb1n3d_lfsrs_4r3_st1ll_l1n34r}
```

## 7) Lessons Learned

- Known plaintext is powerful against linear stream generators.
- XORing two weak generators does not automatically make a strong generator.
- Verify recovered LFSR states on bytes beyond the known prefix.
