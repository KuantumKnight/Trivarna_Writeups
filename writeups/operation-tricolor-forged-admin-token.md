# Operation Tricolor: The Forged Admin Token

Challenge Name: Operation Tricolor: The Forged Admin Token
Platform: CSEMA / Trivarna
Category: Web / Crypto
Difficulty: Easy
Time spent: Not recorded; reconstructed from the solve chat

## 1) Goal

Forge an authentication token that the portal accepts as an administrator, then recover the flag from the admin response.

## 2) Key Clues

- `auth_service_schema.json` documents JWT validation behavior.
- The accepted algorithm list includes `none`.
- The role is read from the JWT payload.
- An unsigned JWT still has the final separator, so its signature component is empty.

## 3) Plan

- Decode the example token and inspect the header/payload fields.
- Create a payload with the required administrator identity.
- Send a token with `alg: none` and an empty signature.

## 4) Steps

1. **Action:** Read the schema and identify the algorithm confusion weakness.

   **Result:** The service accepted unsigned JWTs when the header declared `alg: none`.

2. **Action:** Build the header and payload.

   ```json
   {"alg":"none","typ":"JWT"}
   {"sub":"sysadmin","role":"admin"}
   ```

   Base64url-encode both JSON objects and join them as `header.payload.`.

   **Result:** The token had no cryptographic signature, but matched the parser’s expected format.

3. **Action:** Submit the forged token to the admin endpoint.

   **Result:** The portal treated the request as an administrator request and returned the flag.

## 5) Solution Summary

The server trusted attacker-controlled JWT algorithm and claims. Declaring `alg: none` disabled signature verification, while the forged `role: admin` claim satisfied authorization. The trailing dot represented the empty signature field.

## 6) Flag

```text
flag{jwt_alg_none_weak_hmac_bypassed_2026}
```

## 7) Lessons Learned

- Never let a token choose whether its own signature is verified.
- Authorization claims must be trusted only after authenticating the token.
- Inspect JWT headers and validation configuration before trying password attacks.
