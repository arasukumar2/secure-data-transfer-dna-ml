from crypto.secure_crypto import (
    encrypt_data,
    decrypt_data
)


original = b"Hello World"

print("Original:")
print(original)

print("\nEncrypting...")

encrypted_data, pseudo_key = encrypt_data(
    original
)

print("Encrypted data:")
print(encrypted_data)

print("\nPseudo-key:")
print(pseudo_key)

print("\nDecrypting...")

recovered = decrypt_data(
    encrypted_data,
    pseudo_key
)

print("Recovered:")
print(recovered)

if original == recovered:
    print("\nSUCCESS: Complete DNA + LSTM + XOR pipeline works!")
else:
    print("\nFAILED: Recovered data does not match!")