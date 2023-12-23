import os

from envrx import ENVRX

xenv = ENVRX(env_file="sample.env")
xenv.intilize()
# Accessing Key from database
print(os.environ.get("alread_key_in_env_file")) # Will print the key which is already in the database 
print(xenv.get_all_env_from_database()) # Will print all configs in the database

# You can't use database functions with env_file
# Maybe in future updates, it will be implemented