# Install

```
apt-get install python3 python-virtualenv
```

1. `virtualenv venv`
1. `source venv/bin/activate`
1. `make build`

# Migrate DB

1. `cd python-server`
2. `python`
3. `from server import db`
4. `db.create_all()`
