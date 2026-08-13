# U - My First IOT

Challenge Name: U - My First IOT
Platform: UNI6CTF / Trivarna
Category: IoT / Forensics
Difficulty: Easy
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Inspect an IoT project archive whose ordinary text files are actually nested archives, then recover the final flag.

## 2) Key Clues

- Outer file: `my-first-iot.tgz`.
- The names `debug.log`, `README.txt`, and `config.txt` are misleading.
- Each extracted “text” file has a ZIP signature.
- The useful value appears after peeling the nested layers.

## 3) Plan

- List and extract the outer tarball without trusting extensions.
- Run `file` and `unzip -l` on each extracted item.
- Extract the nested payloads and search their decoded content.

## 4) Steps

1. **Action:** List `my-first-iot.tgz` and inspect its entries.

   **Result:** The archive contained the expected project files, but their contents were not ordinary logs/configuration.

2. **Action:** Extract the files and run `file` on them.

   **Result:** The files began with ZIP data despite their `.txt` names.

3. **Action:** Unpack each nested ZIP and inspect the resulting debug material.

   **Result:** A small encoded fragment was exposed.

4. **Action:** Decode the fragment and validate the output as the event’s flag format.

   **Result:** The flag was recovered.

## 5) Solution Summary

The challenge was an archive-recursion problem. File extensions were decoys; checking magic bytes and archive structure revealed the real layers. The final nested debug artifact contained the flag material.

## 6) Flag

```text
UNI6CTF{d3bug_l0gs_never_lie}
```

## 7) Lessons Learned

- Always use `file` or magic bytes instead of trusting extensions.
- Recursively inspect archives in forensic challenges.
- Keep intermediate extraction directories so the chain remains reproducible.
