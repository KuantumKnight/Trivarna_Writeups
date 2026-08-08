# Same k, Twice

Challenge Name: Same k, Twice
Platform: CSEMA / Trivarna
Category: Crypto
Difficulty: Hard
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Recover the ECDSA private key from two signatures that reused the same nonce, then use the recovered key material to solve the challenge.

## 2) Key Clues

- `auth_log_bundle.json` contains two secp256k1 signatures.
- Both signatures have the same `r` value.
- The messages are different, so their hashes are different.
- The public key is supplied for verification.

## 3) Plan

- Confirm the repeated nonce condition through equal `r` values.
- Recover the nonce `k` and private scalar `d` algebraically.
- Verify `dG` equals the supplied public key and both signatures verify.

## 4) Steps

1. **Action:** Parse the two signatures and hash their messages with SHA-256.

   **Result:** `r1 == r2`, proving nonce reuse under the normal ECDSA assumptions.

2. **Action:** Apply the nonce-recovery equations modulo the curve order `n`:

   ```text
   k = (z1 - z2) / (s1 - s2) mod n
   d = (s1*k - z1) / r1 mod n
   ```

   **Result:** A candidate private scalar was recovered.

3. **Action:** Compute `dG` and verify both original signatures.

   **Result:** The derived public point matched the JSON public key and both signatures passed.

4. **Action:** Use the recovered scalar with the challenge message.

   **Result:** The challenge-specific value yielded the final flag.

## 5) Solution Summary

ECDSA requires a fresh unpredictable nonce for every signature. Reusing `k` makes the two signature equations subtract cleanly, eliminating the private key and allowing `k`, then `d`, to be solved directly. Public-key and signature verification made the result unambiguous.

## 6) Flag

```text
CSEMA{r3us3d_n0nc3_l34ks_pr1v4t3_k3y}
```

## 7) Lessons Learned

- Equal ECDSA `r` values across different messages are an immediate red flag.
- Perform all recovery arithmetic modulo the curve order.
- Always verify the recovered private key against the public key.
