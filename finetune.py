import os
import json
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
X, Y = get_data(unique_tags)
print("Pre-processing complete.")
print("X", X.shape)
print("Y", Y.shape)
input()

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
history = model.fit(X, Y, epochs=5)

# Plot training history
plt.plot(history.history['accuracy'])
# plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
# plt.legend(['train', 'val'], loc='upper left')
plt.legend('train', loc='upper left')
plt.show()
