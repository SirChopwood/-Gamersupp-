import pymongo
import json


class Main:
    def __init__(self):
        with open("mongo.txt", "r") as file:
            token = file.readlines()
        self.client = pymongo.MongoClient(token)
        self.bot_database = self.client['skullandcandy']

    def get_guild_collection(self, guild_id):
        collection = self.bot_database[str(guild_id)]
        return collection

    def get_settings(self, guild_id):
        collection = self.get_guild_collection(guild_id)
        settings = collection.find_one({"Type": "Settings"})
        return settings

    def set_settings(self, guild_id, settings):
        collection = self.get_guild_collection(guild_id)
        collection.replace_one({"Type": "Settings"}, settings)

    def add_settings(self, guild_id, settings):
        collection = self.get_guild_collection(guild_id)
        collection.insert_one(settings)
