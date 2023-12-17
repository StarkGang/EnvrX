# Copyright (C) 2023-present by StarkGang@Github, < https://github.com/StarkGang >.
#
# This file is part of < https://github.com/StarkGang/Envrx > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/StarkGang/Envrx/blob/main/LICENSE >
#
# All rights reserved.

def check_if_package_installed(package_name: str) -> bool:
    """Check if a package is installed."""
    import importlib
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


def guess_which_database_from_url(url: str) -> str:
    """Guess which database is being used from the url."""
    if url.startswith('mongodb'):
        return 'mongo'
    elif url.endswith(".db"):
        return 'sqlite'
    elif url.startswith('postgresql'):
        return 'sql'
    elif url.startswith('redis'):
        return 'redis'
    else:
        return None