import numpy as np

from models.lstm_key_model import create_lstm_model


print("Creating LSTM model...")

model = create_lstm_model()

print("\nLSTM model created successfully!")

print("\nModel architecture:")

model.summary()

pseudo_key = np.array([
    [10, 20, 30, 40, 50]
], dtype=np.int32)

print("\nPseudo Key:")
print(pseudo_key)

print("\nTesting LSTM prediction...")

prediction = model.predict(
    pseudo_key,
    verbose=0
)

print("\nPrediction shape:")
print(prediction.shape)

print("\nSUCCESS: LSTM model is working!")