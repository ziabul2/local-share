"""Generate self-signed certificates for HTTPS/TLS support."""

import os
import subprocess
from pathlib import Path

def generate_self_signed_cert(cert_dir: str = "certs", common_name: str = "localhost"):
    """
    Generate a self-signed certificate for local network development.
    
    Args:
        cert_dir: Directory to store certificates
        common_name: Common name for the certificate (e.g., "192.168.1.100")
    """
    Path(cert_dir).mkdir(exist_ok=True)
    
    cert_file = os.path.join(cert_dir, "cert.pem")
    key_file = os.path.join(cert_dir, "key.pem")
    
    # Check if certificates already exist
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Certificates already exist in {cert_dir}")
        return cert_file, key_file
    
    print(f"Generating self-signed certificate for {common_name}...")
    
    try:
        # Use openssl to generate a self-signed cert
        cmd = [
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", key_file, "-out", cert_file,
            "-days", "365", "-nodes",
            "-subj", f"/CN={common_name}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"OpenSSL error: {result.stderr}")
            return None, None
        
        print(f"✓ Certificate generated: {cert_file}")
        print(f"✓ Key generated: {key_file}")
        return cert_file, key_file
        
    except FileNotFoundError:
        print("OpenSSL not found. Trying alternative approach with pyopenssl...")
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            from datetime import datetime, timedelta
            import ipaddress
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(common_name),
                    x509.DNSName("localhost"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256(), default_backend())
            
            # Write certificate
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Write private key
            with open(key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            print(f"✓ Certificate generated: {cert_file}")
            print(f"✓ Key generated: {key_file}")
            return cert_file, key_file
            
        except ImportError:
            print("cryptography library not found. Install with: pip install cryptography")
            return None, None
        except Exception as e:
            print(f"Error generating certificate: {e}")
            return None, None


if __name__ == "__main__":
    # Auto-generate on import if running as main
    generate_self_signed_cert()
