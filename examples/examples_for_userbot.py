# If you are using a userbot etc, then you can do by the following tips and tricks

# Lets say you have a Config file, and you wanna just load from file as for now and not from database at the 
# moment, then you can do by the following way
import os

from envrx import ENVRX

ENVRX("config.env").load_env_from_env_file()

# Now you can use the Config file as you want, and you can also use the Config file as a normal way
print(os.environ.get("API_ID_FROM_CONFIG_FILE"))


# Now lets say you started database and want to do it in a another file, like __init__.py or something else
# Then you can do by the following way
from pymongo import MongoClient


def main():
    ...
    my_database_client = MongoClient("my_database")
    my_database_client.server_info() # do it if you want else you can ignore it
    env_client = ENVRX(database=my_database_client, database_name="my_database_name")
    env_client.load_from_database(my_database_client)
    # retrive as dictionary if you want
    print(env_client.get_all_env_from_database())
    ...

