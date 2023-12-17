# Copyright (C) 2023-present by StarkGang@Github, < https://github.com/StarkGang >.
#
# This file is part of < https://github.com/StarkGang/Envrx > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/StarkGang/Envrx/blob/main/LICENSE >
#
# All rights reserved.

class InvalidEnvFile(Exception):
    pass

class InvalidDatabaseUrl(Exception):
    pass

class InvalidLogLevel(Exception):
    pass

class InvalidCollectionOrTableName(Exception):
    pass


class NoDatabaseUrlSupplied(Exception):
    pass