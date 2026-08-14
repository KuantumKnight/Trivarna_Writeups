# U - New Destiny

Challenge Name: U - New Destiny
Platform: UNI6CTF / Trivarna
Category: Reversing / Crypto
Difficulty: Medium
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Reverse the password verifier in `verifier.blob`, recover the accepted input, and run the verifier to obtain the flag.

## 2) Key Clues

- The blob is layered rather than a native executable.
- The verifier uses a generated 3×3 matrix and a permutation modulo 257.
- The accepted input is 21 uppercase characters.

## 3) Plan

- Unwrap every compression/encoding layer.
- Read the verifier’s transform in the forward direction.
- Invert the permutation and matrix, then validate by executing the verifier.

## 4) Steps

1. **Action:** Unwrap `verifier.blob`.

   **Result:** The chain was `base64 → xz → bzip2 → gzip → verifier.js`.

2. **Action:** Model the matrix multiplication and permutation modulo 257.

   **Result:** Reversing the permutation and applying the inverse matrix produced:

   ```text
   TRYSTWITHDESTINY1947X
   ```

3. **Action:** Run the recovered input through the JavaScript verifier.

   **Result:** It printed `ACCESS GRANTED` followed by the flag.

## 5) Solution Summary

The verifier was reversible because its matrix and permutation were deterministic and operated modulo a known value. Inverting those operations transformed the target output back into the required password; the verifier itself was the final oracle.

## 6) Flag

```text
UNI6CTF{SaRe_Jahan#1947_xYz!}
```

## 7) Lessons Learned

- Layered compression should be peeled one format at a time.
- Matrix/permutation checks are often easier to invert than brute-force.
- Always validate a recovered password by running the original verifier.
