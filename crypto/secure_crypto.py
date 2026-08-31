import secrets
import numpy as np

from crypto.dna_encoder import bytes_to_dna
from crypto.dna_decoder import dna_to_bytes
from crypto.encryption import xor_encrypt, xor_decrypt


MODEL_PATH = "trained_models/lstm_model.keras"


# ==========================================
# GENERATE RANDOM PSEUDO KEY
# ==========================================

def generate_pseudo_key(length=5):
    """
    Generate a cryptographically random
    pseudo-key containing 5 integer values.
    """

    return np.array(
        [
            secrets.randbelow(256)
            for _ in range(length)
        ],
        dtype=np.int32
    )


# ==========================================
# GENERATE LSTM KEY
# ==========================================
def generate_lstm_key(pseudo_key):
    """
    Generate an encryption key using
    the trained LSTM model.
    """

    # Load TensorFlow only when the ML model is actually needed.
    from tensorflow.keras.models import load_model

    model = load_model(
        MODEL_PATH
    )

    pseudo_key = np.array(
        pseudo_key,
        dtype=np.int32
    )

    if pseudo_key.ndim == 1:

        pseudo_key = np.expand_dims(
            pseudo_key,
            axis=0
        )

    prediction = model.predict(
        pseudo_key,
        verbose=0
    )

    key_value = int(
        np.argmax(
            prediction,
            axis=-1
        )[0]
    )

    key = bytes([
        key_value % 256
    ])

    return key



# ==========================================
# ENCRYPT DATA
# ==========================================

def encrypt_data(data):
    """
    Encrypt file data using:

    1. DNA encoding
    2. LSTM-based key generation
    3. XOR encryption
    """

    # Generate unique pseudo-key
    pseudo_key = generate_pseudo_key()


    # Generate LSTM encryption key
    key = generate_lstm_key(
        pseudo_key
    )


    # Convert binary data to DNA representation
    dna_data = bytes_to_dna(
        data
    )


    # Convert DNA string to bytes
    dna_bytes = dna_data.encode(
        "ascii"
    )


    # XOR encryption
    encrypted_data = xor_encrypt(
        dna_bytes,
        key
    )


    return encrypted_data, pseudo_key


# ==========================================
# DECRYPT DATA
# ==========================================

def decrypt_data(
    encrypted_data,
    pseudo_key
):
    """
    Decrypt data using the same
    LSTM-generated key.
    """

    # Recreate the same LSTM key
    key = generate_lstm_key(
        pseudo_key
    )


    # XOR decryption
    dna_bytes = xor_decrypt(
        encrypted_data,
        key
    )


    # Convert bytes back to DNA string
    dna_data = dna_bytes.decode(
        "ascii"
    )


    # Convert DNA back to original bytes
    original_data = dna_to_bytes(
        dna_data
    )


    return original_data