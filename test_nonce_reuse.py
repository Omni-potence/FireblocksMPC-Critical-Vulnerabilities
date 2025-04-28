#!/usr/bin/env python3
"""
Simplified test script for nonce reuse vulnerability in ECDSA.
"""

import hashlib
import random
from typing import Tuple

# ECDSA parameters for secp256k1
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G_X = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
G_Y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def mod_inverse(a: int, m: int) -> int:
    """Compute the modular inverse of a modulo m."""
    if a < 0:
        a = a % m
    
    # Extended Euclidean Algorithm
    old_r, r = a, m
    old_s, s = 1, 0
    old_t, t = 0, 1
    
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    
    # Check if gcd is 1
    if old_r != 1:
        raise ValueError(f"The modular inverse does not exist (gcd = {old_r})")
    
    return old_s % m

def sign_message(private_key: int, message: str, k: int = None) -> Tuple[int, int]:
    """Sign a message using ECDSA with a fixed nonce for demonstration."""
    # Hash the message
    z = int(hashlib.sha256(message.encode()).hexdigest(), 16) % N
    
    # Use a fixed nonce for demonstration
    if k is None:
        k = 42  # VULNERABLE: Using a fixed nonce
    
    # Calculate r (x-coordinate of k*G)
    r = pow(k * G_X, 1, N)
    
    # Calculate s = k^(-1) * (z + r*d) mod N
    s = (mod_inverse(k, N) * (z + r * private_key)) % N
    
    return (r, s)

def recover_private_key_from_nonce_reuse(message1: str, signature1: Tuple[int, int], 
                                         message2: str, signature2: Tuple[int, int]) -> int:
    """Recover the private key from two signatures that used the same nonce."""
    r1, s1 = signature1
    r2, s2 = signature2
    
    # Check that the signatures used the same nonce
    if r1 != r2:
        raise ValueError("The signatures did not use the same nonce")
    
    # Hash the messages
    z1 = int(hashlib.sha256(message1.encode()).hexdigest(), 16) % N
    z2 = int(hashlib.sha256(message2.encode()).hexdigest(), 16) % N
    
    # Calculate the private key
    s_diff = (s1 - s2) % N
    z_diff = (z1 - z2) % N
    k = (mod_inverse(s_diff, N) * z_diff) % N
    d = ((s1 * k - z1) * mod_inverse(r1, N)) % N
    
    return d

def main():
    # Generate a private key
    private_key = 12345  # For demonstration
    print(f"Original private key: {private_key}")
    
    # Sign two different messages with the same nonce
    message1 = "This is the first message"
    message2 = "This is the second message"
    
    # Use the same nonce (k) for both signatures
    k = 42
    signature1 = sign_message(private_key, message1, k)
    signature2 = sign_message(private_key, message2, k)
    
    print(f"Signature 1: r={signature1[0]}, s={signature1[1]}")
    print(f"Signature 2: r={signature2[0]}, s={signature2[1]}")
    
    # Recover the private key
    try:
        recovered_key = recover_private_key_from_nonce_reuse(message1, signature1, message2, signature2)
        print(f"Recovered private key: {recovered_key}")
        print(f"Private key recovery successful: {recovered_key == private_key}")
    except Exception as e:
        print(f"Error recovering private key: {e}")

if __name__ == "__main__":
    main()
