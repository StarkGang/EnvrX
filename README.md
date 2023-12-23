# ENVRX

`ENVRX` is a Python class designed to manage environment variables seamlessly, providing support for various databases such as MongoDB, SQL, and Redis.
It also supports env files (let it be .json, .env or even .yaml)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Class Initialization](#class-initialization)
- [Loading Environment](#loading-environment)
- [Database Operations](#database-operations)
- [Examples](#examples)
- [License](#license)

## Installation

```bash
pip install envrx
```

- If you are using mongodb for database:
```pip install pymongo```
- or If using postgreSQL
```pip install psycopg2```
- or If using Redis
```pip install redis```
- Sqlite uses ```sqlite3```


## Usage

```python
from envrx import ENVRX
import os

# Initialize ENVRX with optional parameters
env_manager = ENVRX(env_file=".env", database="mongodb://localhost:27017", collection_or_table_name="env_variables")

# or pass a database client client
client = MongoClient(...)
env_manager = ENVRX(env_file=".env", database=client, collection_or_table_name="env_variables")

# Initialize the environment
env_manager.initialize()
# Access loaded env
print(os.getenv("env_from_db_or_file"))
```

## Class Initialization

- `env_file` (Optional): Path to the environment file.
- `database` (Optional): Database URL for MongoDB, SQL, or Redis.
- `collection_or_table_name` (Optional): Name of the collection or table in the database.

```python
# Example initialization
env_manager = ENVRX(env_file=".env", database="mongodb://localhost:27017", collection_or_table_name="env_variables")
# or if you have a database client
client = MongoClient(...)
env_manager = ENVRX(env_file=".env", database=client, collection_or_table_name="env_variables")
```

## Loading Environment

- `initialize()`: Initializes the class and loads environment variables from both the specified file and database.

```python
# Example loading environment
env_manager.initialize()
```

- Please note that, all variables will be auto loaded when running this and can be accessed through ```os.environ.get("foo_bar")```

## Database Operations

- `load_from_database()`: Loads environment variables from the specified database.

- `get_env_from_database(key)`: Gets a specific environment variable from the database.

- `get_all_env_from_database()`: Gets all environment variables from the database.

- `load_env_to_database(key, value)`: Loads a new environment variable to the database.

- `delete_env_from_database(key)`: Deletes an environment variable from the database.

- `update_env_in_database(key, value)`: Updates an environment variable in the database.

```python
# Example database operations
value = env_manager.get_env_from_database("KEY_NAME")
env_manager.load_env_to_database("NEW_KEY", "NEW_VALUE")
env_manager.delete_env_from_database("OLD_KEY")
env_manager.update_env_in_database("EXISTING_KEY", "UPDATED_VALUE")
```

## Examples

Database wise Examples can be found [here](https://github.com/StarkGang/EnvrX/tree/main/examples).


## License

This project is licensed under the [GPL V3.0](https://github.com/StarkGang/EnvrX/blob/main/LICENSE).
