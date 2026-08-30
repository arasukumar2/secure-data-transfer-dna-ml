from crypto.encryption import xor_encrypt, xor_decrypt


original = b"Hello World"

key = b"secretkey"

print("Original:", original)
print("Key:", key)

encrypted = xor_encrypt(original, key)

print("Encrypted:", encrypted)

decrypted = xor_decrypt(encrypted, key)

print("Decrypted:", decrypted)

if original == decrypted:
    print("SUCCESS: Encryption and decryption works!")
else:
    print("FAILED")