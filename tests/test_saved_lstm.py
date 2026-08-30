import numpy as np
from tensorflow.keras.models import load_model


MODEL_PATH = "trained_models/lstm_model.keras"

print("Loading trained LSTM model...")

model = load_model(MODEL_PATH)

print("Model loaded successfully!")

pseudo_key = np.array([
    [10, 20, 30, 40, 50]
], dtype=np.int32)

print("\nPseudo-key:")
print(pseudo_key)

prediction = model.predict(
    pseudo_key,
    verbose=0
)

print("\nPrediction shape:")
print(prediction.shape)

generated_key = np.argmax(
    prediction,
    axis=-1
)

print("\nGenerated key:")
print(generated_key)

print("\nSUCCESS: Trained LSTM model loaded and tested!")