from crypto.dna_encoder import bytes_to_dna
from crypto.dna_decoder import dna_to_bytes


original = b"Hello World"

print("Original:", original)

dna = bytes_to_dna(original)

print("DNA:", dna)

recovered = dna_to_bytes(dna)

print("Recovered:", recovered)

if original == recovered:
    print("SUCCESS: DNA encoding and decoding works!")
else:
    print("FAILED")