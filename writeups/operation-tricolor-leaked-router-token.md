# Operation Tricolor: The Leaked Router Token

Challenge Name: Operation Tricolor: The Leaked Router Token
Platform: CSEMA / Trivarna
Category: Crypto
Difficulty: Easy
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Correlate a router configuration with the TACACS audit log and reverse the layered encoding to recover the hidden API token.

## 2) Key Clues

- Router file: `core_router_jio_sp.cfg`.
- Audit file: `tacacs_auth_audit.log`.
- Hostname: `JIO-CORE-RTR-01`.
- The audit describes `Base64 decode → XOR → Base64 decode`.

## 3) Plan

- Find the active hostname and the suspicious encoded value.
- Use the hostname as the repeating XOR key.
- Apply the transformations in reverse and validate the final text.

## 4) Steps

1. **Action:** Search the configuration and audit log for the relevant router record.

   **Result:** The hostname and a long Base64-looking token were linked by the same administrative session.

2. **Action:** Base64-decode the outer value.

   **Result:** The bytes were still encoded and did not form readable text.

3. **Action:** XOR the decoded bytes with the repeating key `JIO-CORE-RTR-01`.

   **Result:** The output became another Base64 string:

   ```text
   ZmxhZ3tjaXNjb190eXBlN19uZXN0ZWRfYmFzZTY0X3JvdXRlcl9sZWFrXzIwMjZ9
   ```

4. **Action:** Base64-decode the second layer.

   **Result:** The flag was recovered and matched the expected format.

## 5) Solution Summary

The protection was only layered encoding, not encryption. The audit log supplied the exact operation order and XOR key, while the router configuration supplied the ciphertext. Reversing those operations exposed the API token.

## 6) Flag

```text
flag{cisco_type7_nested_base64_router_leak_2026}
```

## 7) Lessons Learned

- Base64 is an encoding and should not be treated as encryption.
- Correlate configuration records with authentication logs before decoding blindly.
- When a log gives an operation order, reverse the order carefully during decryption.
