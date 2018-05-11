# demo-bottle-sqlite-bug

Repository for showing the erroneous behaviour in https://github.com/bottlepy/bottle-sqlite/issues/21

This issue is found also in:

 - bottle-redis
 - bottle-mongo

And probably other plugings that write to some database.
This is particularily annoying because usually when you put data into a database
you want to make sure the request comes from a trusted source.

If you implement a decorator like:
```
@app.route('/secret/:item')
@valid_user()
def secret(item, db):
      ...
```

The `valid_user()` plugin will throw and error like

```
Traceback (most recent call last):
  File "/home/oznt/Software/bottlesession/bottle.py", line 998, in _handle
    out = route.call(**args)
  File "/home/oznt/Software/bottlesession/bottle.py", line 1999, in wrapper
    rv = callback(*a, **ka)
  File "/home/oznt/Software/bottlesession/bottlesession.py", line 48, in check_auth
    return handler(*a, **ka)
TypeError: secret() missing 1 required positional argument: 'db'
```

Which hides the fact that the check for the keyword `db` is failing, although, the callable does have
the keyword `db`.

The reason the check fails, is because `_callback` is no longer the original
function. this is solved in python3.3 with

```
inspect.signature(callable, *, follow_wrapped=True)
```
In earlier versions of python you would have to use `functools.wraps` your
original function and check if the callback has the attribute ``__wrapped__``.
This will only work for 1 level, if you do :

```
@app.route('/secret/:item')
@valid_user()
@has_permission()
def secret(item,db):
       ...
```
you would have to check for `callback.__wrapped__.__wrapped__`, or for each level of decoration add one `__wrapped__`.

The solution is to replace the check from:

```
argspec = inspect.getargspec(_callback)
```

To

```
params = inspect.signature(_callback).parameters

if keyword not in params:
    return callback

```
