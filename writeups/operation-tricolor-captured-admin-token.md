# Operation Tricolor: The Captured Admin Token

Challenge Name: Operation Tricolor: The Captured Admin Token
Platform: CSEMA / Trivarna
Category: Crypto / Forensics
Difficulty: Easy
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Recover an administrative session token captured in proxy traffic and prove that the repeating-key protection is reversible.

## 2) Key Clues

- Ciphertext: `auth_proxy_traffic.log`.
- Correlated session record: `session_vault.json`.
- The implementation uses repeating-key XOR.
- Key: `PROXYKEY2026`.

## 3) Plan

- Locate the matching token and determine its length/key alignment.
- XOR each ciphertext byte with the repeating key.
- Validate the result against the session record and flag syntax.

## 4) Steps

1. **Action:** Inspect the proxy log around the administrative request.

   **Result:** A hex-encoded ciphertext was associated with the privileged session.

2. **Action:** Repeat `PROXYKEY2026` to the ciphertext length and XOR byte by byte.

   ```python
   ciphertext = bytes.fromhex("<captured hex>")
   key = b"PROXYKEY2026"
   plaintext = bytes(c ^ key[i % len(key)] for i, c in enumerate(ciphertext))
   print(plaintext.decode())
   ```

   **Result:** The output was readable and began with the expected flag wrapper.

3. **Action:** Compare the recovered credential with the matching vault entry.

   **Result:** The token and identity fields aligned, confirming the key and offset.

## 5) Solution Summary

Repeating-key XOR is vulnerable when the key is reused and the ciphertext is available. Once the key was identified, decryption was a direct modular repetition and XOR operation; no brute force was required.

## 6) Flag

```text
flag{xor_repeating_key_crib_drag_auth_proxy_2026}
```

## 7) Lessons Learned

- Reusing a short XOR key makes long captures vulnerable to crib dragging.
- Hex encoding does not add cryptographic protection.
- Correlating proxy and session logs prevents decrypting the wrong record.
