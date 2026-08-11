# Intercepted Independence Activation SMS

Challenge Name: Intercepted Independence Activation SMS
Platform: CSEMA / Trivarna
Category: Crypto
Difficulty: Easy
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Recover the plaintext of a suspicious SMS protected by a historical cipher stack. The final plaintext is the flag.

## 2) Key Clues

- `gsm_7bit_intercept.conf` identifies the MSISDN, cipher stack, and Vigenère key.
- The stack is `ROT13_THEN_VIGENERE`.
- Key: `JIOKEY`.
- The ciphertext is in `sms_gateway_routing.log`.

## 3) Plan

- Isolate the SMS associated with `+919876543210`.
- Undo the last encryption step first: Vigenère.
- Apply ROT13 to the intermediate plaintext.

## 4) Steps

1. **Action:** Correlate the configuration and routing log.

   **Result:** The relevant ciphertext was:

   ```text
   bgbd{jxo_ker_izp13_qjdvyamf_qvwaxpj_zypzszvap_2026}
   ```

2. **Action:** Vigenère-decrypt alphabetic characters with the repeating key `JIOKEY`.

   **Result:** The intermediate text became:

   ```text
   synt{fzf_cqh_ebg13_ivtrarer_gryrpbz_vagreprcg_2026}
   ```

3. **Action:** Apply ROT13.

   **Result:** The plaintext became the final flag.

4. **Action:** Re-encrypt the recovered text in the documented order.

   **Result:** It reproduced the captured ciphertext exactly.

## 5) Solution Summary

The important detail was the order of operations. Since the message was encrypted with ROT13 and then Vigenère, decryption had to use Vigenère first and ROT13 second. Re-encryption provided a complete correctness check.

## 6) Flag

```text
flag{sms_pdu_rot13_vigenere_telecom_intercept_2026}
```

## 7) Lessons Learned

- Reverse a cipher stack from the outside inward.
- Use metadata/configuration files to recover keys and algorithm order.
- Always verify by re-encrypting the recovered plaintext.
