import rasterio
import numpy as np
import joblib

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    LSTM,
    Dense,
    Dropout
)

# =========================================
# LOAD DATASET
# =========================================

dataset = rasterio.open(
    '../dataset/ERA5_2019.tif'
)

combined_data = dataset.read()

print("Dataset Shape:", combined_data.shape)

# =========================================
# FEATURE EXTRACTION
# =========================================

features = []

for band in combined_data:

    # IGNORE NaN VALUES

    mean_value = np.nanmean(band)

    # ONLY STORE VALID VALUES

    if not np.isnan(mean_value):

        features.append(mean_value)

# CONVERT TO NUMPY ARRAY

features = np.array(features)

# CONVERT TYPE

features = features.astype(np.float32)

# REMOVE EXTREME VALUES

features = np.clip(
    features,
    -100,
    100
)

print("Clean Features Shape:", features.shape)

# =========================================
# NORMALIZATION
# =========================================

scaler = MinMaxScaler()

features_scaled = scaler.fit_transform(
    features.reshape(-1,1)
)

print(
    "Scaled Features Shape:",
    features_scaled.shape
)

# =========================================
# CREATE SEQUENCES
# =========================================

sequence_length = 30

X = []
y = []

for i in range(
    sequence_length,
    len(features_scaled)
):

    X.append(
        features_scaled[
            i-sequence_length:i
        ]
    )

    y.append(
        features_scaled[i]
    )

X = np.array(X)
y = np.array(y)

print("X Shape:", X.shape)
print("y Shape:", y.shape)

# =========================================
# TRAIN TEST SPLIT
# =========================================

train_size = int(
    len(X) * 0.8
)

X_train = X[:train_size]
X_test = X[train_size:]

y_train = y[:train_size]
y_test = y[train_size:]

print("X_train Shape:", X_train.shape)
print("X_test Shape:", X_test.shape)

# =========================================
# BUILD LSTM MODEL
# =========================================

model = Sequential()

model.add(

    LSTM(

        64,

        return_sequences=True,

        input_shape=(
            X_train.shape[1],
            X_train.shape[2]
        )
    )
)

model.add(
    Dropout(0.2)
)

model.add(
    LSTM(64)
)

model.add(
    Dropout(0.2)
)

model.add(
    Dense(1)
)

# =========================================
# COMPILE MODEL
# =========================================

model.compile(
    optimizer='adam',
    loss='mse',
    metrics=['mae']
)

# =========================================
# TRAIN MODEL
# =========================================

history = model.fit(

    X_train,

    y_train,

    epochs=50,

    batch_size=32,

    validation_data=(
        X_test,
        y_test
    )
)

# =========================================
# SAVE MODEL
# =========================================

model.save(
    '../model/climate_lstm_model.keras'
)

joblib.dump(
    scaler,
    '../model/scaler.save'
)

print("\nMODEL TRAINED SUCCESSFULLY")

# =========================================
# PREDICTIONS
# =========================================

predictions = model.predict(
    X_test
)

# =========================================
# REMOVE NaN VALUES
# =========================================

predictions = np.nan_to_num(
    predictions
)

y_test = np.nan_to_num(
    y_test
)

# =========================================
# INVERSE TRANSFORM
# =========================================

predictions_inverse = scaler.inverse_transform(
    predictions.reshape(-1,1)
)

y_test_inverse = scaler.inverse_transform(
    y_test.reshape(-1,1)
)

# =========================================
# FINAL CLEANING
# =========================================

predictions_inverse = np.nan_to_num(
    predictions_inverse
)

y_test_inverse = np.nan_to_num(
    y_test_inverse
)

# =========================================
# EVALUATION METRICS
# =========================================

r2 = r2_score(
    y_test_inverse,
    predictions_inverse
)

mae = mean_absolute_error(
    y_test_inverse,
    predictions_inverse
)

rmse = np.sqrt(

    mean_squared_error(
        y_test_inverse,
        predictions_inverse
    )
)

# =========================================
# APPROX ACCURACY
# =========================================

accuracy = max(
    0,
    r2 * 100
)

# =========================================
# PRINT RESULTS
# =========================================

print("\n==========================")

print("MODEL EVALUATION RESULTS")

print("==========================\n")

print(f"R2 Score: {r2}")

print(f"MAE: {mae}")

print(f"RMSE: {rmse}")

print(f"Approx Accuracy: {accuracy:.2f}%")

print("\n==========================")