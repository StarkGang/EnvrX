import os

from envrx import ENVRX

xenv = ENVRX(database="sqlitelocal.db", database_name="config", env_file="sample.env")
xenv.intilize()



class Config(object):
    NORMAL_ENV_STORED_IN_DEVICE = os.environ.get("NORMAL_ENV_STORED_IN_DEVICE", "default_value")
    ENV_STORED_IN_DATABASE = os.environ.get("ENV_STORED_IN_DATABASE", "default_value")
    ENV_STORED_IN_ENV_FILE = os.environ.get("ENV_STORED_IN_ENV_FILE", "default_value")


print("This is an env that was stored in the device: ", Config.NORMAL_ENV_STORED_IN_DEVICE)
print("This is an env that was stored in the database: ", Config.ENV_STORED_IN_DATABASE)
print("This is an env that was stored in the env file: ", Config.ENV_STORED_IN_ENV_FILE)


# Adding new keys to database 
xenv.load_env_to_database("NEW_KEY_IN_DATABASE", "NEW_VALUE")
print("This is an env that was stored in the database: ", os.environ.get("NEW_KEY_IN_DATABASE"))

# Updating keys in database
xenv.update_key_in_database("NEW_KEY_IN_DATABASE", "NEW_VALUE2")
print("This is an env that was updated from the database: ", os.environ.get("NEW_KEY_IN_DATABASE"))

# Deleting keys from database
xenv.delete_key_from_database("NEW_KEY_IN_DATABASE")
print("This is an env that was deleted from database: ", os.environ.get("NEW_KEY_IN_DATABASE"))