"""
Generate RSA key pair for JWT signing (RS256).
Run once before first startup: python scripts/generate_keys.py
"""
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

KEYS_DIR = Path(__file__).parent.parent / "keys"
KEYS_DIR.mkdir(exist_ok=True)

private_path = KEYS_DIR / "private.pem"
public_path = KEYS_DIR / "public.pem"

if private_path.exists() or public_path.exists():
    print("Keys already exist. Delete them manually to regenerate.")
    exit(0)

# Generate 2048-bit RSA key
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Save private key
private_path.write_bytes(
    private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
)
private_path.chmod(0o600)  # owner-only read/write

# Save public key
public_path.write_bytes(
    private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
)

print(f"Keys generated:")
print(f"  Private: {private_path}")
print(f"  Public:  {public_path}")
print("\nNEVER commit the private key to version control.")
