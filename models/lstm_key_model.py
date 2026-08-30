import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense


VOCAB_SIZE = 5000
EMBEDDING_DIM = 32
LSTM_UNITS = 100


def create_lstm_model():

    model = Sequential([
        Embedding(
            input_dim=VOCAB_SIZE,
            output_dim=EMBEDDING_DIM
        ),

        LSTM(LSTM_UNITS),

        Dense(
            VOCAB_SIZE,
            activation="softmax"
        )
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


def generate_key(model, pseudo_key):

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

    key = np.argmax(
        prediction,
        axis=-1
    )

    return key