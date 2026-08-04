# U - Saffron Echoes in Old Delhi

Challenge Name: U - Saffron Echoes in Old Delhi
Platform: UNI6CTF / Trivarna
Category: Linux Forensics / Steganography
Difficulty: Medium
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Recover the authentic transfer record from a seized ext4 disk image containing overwritten files, steganographic decoys, and a final encrypted capsule.

## 2) Key Clues

- Disk label and mount path reference a ritual ledger.
- Four BMP scans can be carved from the image.
- The first-stage passphrase is `trishul-lantern-braid`.
- Notes and ritual words lead to `ghat-manjari-copper-owl` and the final AES key material.
- The visible `UNI6CTF{AR3_Y0U_U51NG...}` text is an AI-targeted decoy.

## 3) Plan

- Mount or inspect the ext4 image read-only and recover files/carved images.
- Extract the hidden payloads from the scans and separate decoys from the final capsule.
- Decrypt the authentic original message and preserve the event’s expected flag wrapper.

## 4) Steps

1. **Action:** Inspect the filesystem, deleted entries, and carved BMP files.

   **Result:** The image contained several encrypted ledgers and a separate final capsule.

2. **Action:** Use `trishul-lantern-braid` on the decoy capsules.

   **Result:** Their contents were explicitly marked as false ledgers; they were not the final message.

3. **Action:** Follow the notes and ritual word list to the final capsule passphrase `ghat-manjari-copper-owl`.

   **Result:** The final encrypted payload was recovered. Its AES-256-CBC parameters were recorded in the extracted notes, including salt `d83f0a1e5bc94762` and IV `7f01ea25d6c59f4b38e4d0b451ccae12`.

4. **Action:** Decrypt with the final key phrase `river-ink-oblation` and inspect the resulting message.

   **Result:** The authentic upstream message contained `kashiCTF{ledger_ashes_remember_every_ritual}`. For the Trivarna/UNI6CTF submission, the same body uses the event wrapper below.

## 5) Solution Summary

This challenge deliberately mixed a modified image, old challenge provenance, and AI-facing decoy flags. The reliable solve came from filesystem recovery and the authentic capsule, not from the visible `final_message.txt` decoy.

## 6) Flag

```text
UNI6CTF{ledger_ashes_remember_every_ritual}
```

## 7) Lessons Learned

- Preserve filesystem provenance and inspect deleted/unallocated data.
- Treat extracted “final” files as evidence, not authority, when the challenge plants decoys.
- Record which flag wrapper belongs to the current event before submitting.
