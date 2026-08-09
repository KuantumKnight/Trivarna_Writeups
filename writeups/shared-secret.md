# Shared Secret

Challenge Name: Shared Secret
Platform: CSEMA / Trivarna
Category: Crypto
Difficulty: Medium
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Decrypt the RSA ciphertexts and recover the flag from two public keys that accidentally share a prime factor.

## 2) Key Clues

- `pubkey1.txt` and `pubkey2.txt` contain two RSA moduli.
- The challenge states that both moduli share prime `p`.
- `ciphertext1.txt` and `ciphertext2.txt` contain the encrypted messages.

## 3) Plan

- Compute `gcd(n1, n2)` to recover the shared prime.
- Derive each private exponent from the factored modulus.
- Decrypt the ciphertext and check the plaintext.

## 4) Steps

1. **Action:** Parse `n`, `e`, and `c` from both key/ciphertext files.

2. **Action:** Compute the common factor.

   ```python
   from math import gcd
   p = gcd(n1, n2)
   assert 1 < p < n1 and n1 % p == 0
   q1, q2 = n1 // p, n2 // p
   ```

   **Result:** Both moduli factored immediately.

3. **Action:** Compute `phi(n)` and `d = e^-1 mod phi(n)` for the relevant key.

4. **Action:** Decrypt with `pow(c, d, n)` and convert the integer to bytes.

   **Result:** The bytes formed the final flag.

## 5) Solution Summary

RSA security depends on the difficulty of factoring each modulus. Reusing a prime across two moduli defeats that assumption because a single inexpensive GCD exposes the factorization.

## 6) Flag

```text
CSEMA{gcd_br34ks_wh4t_2048_b1ts_pr0t3ct}
```

## 7) Lessons Learned

- Compute pairwise GCDs when multiple RSA moduli are available.
- Shared-prime failures are cheaper to test than general factorization.
- Convert decrypted integers carefully, preserving leading-zero handling when needed.
