from tensorflow.keras.models import load_model

model = load_model(
    "../model/climate_lstm_model.h5",
    compile=False
)

print("Model loaded successfully")

from tensorflow.keras.models import load_model
import numpy as np

model = load_model(
    "../model/climate_lstm_model.h5",
    compile=False
)

sample = np.array([
    [
        [0.20, 0.10, 0.05],
        [0.25, 0.12, 0.04],
        [0.30, 0.15, 0.06]
    ]
])

pred = model.predict(sample)

print(pred)