# Bring Your Own Keys

Challenge Name: Bring Your Own Keys
Platform: CSEMA / Trivarna
Category: Web / JWT
Difficulty: Medium
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Forge an administrator JWT accepted by the Vantage Cloud API and retrieve the protected flag endpoint.

## 2) Key Clues

- The verifier trusts the JWT `jku` header.
- The `kid` selects a key from the remote JWKS.
- The service does not restrict the JWKS origin.
- `solve.py` generates a matching RSA keypair and token.

## 3) Plan

- Generate an attacker-controlled RSA keypair.
- Publish its public key as a JWKS document at a URL accepted by the challenge.
- Sign an `RS256` token with `role: admin` and point `jku` to the JWKS.

## 4) Steps

1. **Action:** Generate a 2048-bit RSA keypair and construct a JWK containing `n`, `e`, `kid`, and `alg`.

2. **Action:** Host the JWKS through the base64 endpoint used by the supplied solver.

   **Result:** The verifier could fetch the attacker’s public key without a local server.

3. **Action:** Create the token header and payload:

   ```json
   {"alg":"RS256","typ":"JWT","jku":"<attacker JWKS URL>","kid":"attacker-key-1"}
   {"exp":<future time>,"role":"admin","sub":"alice"}
   ```

4. **Action:** Sign `base64url(header) + "." + base64url(payload)` with the private RSA key and request `/admin/flag`.

   **Result:** The server fetched the attacker key, verified the attacker signature, and accepted the administrator role.

## 5) Solution Summary

The server treated a token-controlled `jku` as trusted key infrastructure. That turned JWT verification into a key substitution attack: the attacker supplied both the signature and the public key used to verify it.

## 6) Flag

```text
FLAG{ux2j9u_skcesr_vc36js}
```

## 7) Lessons Learned

- Never allow arbitrary remote key URLs in JWT headers.
- Pin trusted JWKS origins and validate `kid` against a local key set.
- Check expiry and role only after signature verification with a trusted key.
