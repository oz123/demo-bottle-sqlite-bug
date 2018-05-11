#!/usr/bin/env python
import sqlite3

from bottle import HTTPError
import bottle
import bottlesession
# To see the correct plugin comment this line and uncomment the one bellow
from bottle_sqlite import SQLitePlugin
# from bottle_sqlite import SQLitePluginFixed as SQLitePlugin

db = sqlite3.connect('/tmp/test.db')
cur = db.cursor()

# Create table
try:
    cur.execute('''CREATE TABLE items (name text)''')
except sqlite3.OperationalError:
    pass

items = [('foo',), ('bar',), ('baz',)]

cur.executemany("INSERT INTO items VALUES (?)", items)
db.commit()
db.close()


plugin = SQLitePlugin(dbfile='/tmp/test.db')
session_manager = bottlesession.CookieSession()
valid_user = bottlesession.authenticator(session_manager)

app = bottle.Bottle()
app.install(plugin)


@app.route('/')
@app.route('/:name')
@valid_user()
def hello(name='world'):
    return '<h1>Hello %s!</h1>' % name.title()


@app.route('/auth/login')
def login():
    session = session_manager.get_session()
    session['valid'] = True
    session_manager.save(session)
    bottle.redirect(bottle.request.get_cookie('validuserloginredirect', '/'))


@app.route('/show/:item')
def show(item, db):
    row = db.execute('SELECT * from items where name=?', (item,)).fetchone()
    if row:
        return {'item': tuple(row)}
    return HTTPError(404, "Page not found")


"""
This now throws ...

Traceback (most recent call last):
  File "/home/oznt/Software/bottlesession/bottle.py", line 998, in _handle
    out = route.call(**args)
  File "/home/oznt/Software/bottlesession/bottle.py", line 1999, in wrapper
    rv = callback(*a, **ka)
  File "/home/oznt/Software/bottlesession/bottlesession.py", line 48, in check_auth
    return handler(*a, **ka)
TypeError: secret() missing 1 required positional argument: 'db'
"""


@app.route('/secret/:item')
@valid_user()
def secret(item, db):
    row = db.execute('SELECT * from items where name=?', (item,)).fetchone()
    if row:
        return {'item': tuple(row)}
    return HTTPError(404, "Page not found")


if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(app=app)
