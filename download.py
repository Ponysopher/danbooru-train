from database import MongoDBClient
import requests
import os

CDN_DOMAIN = "https://cdn.donmai.us"
WRITE_DIR = r"C:\Users\Michael\PycharmProjects\danbooru-train\downloads"

with MongoDBClient() as db_client:
    image_data = db_client.get_small_image_data()
    for data in image_data:
        if 'smaller' in data['urls']:
            img_id = data['id']

            # check that we don't already have an image with that id
            image_absolute_path = os.path.join(WRITE_DIR, str(img_id) + '.jpg')
            if os.path.exists(image_absolute_path):
                print("Image already exists. Skipping...")
                continue

            # download the image
            url = CDN_DOMAIN + data['urls']['smaller']
            response = requests.get(url=url, stream=True)
            if response.status_code == 200:

                # write to disk
                with open(image_absolute_path, "wb") as file:
                    # Iterate over the response content in chunks and write to file
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                print("Image downloaded successfully.")
            else:
                response.raise_for_status()
