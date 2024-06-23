import logging
import aiohttp
import requests
import asyncio
import re


class DanbooruAPI:
    """
    Class for interacting with the Danbooru API to fetch image metadata.
    """

    @staticmethod
    def get_posts(url: str, limit: int = 20) -> dict:
        """
        Fetch posts from the given URL with optional limit.

        Args:
            url (str): The URL to fetch posts from.
            limit (int, optional): The maximum number of posts to fetch. Defaults to 20.

        Returns:
            dict: The JSON response containing the posts.
        """
        try:
            response = requests.get(url, params={'limit': limit})
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Handle network errors
            raise RuntimeError(f"Failed to fetch posts: {e}")

    @staticmethod
    def get_posts_by_page(page: int = 1, limit: int = 20) -> dict:
        """
        Fetch posts by page number with optional limit.

        Args:
            page (int, optional): The page number of posts to fetch. Defaults to 1.
            limit (int, optional): The maximum number of posts to fetch. Defaults to 20.

        Returns:
            dict: The JSON response containing the posts.
        """
        url = f"https://danbooru.donmai.us/posts.json?page={page}"
        return DanbooruAPI.get_posts(url, limit)

    @staticmethod
    async def get_post_by_id(post_id: int):
        """
        Fetch post metadata by its ID asynchronously.

        Args:
            post_id (int): The ID of the post.

        Returns:
            dict: The JSON response containing the post metadata.
        """
        url = f"https://danbooru.donmai.us/posts/{post_id}.json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    @staticmethod
    async def get_latest_post_id() -> int:
        """
        Fetch the ID of the latest post asynchronously.

        Returns:
            int: The ID of the latest post.
        """
        try:
            latest_post = await asyncio.to_thread(DanbooruAPI.get_posts_by_page, limit=1, page=1)
            return latest_post[0]['id']
        except (IndexError, KeyError):
            raise RuntimeError("Failed to fetch the latest post ID")

    @staticmethod
    def filter_desired_metadata(post: dict) -> dict:
        """
        Filter desired metadata from the post.

        Args:
            post (dict): The post metadata.

        Returns:
            dict: Filtered metadata containing 'id', 'file_url', and 'tags'.
        """
        logging.debug(f"Filtering desired metadata from source post...")
        smaller: str | None = None
        if 'variants' in post:
            smaller = post['variants'][1]['url']
        else:
            try:
                smaller = post['media_asset']['variants'][1]['url']
            except KeyError:
                pass

        logging.debug("Creating document...")
        document = {
            'id': post.get('id'),
            'urls': {
                'file_url': re.sub(r".*donmai.us", "", post.get('file_url')),
            },
            'tags': post.get('tag_string', '').split()
        }
        if smaller:
            logging.debug("Got smaller image...")
            document['urls']['smaller'] = re.sub(r".*donmai.us", "", smaller)
        return document
