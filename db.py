import pathlib
import pickle

DATABASEDIRECTORY = pathlib.Path("database")

databases = {}


class Database:
    def __init__(self, name):
        self.file: pathlib.Path = DATABASEDIRECTORY / name
        self.name = name

        if not self.file.exists():
            with open(self.file, "wb") as f:
                pickle.dump({}, f)

        with open(self.file, "rb") as f:
            try:
                self.database = pickle.load(f)
            except EOFError:
                self.database = {}

    def getrow(self, rowname: str, default=None) -> dict:
        """Get a row by its key and return its value.

        :param rowname: Row of the database to retrieve.
        :param default: Will be returned if the key does not exist.
        :return: The dict held at the row.
        """
        if rowname in self.database:
            return self.database[rowname].copy()
        else:
            return default

    def updaterow(self, rowname: str, data: dict):
        """Update a row with a new value by its key.

        Raises a ValueError if the data is not a dict.

        :param rowname: Row of the database to update. Will be created if doesn't already exist.
        :param data: The data to update the row with.
        """
        if type(data) != dict:
            raise ValueError("Data type provided was not a dict.")

        self.database[rowname] = data

    def delrow(self, rowname: str):
        """Delete a row of the database.

        Raises a ValueError if the row does not exist.

        :param rowname: Row to be deleted.
        """
        if rowname in self.database:
            del self.database[rowname]
        else:
            raise ValueError(f"Row does not exist with name: {rowname}")

    def getname(self) -> str:
        """Returns the name of the database."""
        return self.name

    def _updatefile(self):
        with open(self.file, "wb") as f:
            pickle.dump(self.database, f)


def _updateindex():
    strtowrite = ""
    for db in databases:
        strtowrite += db + "\n"


def createdb(dbname: str):
    """
    Create a new database and add it to the index.

    Raises a KeyError if database already exists.

    :param dbname: Name of the database.
    """
    if db in databases:
        raise KeyError(f"Database already exists with name: {dbname}")
    newdb = Database(db)
    databases[db] = newdb
    _updateindex()


def deletedb(dbname: str):
    if db not in databases:
        raise KeyError(f"Database does not exist with name: {dbname}")
    del databases[db]
    _updateindex()


with open(DATABASEDIRECTORY / ".index", "r") as f:
    dbtobeparsed = f.read().strip().split("\n")

for db in dbtobeparsed:
    createdb(db)

