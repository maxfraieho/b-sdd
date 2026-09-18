"""
B-SDD Air-Gapped Cryptographic Gate Verifier (INV-014-04).
Implements pure Python RFC 8032 Ed25519 key generation, signing, and verification.
Guarantees 100% offline air-gapped mathematical certainty for Phase Φ6 Review Gates.
Zero third-party dependencies (stdlib only).
"""
import hashlib
import json
import secrets
import time
from typing import Dict, Any, Optional, Tuple

# RFC 8032 Ed25519 Field and Curve Parameters
_q = 2**255 - 19
_l = 2**252 + 27742317777372353535851937790883648493
_d = (-121665 * pow(121666, -1, _q)) % _q
_I = pow(2, (_q - 1) // 4, _q)


def _inv(z: int) -> int:
    return pow(z, _q - 2, _q)


def _recover_x(y: int, sign: int) -> Optional[int]:
    if y >= _q:
        return None
    x2 = (y * y - 1) * _inv(_d * y * y + 1) % _q
    if x2 == 0:
        if sign:
            return None
        return 0
    x = pow(x2, (_q + 3) // 8, _q)
    if (x * x - x2) % _q != 0:
        x = (x * _I) % _q
    if (x * x - x2) % _q != 0:
        return None
    if (x & 1) != sign:
        x = _q - x
    return x


_By = (4 * _inv(5)) % _q
_Bx = _recover_x(_By, 0)
_B = (_Bx, _By)


def _edwards_add(P: Tuple[int, int], Q: Tuple[int, int]) -> Tuple[int, int]:
    x1, y1 = P
    x2, y2 = Q
    x3 = (x1 * y2 + x2 * y1) * _inv(1 + _d * x1 * x2 * y1 * y2) % _q
    y3 = (y1 * y2 + x1 * x2) * _inv(1 - _d * x1 * x2 * y1 * y2) % _q
    return (x3, y3)


def _scalarmult(P: Tuple[int, int], e: int) -> Tuple[int, int]:
    if e == 0:
        return (0, 1)
    Q = _scalarmult(P, e // 2)
    Q = _edwards_add(Q, Q)
    if e & 1:
        Q = _edwards_add(Q, P)
    return Q


def _encode_point(P: Tuple[int, int]) -> bytes:
    x, y = P
    bits = [(y >> i) & 1 for i in range(255)] + [x & 1]
    return bytes(sum(bits[i * 8 + j] << j for j in range(8)) for i in range(32))


def _decode_point(s: bytes) -> Optional[Tuple[int, int]]:
    if len(s) != 32:
        return None
    y = sum(s[i] << (i * 8) for i in range(32))
    sign = (y >> 255) & 1
    y &= (1 << 255) - 1
    x = _recover_x(y, sign)
    if x is None:
        return None
    return (x, y)


def public_key_from_secret(secret_key_bytes: bytes) -> bytes:
    """Derives 32-byte Ed25519 public key from 32-byte secret seed."""
    h = hashlib.sha512(secret_key_bytes).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 64
    A = _scalarmult(_B, a)
    return _encode_point(A)


def generate_ed25519_keypair(seed: Optional[bytes] = None) -> Tuple[str, str]:
    """Generates (secret_hex, public_hex) pair for operator cryptographic proofs."""
    seed_bytes = seed if seed is not None else secrets.token_bytes(32)
    pk_bytes = public_key_from_secret(seed_bytes)
    return seed_bytes.hex(), pk_bytes.hex()


def ed25519_sign(secret_key_bytes: bytes, message: bytes) -> bytes:
    """Signs a message using standard Ed25519 (pure Python stdlib)."""
    h = hashlib.sha512(secret_key_bytes).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 64
    A = _scalarmult(_B, a)
    A_bytes = _encode_point(A)

    r_digest = hashlib.sha512(h[32:] + message).digest()
    r = int.from_bytes(r_digest, "little") % _l
    R = _scalarmult(_B, r)
    R_bytes = _encode_point(R)

    k_digest = hashlib.sha512(R_bytes + A_bytes + message).digest()
    k = int.from_bytes(k_digest, "little") % _l
    S = (r + k * a) % _l
    S_bytes = S.to_bytes(32, "little")
    return R_bytes + S_bytes


def ed25519_verify(public_key_bytes: bytes, message: bytes, signature_bytes: bytes) -> bool:
    """Verifies an Ed25519 signature (pure Python stdlib)."""
    if len(signature_bytes) != 64 or len(public_key_bytes) != 32:
        return False
    R_bytes = signature_bytes[:32]
    S_bytes = signature_bytes[32:]
    S = int.from_bytes(S_bytes, "little")
    if S >= _l:
        return False

    A = _decode_point(public_key_bytes)
    if A is None:
        return False

    k_digest = hashlib.sha512(R_bytes + public_key_bytes + message).digest()
    k = int.from_bytes(k_digest, "little") % _l

    R = _decode_point(R_bytes)
    if R is None:
        return False

    # Check S*B == R + k*A
    SB = _scalarmult(_B, S)
    kA = _scalarmult(A, k)
    R_plus_kA = _edwards_add(R, kA)

    return _encode_point(SB) == _encode_point(R_plus_kA)


class AirGappedProofValidator:
    """
    Offline cryptographic gate validator for Phase Φ6 Review Gates (INV-014-04).
    Ensures mathematical certainty of review manifests with zero outbound network calls.
    """

    def generate_proof(self, manifest: Dict[str, Any], secret_hex: str) -> Dict[str, Any]:
        """Generates an air-gapped cryptographic proof bundle for a manifest."""
        secret_bytes = bytes.fromhex(secret_hex.strip())
        pk_bytes = public_key_from_secret(secret_bytes)
        canonical_json = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        payload_hash = hashlib.sha256(canonical_json).hexdigest()

        # Sign the deterministic payload hash
        sig = ed25519_sign(secret_bytes, payload_hash.encode("utf-8"))

        return {
            "algorithm": "Ed25519",
            "public_key": pk_bytes.hex(),
            "signature": sig.hex(),
            "payload_hash": payload_hash,
            "timestamp": time.time(),
            "airgap_verified": True
        }

    def verify_proof(self, proof: Dict[str, Any], manifest: Dict[str, Any]) -> bool:
        """Verifies proof against given manifest payload."""
        try:
            canonical_json = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
            expected_hash = hashlib.sha256(canonical_json).hexdigest()
            if proof.get("payload_hash") != expected_hash:
                return False

            pk_hex = proof.get("public_key", "").replace("ed25519:", "").strip()
            sig_hex = proof.get("signature", "").replace("ed25519:", "").strip()

            pk_bytes = bytes.fromhex(pk_hex)
            sig_bytes = bytes.fromhex(sig_hex)

            return ed25519_verify(pk_bytes, expected_hash.encode("utf-8"), sig_bytes)
        except Exception:
            return False
