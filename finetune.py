import os
import pickle
from tensorflow import keras
from keras.applications import ResNet50
from keras.layers import Dense, GlobalAveragePooling2D
import matplotlib.pyplot as plt
from preprocess import get_data

# handle matplotlib killing itself immediately
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Get set of tags
unique_tags = ['long_hair', 'solo', 'looking_at_viewer', 'breasts', 'smile', 'blush', 'shirt', 'open_mouth',
               'simple_background', 'short_hair']

# Pre-process data
X, Y = get_data(unique_tags, 10_000)
print("Pre-processing complete.")
print("X", X.shape)
print("Y", Y.shape)

# Define model
base_model = ResNet50(weights='imagenet', include_top=False)
for layer in base_model.layers:
    layer.trainable = False
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(len(unique_tags), activation='sigmoid')(x)
model = keras.Model(inputs=base_model.input, outputs=predictions)
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Load model weights
weights_filename = 'model_weights.h5'
if os.path.exists(weights_filename):
    model.load_weights(weights_filename)

# Load training history
history_filename = 'training_history.pkl'
history = {"loss": [], "accuracy": []}
if os.path.exists(history_filename):
    with open(history_filename, 'rb') as f:
        history = pickle.load(f)

# Train the model
new_history = model.fit(X, Y, epochs=10)

# Combine the old and new history
for key in new_history.history.keys():
    if key in history:
        history[key].extend(new_history.history[key])
    else:
        history[key] = new_history.history[key]

# Save the updated history
with open(history_filename, 'wb') as f:
    pickle.dump(history, file=f)

# Save model weights
model.save_weights(weights_filename)

# Plot training history
plt.plot(history['accuracy'])
# plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
# plt.legend(['train', 'val'], loc='upper left')
plt.legend('train', loc='upper left')
plt.show()
