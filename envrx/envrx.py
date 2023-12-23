# Copyright (C) 2023-present by StarkGang@Github, < https://github.com/StarkGang >.
#
# This file is part of < https://github.com/StarkGang/Envrx > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/StarkGang/Envrx/blob/main/LICENSE >
#
# All rights reserved.

import json
import logging
import os
import re
import sqlite3
from urllib.parse import urlparse

import yaml

from envrx.exceptions import *
from envrx.utils import *

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

if is_mongo_installed := check_if_package_installed("pymongo"):
    log.debug("pymongo is installed.")
    from pymongo import MongoClient
if is_redis_installed := check_if_package_installed("redis"):
    log.debug("redis is installed.")
    import redis
if is_psycopg2_installed := check_if_package_installed("psycopg2"):
    log.debug("psycopg2 is installed.")
    import psycopg2


class ENVRX:
    """ENVRX is a class to manage environment variables."""

    def __init__(
        self,
        env_file: str = None,
        database: str = None,
        collection_or_table_name: str = None,
    ) -> None:
        """Initialize the ENVRX class.

        Parameters:
            env_file (str): Path to the environment file.
            database (str): Database url or database object.
            collection_or_table_name (str): Name of the collection or table in the database.
        Returns:
            None"""
        self.database = database
        self.collection_or_table_name = collection_or_table_name
        self.env_file = env_file
        self.client = None
        self.databasename = None
        if self.database and (not self.collection_or_table_name):
            raise InvalidCollectionOrTableName(
                "No database/table name given. Please provide a database/table name."
            )
        self.collection_or_table_name = self.collection_or_table_name.strip()
        if " " in self.collection_or_table_name:
            raise ValueError(
                "Collection/table name cannot contain spaces. Please provide a valid collection/table name."
            )

    def intilize(self) -> None:
        """Initialize the ENVRX class.

        Parameters:
            None
        Returns:
            None"""
        if self.database:
            log.debug("Database url provided.")
            self.databasename = guess_which_database_from(self.database)
            if self.databasename == "mongo":
                log.debug("MongoDB database url provided.")
                if not is_mongo_installed:
                    raise ImportError(
                        "pymongo is not installed. Please install it using pip install pymongo."
                    )
                if isinstance(self.database, MongoClient):
                    self.client = self.database
                else:
                    self.client = MongoClient(self.database)
                    try:
                        self.client.envrx.command("ping")
                    except Exception as e:
                        log.error(
                            "MongoDB database url is invalid. Unable to connect to the database."
                        )
                        raise InvalidDatabaseUrl(
                            "Invalid database url. Please check the url and try again.",
                            e,
                        ) from e
            elif self.databasename in ["sql", "sqlite"]:
                log.debug("SQL database url provided.")
                try:
                    if self.databasename == "sqlite":
                        self.client = (
                            self.database
                            if isinstance(self.database, sqlite3.Connection)
                            else sqlite3.connect(self.database)
                        )
                    elif isinstance(self.database, psycopg2.extensions.connection):
                        self.client = self.database
                    else:
                        if not is_psycopg2_installed:
                            raise ImportError(
                                "psycopg2 is not installed. Please install it using pip install psycopg2."
                            )
                        url = urlparse(url)
                        self.database = url.path[1:]
                        self.client = psycopg2.connect(
                            database=url.path[1:],
                            user=url.username,
                            password=url.password,
                            host=url.hostname,
                            port=url.port,
                        )
                except Exception as e:
                    log.error(
                        "SQL database url is invalid. Unable to connect to the database."
                    )
                    raise InvalidDatabaseUrl(
                        "Invalid database url. Please check the url and try again.",
                        e,
                    ) from e
                self.create_sql_table_if_not_exists()
            elif self.databasename == "redis":
                log.debug("Redis database url provided.")
                if not is_redis_installed:
                    raise ImportError(
                        "redis is not installed. Please install it using pip install redis."
                    )
                if isinstance(self.database, redis.Redis):
                    self.client = self.database
                else:
                    try:
                        self.client = redis.Redis.from_url(self.database)
                    except Exception as e:
                        log.error(
                            "Redis database url is invalid. Unable to connect to the database."
                        )
                        raise InvalidDatabaseUrl(
                            "Invalid database url. Please check the url and try again.",
                            e,
                        ) from e
            else:
                log.error("Invalid database url provided.")
                raise InvalidDatabaseUrl(
                    "Invalid database url. Please check the url and try again."
                )
            self.load_from_database()
        if self.env_file:
            log.debug("Environment file provided.")
            if not os.path.exists(self.env_file):
                log.error("Environment file not found.")
                raise FileNotFoundError(
                    "Environment file not found. Please check the file path and try again."
                )
            self.load_env_from_file()

    def create_sql_table_if_not_exists(self):
        """Create SQL table if not exists.

        Parameters:
            None
        Returns:
            None"""
        if self.databasename not in ["sql", "sqlite"]:
            raise NoDatabaseUrlSupplied(
                "No database url supplied. Please supply a database url."
            )
        log.debug("Creating SQL table if not exists.")
        cursor = self.client.cursor()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {self.collection_or_table_name} (key TEXT PRIMARY KEY, value TEXT)"
        )
        self.client.commit()

    def load_env_from_file(self):
        """Load environment variables from file.

        Parameters:
            None
        Returns:
            None"""
        if not self.env_file:
            raise FileNotFoundError(
                "No environment file supplied. Please supply an environment file."
            )
        if self.env_file.endswith(".env"):
            self.load_env_from_env_file()
        elif self.env_file.endswith(".json"):
            self.load_env_from_json_file()
        elif self.env_file.endswith(".yaml"):
            self.load_env_from_yaml_file()
        else:
            log.error("Invalid environment file provided.")
            raise InvalidEnvFile(
                "Invalid environment file. Please check the file and try again."
            )

    def load_env_from_json_file(self):
        """Load environment variables from json file.

        Parameters:
            None
        Returns:
            None"""
        log.debug("Loading environment variables from json file.")
        file_path = os.path.abspath(self.env_file)
        try:
            with open(file_path, "r") as file:
                content = file.read()
                json_content = json.loads(content)
                for key, value in json_content.items():
                    os.environ[key.upper()] = value
        except Exception as e:
            raise InvalidEnvFile(
                "Invalid environment file. Please check the file and try again.", e
            ) from e

    def load_env_from_yaml_file(self):
        """Load environment variables from yaml file.

        Parameters:
            None
        Returns:
            None"""
        log.debug("Loading environment variables from yaml file.")
        file_path = os.path.abspath(self.env_file)
        try:
            with open(file_path, "r") as file:
                content = file.read()
                yaml_content = yaml.safe_load(content)
                for key, value in yaml_content.items():
                    os.environ[key.upper()] = value
        except Exception as e:
            raise InvalidEnvFile(
                "Invalid environment file. Please check the file and try again.", e
            ) from e

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
            with open(file_path, "r") as file:
                content = file.read()
                matches = pattern.findall(content)
                for key, quoted_value, unquoted_value in matches:
                    value = quoted_value or unquoted_value
                    os.environ[key.upper()] = value.replace("\n", "")
        except Exception as e:
            raise InvalidEnvFile(
                "Invalid environment file. Please check the file and try again.", e
            ) from e

    def load_from_database(self):
        """Load environment variables from database.

        Parameters:
            None
        Returns:
            None"""
        if not self.database:
            raise NoDatabaseUrlSupplied(
                "No database url supplied. Please supply a database url."
            )
        log.debug("Loading environment variables from database.")
        if self.databasename == "mongo":
            log.debug("Loading environment variables from MongoDB database.")
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            for doc in collection.find():
                os.environ[doc["key"].upper()] = doc["value"]
        elif self.databasename in ["sql", "sqlite"]:
            log.debug("Loading environment variables from SQL database.")
            with self.client:
                cursor = self.client.cursor()
                result = cursor.execute(
                    f"SELECT * FROM {self.collection_or_table_name}"
                )
                for row in result:
                    os.environ[row[0].upper()] = row[1]
        elif self.databasename == "redis":
            log.debug("Loading environment variables from Redis database.")
            for key in self.client.keys():
                os.environ[key.decode("utf-8").upper()] = self.client.get(key).decode(
                    "utf-8"
                )

    def get_env_from_database(self, key):
        """Get environment variable from database.

        Parameters:
            key (str): Environment variable key.
        Returns:
            str: Environment variable value."""
        self._extracted_from_update_env_in_database_8(key)
        log.debug(f"Getting environment variable {key} from database.")
        if self.databasename == "mongo":
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            if result := collection.find_one({"key": key}):
                return result["value"]
            else:
                raise None
        elif self.databasename in ["sql", "sqlite"]:
            with self.client:
                cursor = self.client.cursor()
                result = cursor.execute(
                    f"SELECT * FROM {self.collection_or_table_name} WHERE key=?", (key,)
                )
                return result.fetchone()[1] if result.fetchone() else None
        elif self.databasename == "redis":
            result = self.client.get(key)
            return result.decode("utf-8") if result else None

    def get_all_env_from_database(self):
        """Get all environment variables from database.

        Parameters:
            None
        Returns:
            dict: Environment variables."""
        if not self.database:
            raise NoDatabaseUrlSupplied(
                "No database url supplied. Please supply a database url."
            )
        log.debug("Getting all environment variables from database.")
        if self.databasename == "mongo":
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            return collection.find()
        elif self.databasename in ["sql", "sqlite"]:
            with self.client:
                cursor = self.client.cursor()
                return cursor.execute(f"SELECT * FROM {self.collection_or_table_name}")
        elif self.databasename == "redis":
            return self.client.keys()

    def load_env_to_database(self, key, value):
        """Load environment variable to database.

        Parameters:
            key (str): Environment variable key.
            value (str): Environment variable value.
        Returns:
            None"""
        self._extracted_from_update_env_in_database_8(key)
        if self.databasename == "mongo":
            log.debug(
                f"Loading environment variable {key}={value} to MongoDB database."
            )
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            collection.insert_one({"key": key, "value": value})
        elif self.databasename in ["sql", "sqlite"]:
            log.debug(f"Loading environment variable {key}={value} to SQL database.")
            with self.client:
                cursor = self.client.cursor()
                cursor.execute(
                    f"INSERT OR REPLACE INTO {self.collection_or_table_name} (key, value) VALUES (?, ?)",
                    (key, value),
                )
        elif self.databasename == "redis":
            log.debug(f"Loading environment variable {key}={value} to Redis database.")
            self.client.set(key, value)
        os.environ[key.upper()] = value

    def delete_env_from_database(self, key):
        """Delete environment variable from database.

        Parameters:
            key (str): Environment variable key.
        Returns:
            None"""
        self._extracted_from_update_env_in_database_8(key)
        log.debug(f"Deleting environment variable {key} from database.")
        if self.databasename == "mongo":
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            collection.delete_one({"key": key})
        elif self.databasename in ["sql", "sqlite"]:
            with self.client:
                cursor = self.client.cursor()
                # Check if the key exists in the database
                result = cursor.execute(
                    f"SELECT * FROM {self.collection_or_table_name} WHERE key=?", (key,)
                )
                if not result.fetchone():
                    raise KeyError(f"Key {key} not found in the database.")
                cursor.execute(
                    f"DELETE FROM {self.collection_or_table_name} WHERE key=?", (key,)
                )
        elif self.databasename == "redis":
            self.client.delete(key)
        del os.environ[key.upper()]

    def update_env_in_database(self, key, value):
        """Update environment variable in database.

        Parameters:
            key (str): Environment variable key.
            value (str): Environment variable value.
        Returns:
            None"""
        self._extracted_from_update_env_in_database_8(key)
        if self.databasename == "mongo":
            db = self.client.envrx
            collection = db[self.collection_or_table_name]
            collection.update_one({"key": key}, {"$set": {"value": value}})
        elif self.databasename in ["sql", "sqlite"]:
            with self.client:
                cursor = self.client.cursor()
                result = cursor.execute(
                    f"SELECT * FROM {self.collection_or_table_name} WHERE key=?", (key,)
                )
                if not result.fetchone():
                    self.load_env_to_database(key, value)
                else:
                    cursor.execute(
                        f"UPDATE {self.collection_or_table_name} SET value=? WHERE key=?",
                        (value, key),
                    )
        elif self.databasename == "redis":
            self.client.set(key, value)
        os.environ[key.upper()] = value

    # TODO Rename this here and in `get_env_from_database`, `load_env_to_database`, `delete_env_from_database` and `update_env_in_database`
    def _extracted_from_update_env_in_database_8(self, key):
        if not self.database:
            raise NoDatabaseUrlSupplied(
                "No database url supplied. Please supply a database url."
            )
        if type(key) not in str:
            raise TypeError("Invalid key type. Please provide a valid key.")
        if " " in key:
            raise ValueError("Keys cannot contain spaces. Please provide a valid key.")
