import cylinder  # pip install cylinder
import waitress  # pip install waitress

import sqlite3
import json
from collections import UserDict
import secrets


def main():
    app = cylinder.get_app(triage)
    waitress.serve(app, host="127.0.0.1", port=80)


def triage(request, response):
    session_id = request.cookies.get("session_id") or secrets.token_urlsafe(32)
    response.set_cookie("session_id", session_id)
    session = SessionDict(session_id)
    return "my_webapps", "webapp1", {"session": session}


class SessionDict(UserDict):
    def __init__(self, uid):
        self.uid, self.conn = uid, sqlite3.connect("sessions.sqlite")
        self.conn.execute("CREATE TABLE IF NOT EXISTS store (uid TEXT PRIMARY KEY, data TEXT)")
        row = self.conn.execute("SELECT data FROM store WHERE uid=?", (self.uid,)).fetchone()
        super().__init__(json.loads(row[0]) if row else {})

    def _save(self):
        self.conn.execute("INSERT OR REPLACE INTO store VALUES (?,?)", (self.uid, json.dumps(self.data)))
        self.conn.commit()

    def __setitem__(self, k, v):
        super().__setitem__(k, v)
        self._save()

    def __delitem__(self, k):
        super().__delitem__(k)
        self._save()


if __name__ == "__main__":
    main()
