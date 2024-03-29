import os

from envrx import ENVRX

xenv = ENVRX(database="yourredisurl", database_name="config")
xenv.intilize()
# Accessing Key from database
print(os.environ.get("alread_key_in_database")) # Will print the key which is already in the database 
# Adding a new key to the database
xenv.load_env_to_database("key_name", "value")
# Accessing the key from database
print("Value: ", os.environ.get('key_name')) # Will print "value"
# Updating the key in database
xenv.update_key_in_database("key_name", "new_value")
# Accessing the key from database
print("Value: ", os.environ.get('key_name')) # Will print "new_value"
# Deleting the key from database
xenv.delete_key_from_database("key_name")
# Accessing the key from database
print("Value: ", os.environ.get('key_name')) # Will print None
# Get all configs from database
print(xenv.get_all_env_from_database()) # Will print all configs in the database