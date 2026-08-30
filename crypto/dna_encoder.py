DNA_MAP = {
    "00": "A",
    "01": "C",
    "10": "G",
    "11": "T"
}


def bytes_to_binary(data):
    return ''.join(format(byte, '08b') for byte in data)


def binary_to_dna(binary_data):
    if len(binary_data) % 2 != 0:
        binary_data += "0"

    dna = ""

    for i in range(0, len(binary_data), 2):
        pair = binary_data[i:i + 2]
        dna += DNA_MAP[pair]

    return dna


def bytes_to_dna(data):
    binary_data = bytes_to_binary(data)
    return binary_to_dna(binary_data)