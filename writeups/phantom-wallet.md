# PHANTOM WALLET

Challenge Name: PHANTOM WALLET
Platform: UNI6CTF / Trivarna
Category: Android / Crypto / Web
Difficulty: Hard
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Reverse the Android wallet protocol, reproduce its signed API requests, complete the intended workflow, and unlock the recovery endpoint.

## 2) Key Clues

- APK: `phantom-wallet.apk`.
- Native library: `libphantomcore.so`.
- API endpoints include challenge, session registration, wallet balance, transactions, 2FA, and recovery.
- Requests use custom `X-Phantom-*` headers and HMAC-SHA256.
- The UI order matters: wallet → transactions → 2FA → recovery.

## 3) Plan

- Decompile the APK and inspect the native key-derivation path.
- Build a small JNI harness to reproduce the native function.
- Script the signed session and decrypt each returned fragment.

## 4) Steps

1. **Action:** Inspect the manifest, DEX code, native exports, and server routes.

   **Result:** The protocol and canonical signing strings were recovered.

2. **Action:** Derive the session key from the certificate digest and server challenge.

   **Result:** The native harness reproduced the key expected by the backend.

3. **Action:** Register a session with HMAC-signed newline-delimited fields.

   **Result:** The server returned a session ID, nonce, encrypted fragments, and a counter.

4. **Action:** Call endpoints in the required order and decrypt each fragment with the per-stage HMAC stream.

   **Result:** Balance, transaction, and security fragments were recovered.

5. **Action:** Generate the TOTP from the epoch-derived HMAC value, then hash the concatenated fragments for the recovery proof.

   **Result:** `/recovery/unlock` accepted the proof and returned the flag.

## 5) Solution Summary

The app’s cryptography was custom but deterministic. Reimplementing the native derivation and exact header canonicalization was enough to create a valid session. The final trap was calling 2FA before the application’s expected stage order; the backend required the UI sequence.

## 6) Flag

```text
PHANTOM{easyrh_48j4fl_x3zvgh_jx8hwg}
```

## 7) Lessons Learned

- Android challenges often require examining both managed and native code.
- Exact request canonicalization and counters are part of the protocol.
- Reproduce state-machine order before looking for an authorization bypass.
