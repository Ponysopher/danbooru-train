import logging
import asyncio
from pprint import pformat

from database import MongoDBClient
from pymongo.errors import DuplicateKeyError
from api import DanbooruAPI
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger("main")

# Define the maximum number of concurrent requests to the API
MAX_CONCURRENT_REQUESTS = 5


async def fetch_and_insert_image_metadata(mongo_client, desired_count, semaphore):
    # Get the count of inserted images
    inserted_image_count = await mongo_client.get_images_count()

    # Get the last post ID and use it as the first
    next_post_id = await DanbooruAPI.get_latest_post_id()
    next_post_id += 1

    # Ensure next_post_id is less than the smallest 'id' in the database
    smallest_id = await mongo_client.get_smallest_id()
    if smallest_id is not None and smallest_id < next_post_id:
        next_post_id = smallest_id

    # Semaphore to limit concurrent requests
    async with semaphore:
        # Loop until desired image count is reached
        while inserted_image_count < desired_count:
            logging.info(f"Getting image metadata for post with ID {next_post_id} {inserted_image_count + 1} of "
                         f"{desired_count}.")
            # Get the ID of the next latest post
            next_post_id -= 1

            # Fetch post metadata asynchronously
            try:
                post_metadata = await DanbooruAPI.get_post_by_id(next_post_id)
                logging.info("Fetched post medadata.")
                if logger.isEnabledFor(logging.DEBUG):
                    logging.debug(pformat(post_metadata))
            except aiohttp.ClientResponseError:
                logging.error("Could not get image metadata")
                continue

            # If the image is banned, continue
            if post_metadata['is_banned'] or post_metadata['is_deleted']:
                logging.info("Image is banned or deleted. Skipping...")
                continue

            if 'file_url' not in post_metadata:
                logging.info("Image has no file url. Skipping...")
                continue

            # Filter desired metadata
            filtered_metadata = DanbooruAPI.filter_desired_metadata(post_metadata)

            # Log the metadata
            logging.info(f"Fetched metadata for post with ID {next_post_id}: {filtered_metadata}")

            # Insert the image metadata into the database
            try:
                mongo_client.insert_one(filtered_metadata)
                inserted_image_count += 1
            except DuplicateKeyError:
                logging.warning("Failed to insert image metadata due to duplicate key error. Skipping...")

if __name__ == '__main__':
    DESIRED_IMAGE_COUNT = 10_000  # Change this to the desired number of images

    # Create a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    # Connect to MongoDB
    with MongoDBClient() as db_client:
        # Execute the asynchronous function to fetch and insert image metadata
        try:
            asyncio.run(fetch_and_insert_image_metadata(db_client, DESIRED_IMAGE_COUNT, semaphore))
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
