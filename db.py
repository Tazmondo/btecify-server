import pathlib
import pickle

DATABASEDIRECTORY = pathlib.Path("database")
DATABASEINDEX = DATABASEDIRECTORY / ".index"

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

        :param rowname: Row of the database to update. Will be created if doesn't already exist.
        :param data: The data to update the row with.
        """
        self.database[rowname] = data
        self._updatefile()

    def delrow(self, rowname: str):
        """Delete a row of the database.

        Raises a ValueError if the row does not exist.

        :param rowname: Row to be deleted.
        """
        if rowname in self.database:
            del self.database[rowname]
        else:
            raise ValueError(f"Row does not exist with name: {rowname}")
        self._updatefile()

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

    with open(DATABASEINDEX, "w") as f:
        f.write(strtowrite)


def createdb(dbname: str) -> Database:
    """
    Create a new database and add it to the index.

    Raises a KeyError if database already exists.

    :param dbname: Name of the database.
    :return: Database created.
    """
    if dbname in databases:
        raise KeyError(f"Database already exists with name: {dbname}")
    newdb = Database(dbname)
    databases[dbname] = newdb
    _updateindex()

    return newdb


def deletedb(dbname: str):
    if dbname not in databases:
        raise KeyError(f"Database does not exist with name: {dbname}")
    del databases[dbname]
    _updateindex()


if not DATABASEINDEX.exists():
    with open(DATABASEINDEX, "w") as f:
        pass

with open(DATABASEINDEX, "r") as f:
    dbtobeparsed = f.read().splitlines()

for db in dbtobeparsed:
    databases[db] = createdb(db)

if __name__ == "__main__":
    db = databases['test']
    print(db.database['Taz'])
