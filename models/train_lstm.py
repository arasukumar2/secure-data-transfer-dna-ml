import csv
import numpy as np
from tensorflow.keras.utils import pad_sequences

from models.lstm_key_model import create_lstm_model


DATASET_PATH = "dataset/training_data.csv"


def load_dataset():

    sequences = []
    targets = []

    with open(DATASET_PATH, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            sequence = [
                int(value)
                for value in row["input"].split()
            ]

            target = int(row["target"])

            sequences.append(sequence)
            targets.append(target)

    return np.array(sequences, dtype=np.int32), np.array(targets, dtype=np.int32)


print("Loading dataset...")

X, y = load_dataset()

print("Input shape:", X.shape)
print("Target shape:", y.shape)

print("\nCreating LSTM model...")

model = create_lstm_model()

print("\nBuilding model...")

model.build(input_shape=(None, X.shape[1]))

model.summary()

print("\nStarting training...")

history = model.fit(
    X,
    y,
    epochs=10,
    batch_size=4,
    validation_split=0.2,
    verbose=1
)

print("\nTraining completed!")

print("\nFinal training accuracy:",
      history.history["accuracy"][-1])

print("Final validation accuracy:",
      history.history["val_accuracy"][-1])

print("\nSUCCESS: LSTM training pipeline completed!")
MODEL_PATH = "trained_models/lstm_model.keras"

model.save(MODEL_PATH)

print("\nModel saved successfully!")
print("Saved to:", MODEL_PATH)