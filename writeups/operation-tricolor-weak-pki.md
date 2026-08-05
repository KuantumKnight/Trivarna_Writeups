# Operation Tricolor: The Weak PKI

Challenge Name: Operation Tricolor: The Weak PKI
Platform: CSEMA / Trivarna
Category: Crypto
Difficulty: Medium
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Recover the plaintext from a suspicious RSA record in the PKI audit data. Success means obtaining the complete `flag{...}` value from the supplied public parameters and ciphertext.

## 2) Key Clues

- `rsa_pubkeys_audit.conf` contains an RSA public key and ciphertext.
- The public exponent is unusually small: `e = 3`.
- The encryption is textbook RSA with no padding.
- The plaintext is short enough that `m^3` may never reach the modulus.

## 3) Plan

- Inspect the RSA parameters rather than treating the large modulus as automatically secure.
- Test whether the ciphertext is an exact integer cube.
- Convert the cube root back to bytes and verify the result.

## 4) Steps

1. **Action:** Locate the suspicious record.

   **Result:** The audit entry showed `e = 3`, no padding, and a short ciphertext.

   **Decision:** This is the classic low-exponent/small-message RSA case.

2. **Action:** Compute the exact integer cube root.

   ```python
   from sympy import integer_nthroot

   m, exact = integer_nthroot(ciphertext, 3)
   assert exact and m ** 3 == ciphertext
   plaintext = m.to_bytes((m.bit_length() + 7) // 8, "big")
   print(plaintext.decode())
   ```

   **Result:** The root was exact, proving the ciphertext had not wrapped modulo `n`.

3. **Action:** Verify the decoded bytes match the expected flag syntax.

   **Result:** The output was a single coherent flag.

## 5) Solution Summary

Textbook RSA is only safe when modular reduction and proper padding provide the intended security properties. Here the message was short and `e = 3`, so `c = m^3 mod n` was simply `m^3`. Taking the exact cube root recovered the message without factoring the modulus.

## 6) Flag

```text
flag{rsa_small_exponent_cube_root_attack_2026}
```

## 7) Lessons Learned

- Always inspect RSA exponent, padding, and message size before attempting factorization.
- An exact integer root is a strong validation signal.
- Never use textbook RSA for real data; use a standardized padded scheme such as OAEP.
