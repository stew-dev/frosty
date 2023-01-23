from pymongo import MongoClient


class Database:
    db = None

    def __init__(self, ip):
        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        CONNECTION_STRING = "mongodb://{}/frosty".format(ip)
        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        client = MongoClient(CONNECTION_STRING)

        # Create the database for our example (we will use the same database throughout the tutorial
        self.db = client['frosty']

    def insert(self, collection_name, items):
        collection = self.db[collection_name]
        collection.insert_many(items)

    def get_all(self, collection_name):
        collection = self.db[collection_name]
        return collection.find()

    def get_by_query(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.find(query)
