import secrets
import base64

# Generate a random 32-byte key and encode it in base64
secret_key = base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
print("\nYour Flask secret key:")
print(secret_key)
print("\nAdd this to your .env file as:")
print(f"FLASK_SECRET_KEY={secret_key}") 