# import os
import numpy as np
from PIL import Image
from tensorflow import keras
from database import MongoDBClient


def resize_image(path, size=(224, 224)):
    img = Image.open(path)
    img = img.resize(size, Image.Resampling.LANCZOS)
    img = np.array(img)
    if img.ndim == 2:
        # Expand dimensions for grayscale images
        img = np.expand_dims(img, axis=-1)
    if img.shape[2] != 3:
        # Convert single channel images to RGB
        img = np.concatenate([img] * 3, axis=2)
    return img


# Image and tag generator
def get_data(unique_tags, img_count):
    with MongoDBClient() as db_client:
        limit = img_count
        docs = db_client.get_small_image_data(limit=limit)

        x = np.zeros((limit, 224, 224, 3), dtype=np.float32)
        y = np.zeros((limit, len(unique_tags)), dtype=np.int32)

        for i, document in enumerate(docs):
            print(f"Processing image {i+1} of {limit}")
            imagePath = './downloads/' + str(document['id']) + '.jpg'
            tag_vector = [1 if tag in document['tags'] else 0 for tag in unique_tags]
            img = resize_image(imagePath)
            img = keras.applications.resnet50.preprocess_input(img)
            x[i] = img
            y[i] = np.array(tag_vector)
        return x, y
