DNA_REVERSE_MAP = {
    "A": "00",
    "C": "01",
    "G": "10",
    "T": "11"
}


def dna_to_binary(dna_data):
    binary_data = ""

    for base in dna_data:
        if base not in DNA_REVERSE_MAP:
            raise ValueError(f"Invalid DNA base: {base}")

        binary_data += DNA_REVERSE_MAP[base]

    return binary_data


def binary_to_bytes(binary_data):
    if len(binary_data) % 8 != 0:
        raise ValueError("Invalid binary length")

    data = bytearray()

    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i + 8]
        data.append(int(byte, 2))

    return bytes(data)


def dna_to_bytes(dna_data):
    binary_data = dna_to_binary(dna_data)
    return binary_to_bytes(binary_data)