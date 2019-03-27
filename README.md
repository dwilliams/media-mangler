media-mangler
=============

Manager of backup media for media backups.

Commands for development
------------------------

1. Setup virtual environment:
```
python -m venv venv
```

If there's an error involving ensurepip (usually on Windows using Anaconda Python), run the following:
```
python -m venv venv --without-pip
source test/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
```

2. Install the package as editable:
```
pip install -e .
```

Instantiate database with alembic.


Run the server.
