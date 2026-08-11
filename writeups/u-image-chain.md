# U - Image Chain

Challenge Name: U - Image Chain
Platform: UNI6CTF / Trivarna
Category: Crypto / OSINT
Difficulty: Hard
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Decode the obfuscated URL, follow the resulting public form/image chain, and recover the final flag.

## 2) Key Clues

- The supplied text is a URL-like string with letters substituted.
- The scheme and host become recognizable under Atbash.
- The resolved Google Form is the next step rather than the final answer.

## 3) Plan

- Apply Atbash to the entire string.
- Preserve the short-code exactly after decoding the URL.
- Follow the form response and record the final flag.

## 4) Steps

1. **Action:** Apply `A↔Z` and `a↔z` to:

   ```text
   sggkh://ulinh.tov/h9UACJvFWtiZecK26
   ```

   **Result:** The text became a Google Forms URL.

2. **Action:** Open the resolved form and inspect its chained response.

   **Result:** The form supplied the final flag-shaped value.

3. **Action:** Preserve the exact capitalization and leetspeak.

   **Result:** The submitted flag matched the challenge output.

## 5) Solution Summary

The first layer was a simple Atbash substitution disguised as a malformed URL. Once the URL was restored, the public form supplied the remaining data; no brute force or image processing was needed.

## 6) Flag

```text
UNI6CTF{Y0u_m5s1e7_im5g2_c1p8e7s}
```

## 7) Lessons Learned

- URL-looking ciphertext is a good candidate for alphabet substitutions.
- Decode the URL before guessing what the destination contains.
- Keep exact case and intentional leetspeak in flags.
