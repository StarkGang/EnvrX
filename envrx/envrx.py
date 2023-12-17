# Copyright (C) 2023-present by StarkGang@Github, < https://github.com/StarkGang >.
#
# This file is part of < https://github.com/StarkGang/Envrx > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/StarkGang/Envrx/blob/main/LICENSE >
#
# All rights reserved.

import os
import re
from urllib.parse import urlparse
from envrx.exceptions import *
from envrx.utils import *
import sqlite3
import logging
import json
import yaml

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

if is_mongo_installed := check_if_package_installed('pymongo'):
    log.debug("pymongo is installed.")
    from pymongo import MongoClient
if is_redis_installed := check_if_package_installed('redis'):
    log.debug("redis is installed.")
    import redis
if is_psycopg2_installed := check_if_package_installed('psycopg2'):
    log.debug("psycopg2 is installed.")
    import psycopg2

class ENVRX:
    """ENVRX is a class to manage environment variables."""
    def __init__(self, env_file: str=None, database_url: str=None, collection_or_table_name: str=None) -> None:
        """Initialize the ENVRX class.

        Parameters:
            env_file (str): Path to the environment file.
            database_url (str): Database url.
            collection_or_table_name (str): Name of the collection or table in the database.
        Returns:
            None"""
        self.database_url = database_url
        self.collection_or_table_name = collection_or_table_name
        self.env_file = env_file
        self.client = None
        self.database_url_name = None
        if self.database_url and (not self.collection_or_table_name):
            raise InvalidCollectionOrTableName("No database/table name given. Please provide a database/table name.")

    def intilize(self) -> None:
        """Initialize the ENVRX class.

        Parameters:
            None
        Returns:
            None"""
        if self.database_url:
            log.debug("Database url provided.")
            self.database_url_name = guess_which_database_from_url(self.database_url)
            if self.database_url_name == 'mongo':
                log.debug("MongoDB database url provided.")
                if not is_mongo_installed:
                    raise ImportError("pymongo is not installed. Please install it using pip install pymongo.")
                self.client = MongoClient(self.database_url)
                try:
                    self.client.server_info()
                except Exception as e:
                    log.error("MongoDB database url is invalid. Unable to connect to the database.")
                    raise InvalidDatabaseUrl("Invalid database url. Please check the url and try again.", e)
            elif self.database_url_name in ['sql', 'sqlite']:
                log.debug("SQL database url provided.")
                try:
                    if self.database_url_name == 'sqlite':
                        self.client = sqlite3.connect(self.database_url)
                    else:
                        if not is_psycopg2_installed:
                            raise ImportError("psycopg2 is not installed. Please install it using pip install psycopg2.")
                        url = urlparse(url)
                        self.database_url = url.path[1:]
                        self.client = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
                except Exception as e:
                    log.error("SQL database url is invalid. Unable to connect to the database.")
                    raise InvalidDatabaseUrl("Invalid database url. Please check the url and try again.", e)
                self.create_sql_table_if_not_exists()
            elif self.database_url_name == 'redis':
                log.debug("Redis database url provided.")
                if not is_redis_installed:
                    raise ImportError("redis is not installed. Please install it using pip install redis.")
                try:
                    self.client = redis.Redis.from_url(self.database_url)
                except Exception as e:
                    log.error("Redis database url is invalid. Unable to connect to the database.")
                    raise InvalidDatabaseUrl("Invalid database url. Please check the url and try again.", e)
            else:
                log.error("Invalid database url provided.")
                raise InvalidDatabaseUrl("Invalid database url. Please check the url and try again.")
            self.load_from_database()
        if self.env_file:
            log.debug("Environment file provided.")
            if not os.path.exists(self.env_file):
                log.error("Environment file not found.")
                raise FileNotFoundError("Environment file not found. Please check the file path and try again.")
            self.load_env_from_file()
        
    def create_sql_table_if_not_exists(self):
        """Create SQL table if not exists.

        Parameters:
            None
        Returns:
            None"""
        if self.database_url_name not in ['sql', 'sqlite']:
            raise NoDatabaseUrlSupplied("No database url supplied. Please supply a database url.")
        log.debug("Creating SQL table if not exists.")
        cursor = self.client.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.collection_or_table_name} (key TEXT PRIMARY KEY, value TEXT)")
        self.client.commit()

    def load_env_from_file(self):
        """Load environment variables from file.

        Parameters:
            None
        Returns:
            None"""
        if not self.env_file:
            raise FileNotFoundError("No environment file supplied. Please supply an environment file.")
        if self.env_file.endswith('.env'):
            self.load_env_from_env_file()
        elif self.env_file.endswith('.json'):
            self.load_env_from_json_file()
        elif self.env_file.endswith('.yaml'):
            self.load_env_from_yaml_file()
        else:
            log.error("Invalid environment file provided.")
            raise InvalidEnvFile("Invalid environment file. Please check the file and try again.")
        

    def load_env_from_json_file(self):
        """Load environment variables from json file.

        Parameters:
            None
        Returns:
            None"""
        log.debug("Loading environment variables from json file.")
        file_path = os.path.abspath(self.env_file)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                json_content = json.loads(content)
                for key, value in json_content.items():
                    os.environ[key.upper()] = value
        except Exception as e:
            raise InvalidEnvFile("Invalid environment file. Please check the file and try again.", e)
        
    def load_env_from_yaml_file(self):
        """Load environment variables from yaml file.

        Parameters:
            None
        Returns:
            None"""
        log.debug("Loading environment variables from yaml file.")
        file_path = os.path.abspath(self.env_file)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                yaml_content = yaml.safe_load(content)
                for key, value in yaml_content.items():
                    os.environ[key.upper()] = value
        except Exception as e:
            raise InvalidEnvFile("Invalid environment file. Please check the file and try again.", e)
        
    def load_env_from_env_file(self):
        """Load environment variables from file.

        Parameters:
            None
        Returns:
            None"""
        log.debug("Loading environment variables from file.")
        file_path = os.path.abspath(self.env_file)
        pattern = re.compile(r'(\w+)\s*=\s*(?:"(.*?)"|([^"\n]+))', re.DOTALL)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                matches = pattern.findall(content)
                for key, quoted_value, unquoted_value in matches:
                    value = quoted_value if quoted_value else unquoted_value
                    os.environ[key.upper()] = value.replace('\n', '')
        except Exception as e:
            raise InvalidEnvFile("Invalid environment file. Please check the file and try again.", e)
    

    def load_from_database(self):
        """Load environment variables from database.

        Parameters:
            None
        Returns:
            None"""
        if not self.database_url:
            raise NoDatabaseUrlSupplied("No database url supplied. Please supply a database url.")
        log.debug("Loading environment variables from database.")
        if self.database_url_name == 'mongo':
            log.debug("Loading environment variables from MongoDB database.")
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            for doc in collection.find():
                os.environ[doc['key'].upper()] = doc['value']
        elif self.database_url_name in ['sql', 'sqlite']:
            log.debug("Loading environment variables from SQL database.")
            with self.client:
                cursor = self.client.cursor()
                result = cursor.execute(f"SELECT * FROM {self.collection_or_table_name}")
                for row in result:
                    os.environ[row[0].upper()] = row[1]
        elif self.database_url_name == 'redis':
            log.debug("Loading environment variables from Redis database.")
            for key in self.client.keys():
                os.environ[key.decode('utf-8').upper()] = self.client.get(key).decode('utf-8')


    def get_env_from_database(self, key):
        """Get environment variable from database.

        Parameters:
            key (str): Environment variable key.
        Returns:
            str: Environment variable value."""
        if not self.database_url:
            raise NoDatabaseUrlSupplied("No database url supplied. Please supply a database url.")
        log.debug(f"Getting environment variable {key} from database.")
        if self.database_url_name == 'mongo':
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            if result := collection.find_one({'key': key}):
                return result['value']
            else:
                raise None
        elif self.database_url_name in ['sql', 'sqlite']:
            with self.client:
                cursor = self.client.cursor()
                result = cursor.execute(f"SELECT * FROM {self.collection_or_table_name} WHERE key=?", (key,))
                return None if not result.fetchone() else result.fetchone()[1]
        elif self.database_url_name == 'redis':
            result = self.client.get(key)
            return None if not result else result.decode('utf-8')


    def get_all_env_from_database(self):
        """Get all environment variables from database.

        Parameters:
            None
        Returns:
            dict: Environment variables."""
        if not self.database_url:
            raise NoDatabaseUrlSupplied("No database url supplied. Please supply a database url.")
        if self.database_url_name == 'mongo':
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            return collection.find()
        elif self.database_url_name in ['sql', 'sqlite']:
            with self.client:
                cursor = self.client.cursor()
                return cursor.execute(f"SELECT * FROM {self.collection_or_table_name}")
        elif self.database_url_name == 'redis':
            return self.client.keys()

    def load_env_to_database(self, key, value):
        """Load environment variable to database.

        Parameters:
            key (str): Environment variable key.
            value (str): Environment variable value.
        Returns:
            None"""
        if not self.database_url:
            raise NoDatabaseUrlSupplied("No database url supplied. Please supply a database url.")
        if self.database_url_name == 'mongo':
            log.debug(f"Loading environment variable {key}={value} to MongoDB database.")
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            collection.insert_one({'key': key, 'value': value})
        elif self.database_url_name in ['sql', 'sqlite']:
            log.debug(f"Loading environment variable {key}={value} to SQL database.")
            with self.client:
                cursor = self.client.cursor()
                cursor.execute(f"INSERT OR REPLACE INTO {self.collection_or_table_name} (key, value) VALUES (?, ?)", (key, value))
        elif self.database_url_name == 'redis':
            log.debug(f"Loading environment variable {key}={value} to Redis database.")
            self.client.set(key, value)
        os.environ[key.upper()] = value
    
    def delete_env_from_database(self, key):
        """Delete environment variable from database.

        Parameters:
            key (str): Environment variable key.
        Returns:
            None"""
        if not self.database_url:
            raise NoDatabaseUrlSupplied("No database url supplied. Please supply a database url.")
        log.debug(f"Deleting environment variable {key} from database.")
        if self.database_url_name == 'mongo':
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            collection.delete_one({'key': key})
        elif self.database_url_name in ['sql', 'sqlite']:
            with self.client:
                cursor = self.client.cursor()
                # Check if the key exists in the database
                result = cursor.execute(f"SELECT * FROM {self.collection_or_table_name} WHERE key=?", (key,))
                if not result.fetchone():
                    raise KeyError(f"Key {key} not found in the database.")
                cursor.execute(f"DELETE FROM {self.collection_or_table_name} WHERE key=?", (key,))
        elif self.database_url_name == 'redis':
            self.client.delete(key)
        del os.environ[key.upper()]

    def update_env_in_database(self, key, value):
        """Update environment variable in database.
        
        Parameters:
            key (str): Environment variable key.
            value (str): Environment variable value.
        Returns:
            None"""
        if not self.database_url:
            raise NoDatabaseUrlSupplied("No database url supplied. Please supply a database url.")
        if self.database_url_name == 'mongo':
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            collection.update_one({'key': key}, {'$set': {'value': value}})
        elif self.database_url_name in ['sql', 'sqlite']:
            with self.client:
                cursor = self.client.cursor()
                result = cursor.execute(f"SELECT * FROM {self.collection_or_table_name} WHERE key=?", (key,))
                if not result.fetchone():
                    self.load_env_to_database(key, value)
                else:
                    cursor.execute(f"UPDATE {self.collection_or_table_name} SET value=? WHERE key=?", (value, key))
        elif self.database_url_name == 'redis':
            self.client.set(key, value)
        os.environ[key.upper()] = value

