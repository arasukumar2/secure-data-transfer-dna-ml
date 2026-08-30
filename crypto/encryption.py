def xor_encrypt(data, key):
    """
    Encrypt data using XOR with a repeating key.
    """
    if not key:
        raise ValueError("Key cannot be empty")

    encrypted = bytearray()

    for i, byte in enumerate(data):
        encrypted.append(byte ^ key[i % len(key)])

    return bytes(encrypted)


def xor_decrypt(encrypted_data, key):
    """
    Decrypt XOR-encrypted data.
    XOR encryption and decryption use the same operation.
    """
    return xor_encrypt(encrypted_data, key)