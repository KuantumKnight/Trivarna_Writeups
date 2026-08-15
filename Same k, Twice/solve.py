#!/usr/bin/env python3
"""Solve the Same k, Twice challenge without an ECC library.

This implements the group law, scalar multiplication, ECDSA signing and
verification for secp256k1.  The challenge itself is solved by recovering the
private scalar from the two signatures that share a nonce.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


Point = tuple[int, int] | None


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int
    n: int
    g: Point

    def on_curve(self, q: Point) -> bool:
        if q is None:
            return True
        x, y = q
        return 0 <= x < self.p and 0 <= y < self.p and (y * y - x * x * x - self.a * x - self.b) % self.p == 0

    def add(self, q: Point, r: Point) -> Point:
        if q is None:
            return r
        if r is None:
            return q
        x1, y1 = q
        x2, y2 = r
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if q == r:
            if y1 % self.p == 0:
                return None
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p) % self.p
        else:
            slope = (y2 - y1) * pow((x2 - x1) % self.p, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        return x3, y3

    def mul(self, scalar: int, q: Point | None = None) -> Point:
        if q is None:
            q = self.g
        if scalar < 0:
            if q is None:
                return None
            q = (q[0], (-q[1]) % self.p)
            scalar = -scalar
        result: Point = None
        while scalar:
            if scalar & 1:
                result = self.add(result, q)
            q = self.add(q, q)
            scalar >>= 1
        return result

    def sign(self, private: int, message: bytes, nonce: int) -> tuple[int, int]:
        if not 1 <= private < self.n or not 1 <= nonce < self.n:
            raise ValueError("private key and nonce must be in [1, n)")
        r_point = self.mul(nonce)
        assert r_point is not None
        r = r_point[0] % self.n
        z = int.from_bytes(hashlib.sha256(message).digest(), "big")
        s = pow(nonce, -1, self.n) * (z + r * private) % self.n
        if r == 0 or s == 0:
            raise ValueError("invalid nonce produced r=0 or s=0")
        return r, s

    def verify(self, public: Point, message: bytes, signature: tuple[int, int]) -> bool:
        r, s = signature
        if public is None or not self.on_curve(public) or not (1 <= r < self.n and 1 <= s < self.n):
            return False
        z = int.from_bytes(hashlib.sha256(message).digest(), "big")
        w = pow(s, -1, self.n)
        point = self.add(self.mul(z * w), self.mul(r * w, public))
        return point is not None and point[0] % self.n == r


def recover_private(curve: Curve, first: dict, second: dict) -> tuple[int, int]:
    """Return (private, reused_nonce) from two signatures with equal r."""
    r1, s1 = int(first["r"], 16), int(first["s"], 16)
    r2, s2 = int(second["r"], 16), int(second["s"], 16)
    if r1 != r2:
        raise ValueError("signatures do not have the same r")
    z1 = int.from_bytes(hashlib.sha256(first["message"].encode()).digest(), "big")
    z2 = int.from_bytes(hashlib.sha256(second["message"].encode()).digest(), "big")
    k = (z1 - z2) * pow(s1 - s2, -1, curve.n) % curve.n
    private = (s1 * k - z1) * pow(r1, -1, curve.n) % curve.n
    if not (1 <= private < curve.n):
        raise ValueError("recovered scalar is out of range")
    return private, k


def main() -> None:
    bundle = json.loads(Path("auth_log_bundle.json").read_text())
    curve = Curve(
        p=int(bundle["P"], 16), a=bundle["A"], b=bundle["B"], n=int(bundle["N"], 16),
        g=tuple(int(v, 16) for v in bundle["G"]),
    )
    if not curve.on_curve(curve.g):
        raise ValueError("refusing to use a generator that is not on secp256k1")
    private, nonce = recover_private(curve, *bundle["signatures"])
    public = tuple(int(v, 16) for v in bundle["public_key"])
    if curve.mul(private) != public:
        raise ValueError("recovered private key does not match public key")
    for item in bundle["signatures"]:
        sig = int(item["r"], 16), int(item["s"], 16)
        assert curve.verify(public, item["message"].encode(), sig)
    challenge_nonce = int.from_bytes(
        hashlib.sha256(private.to_bytes(32, "big") + bundle["challenge_message"].encode()).digest(), "big"
    ) % curve.n
    print(f"private key: {private:064x}")
    print(f"reused nonce: {nonce:064x}")
    print(f"challenge nonce: {challenge_nonce:064x}")


if __name__ == "__main__":
    main()
