import pathlib
import pickle
from passlib.hash import sha256_crypt as sha256
from json import dumps
from flask import jsonify

DATABASEDIRECTORY = pathlib.Path("database")
DATABASEINDEX = DATABASEDIRECTORY / ".index"

databases = {}
# TODO: Heroku integration


class Song:
    """Create a Song object."""
    def __init__(self, songname: str, songurl: str, duration: str, author: str):
        self.name = songname
        self.url = songurl
        self.duration = duration
        self.author = author

    def getstream(self):
        pass
        # todo: Not entirely sure. Does can the stream url be passed properly to the mobile app?

    def tojsondict(self):
        return dict(songname=self.name, songurl=self.url, duration=self.duration, author=self.author)

    @classmethod
    def songfromjson(cls, json: dict):
        if all((k in json for k in ("songname", "songurl", "duration", "author"))):
            return Song(json['songname'], json['songurl'], json['duration'], json['author'])


class Playlist:
    """Create a playlist object, using a tuple of songs."""
    def __init__(self, name, songs: tuple = ()):
        self.songs: tuple[Song] = tuple(songs)
        self.name = name

    def getname(self):
        return self.name

    def getsongs(self):
        return self.songs

    def findsong(self, songname):
        for song in self.songs:
            if song.name == songname:
                return song
        return None

    def tojsondict(self):
        return dict(playlistname=self.name, songs=tuple(i.tojsondict() for i in self.songs))

    @classmethod
    def playlistfromjson(cls, json: dict):
        """Construct a playlist object from a json dict.

        JSON must contain a string playlistname, and a list/tuple of valid songs."""
        if all((k in json for k in ("playlistname", "songs"))):
            return Playlist(json['playlistname'], (Song.songfromjson(i) for i in json['songs']))
    # todo: Maybe needs functions for adding new songs. Alternatively, new playlist made whenever user updated.


class User:
    def __init__(self, name, password, apikey, playlists: list[Playlist] = ()):
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self._name = name
        self.apikey = apikey
        if playlists:
            if type(playlists[0]) is dict:
                playlists = list(map(lambda a: Playlist.playlistfromjson(a), playlists))
        self.playlists: list[Playlist] = list(playlists)
        self.hashpw = password

    def get_id(self):
        return self._name

    def getname(self):
        return self._name

    def setplaylists(self, playlists):
        self.playlists = playlists

    def getplaylists(self):
        return self.playlists

    def getjsonplaylists(self):
        return tuple(i.tojsondict() for i in self.playlists)

    def tojson(self):
        return {'username': self.getname(), 'password': self.hashpw, 'apikey': self.apikey, 'playlists': self.getjsonplaylists()}

    def validate(self, pw):
        return sha256.verify(pw, self.hashpw)
    # TODO: Probably need to add more functions here at some point


class Database:
    def __init__(self, name):
        self.file: pathlib.Path = DATABASEDIRECTORY / name
        self.name = name

        if not self.file.exists():
            with open(self.file, "wb") as f:
                pickle.dump({}, f)

        with open(self.file, "rb") as f:
            try:
                tempbase = pickle.load(f)
                self.database = {}

                for i in tempbase:
                    v = tempbase[i]
                    self.database[i] = User(v['username'], v['password'], v['apikey'], v['playlists'])

            except EOFError:
                self.database = {}

    def getrow(self, rowname: str, default=None) -> User:
        """Get a row by its key and return its value.

        :param rowname: Row of the database to retrieve.
        :param default: Will be returned if the key does not exist.
        :return: The dict held at the row.
        """
        if rowname in self.database:
            return self.database[rowname]
        else:
            return default

    def getrows(self, ):
        return tuple(i for i in self.database)

    def updaterow(self, rowname: str, data):
        """Update a row with a new value by its key.

        :param rowname: Row of the database to update. If doesn't exist, KeyError raised.
        :param data: The data to update the row with. If None, ValueError raised.
        """
        if rowname not in self:
            raise KeyError("Can't update a non-existent row.")
        if data is None:
            raise ValueError("Can't supply None data.")
        self.database[rowname] = data
        self._updatefile()

    def createrow(self, rowname, data=None):
        """Create a new row.

        :param rowname: Name of row to be created. If exists, KeyError raised.
        :param data: Data to set.
        """
        if rowname in self:
            raise KeyError("Can't create row that already exists.")
        self.database[rowname] = ({} if not data else data)
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
            pickle.dump({i: self.database[i].tojson() for i in self.database}, f)

    def __contains__(self, item):
        return bool(self.getrow(item, False))


class AccessRow:
    def __init__(self, database: Database, row: str):
        self.database = database
        self.value = database.getrow(row)
        self.row = row
        self.newvalue = self.value

    def __enter__(self):
        return self.value

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.database.updaterow(self.row, self.newvalue)


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
    database = databases[dbname]
    database.file.unlink()
    del databases[dbname]
    _updateindex()


if not DATABASEINDEX.exists():
    with open(DATABASEINDEX, "w") as f:
        pass

with open(DATABASEINDEX, "r") as f:
    dbtobeparsed = f.read().splitlines()

for db in dbtobeparsed:
    databases[db] = createdb(db)

userdb = databases['users']

if __name__ == "__main__":



    pass
    testsong = Song("testname", "google.com", "durat23ion", "aut231hor")
    testplaylists = [Playlist("testplaylist", [testsong]), Playlist("testplaylist2", [testsong])]
    newuser = User("Taz", sha256.hash("password"), "testkey")

    try:
        userdb.createrow("Taz", newuser)
    except Exception:
        userdb.updaterow("Taz", newuser)


    with AccessRow(userdb, "Taz") as data:
        data.setplaylists(testplaylists)


