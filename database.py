import pymongo
import pymongo.errors
import logging
import json


class MongoDBClient:
    def __init__(self, config_file="mongodb_config.json"):
        """
        Initialize MongoDBClient with connection details from config file.

        Args:
            config_file (str): Path to the JSON config file containing connection details.
        """
        with open(config_file, "r") as file:
            config = json.load(file)

        username = config.get("username")
        password = config.get("password")
        cluster_url = config.get("cluster_url")
        database = config.get("database")

        # Build the connection string
        self.connection_string = (f"mongodb+srv://{username}:{password}@{cluster_url}/{database}?retryWrites=true&w"
                                  f"=majority")
        self.db_name = config.get("database")
        self.collection_name = config.get("collection")
        self.client = None

    def __enter__(self):
        """
        Context manager entry point. Establishes connection to MongoDB.

        Returns:
            MongoDBClient: Instance of MongoDBClient.
        """
        try:
            self.client = pymongo.MongoClient(self.connection_string)
            return self
        except pymongo.errors.ConnectionFailure as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context manager exit point. Closes MongoDB connection.

        Args:
            exc_type: Type of exception (if any).
            exc_value: Value of exception (if any).
            traceback: Traceback information (if any).
        """
        if self.client is not None:
            self.client.close()

    def _get_collection(self):
        """
        Helper method to get the MongoDB collection object.

        Returns:
            pymongo.collection.Collection: MongoDB collection object.
        """
        db = self.client[self.db_name]
        return db[self.collection_name]

    def test_connection(self):
        """
        Test the connection to the MongoDB server.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            self.client.admin.command('ping')  # Send ping command to test connection
            logging.info("Connected to MongoDB sucessfully.")
            return True
        except pymongo.errors.PyMongoError as connectionError:
            logging.error(connectionError)
            return False

    def insert_one(self, document):
        """
        Insert a document into the MongoDB collection.

        Args:
            document (dict): Document to be inserted.

        Returns:
            pymongo.results.InsertOneResult: Result of the insertion operation.
        """
        try:
            self._get_collection().insert_one(document)
            logging.info("Document inserted successfully.")
            return True
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Failed to insert document: {e}")
            raise

    def find_one_by_id(self, document_id):
        """
        Find a document by its ID in the MongoDB collection.

        Args:
            document_id: ID of the document to find.

        Returns:
            dict: Found document or None if not found.
        """
        try:
            return self._get_collection().find_one({"_id": document_id})
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Failed to find document by ID: {e}")
            raise

    async def get_images_count(self):
        """
        Get the count of images in the MongoDB collection asynchronously.

        Returns:
            int: Count of images.
        """
        try:
            collection = self._get_collection()
            count = collection.count_documents({})
            return count
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Failed to get images count: {e}")
            raise

    async def get_smallest_id(self):
        try:
            # Connect to the collection
            collection = self.client[self.db_name][self.collection_name]

            # Find the document with the smallest 'id' field
            smallest_document = collection.find_one({}, sort=[("id", pymongo.ASCENDING)])

            # If no document found or 'id' field is missing, return None
            if smallest_document is None or 'id' not in smallest_document:
                return None

            # Return the value of the smallest 'id'
            return smallest_document['id']
        except Exception as e:
            logging.error(f"Failed to get the smallest id from the database: {str(e)}")
            return None

    def get_image_data(self, limit=100):
        try:
            collection = self._get_collection()
            image_metadata = collection.find(limit=limit)
            return image_metadata
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Failed to get images count: {e}")
            raise

    def get_small_image_data(self, limit=10_000):
        try:
            collection = self._get_collection()
            image_metadata = collection.find({"urls.smaller": {'$exists': True}}, limit=limit)
            return image_metadata
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Failed to get images count: {e}")
            raise

    def get_unique_tags(self):
        try:
            collection = self._get_collection()
            # Use the aggregation framework to get a dictionary of tags and their counts
            tag_counts = collection.aggregate([
                {"$unwind": "$tags"},  # Unwind the tags array
                {"$group": {"_id": "$tags", "count": {"$sum": 1}}},  # Group by each tag and count occurrences
                {"$sort": {"count": -1}}  # Sort by count in descending order (optional)
            ])

            # Convert the aggregation result to a dictionary
            return {doc['_id']: doc['count'] for doc in tag_counts}
        except pymongo.errors.PyMongoError as e:
            logging.error(f"Failed to get images count: {e}")
            raise
