# Deploy DriveHub to PythonAnywhere

This project uses `DriveHub.settings`, SQLite, and a top-level `static/` directory.
The local `db.sqlite3` and `media/` uploads are intentionally excluded from Git.

## PythonAnywhere setup

1. Create a PythonAnywhere account and note its username. On the Web tab, create a
   **Manual configuration** web app using Python 3.13. PythonAnywhere currently
   lists Python 3.13 as available, and Django 6.1 supports Python 3.12 and later.
2. In a Bash console, run:

   ```bash
   git clone https://github.com/aswinthachu2006-ux/DriveHub.git
   cd DriveHub
   mkvirtualenv drivehub --python=python3.13
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

   Run `python manage.py createsuperuser` if you need an admin account.
3. Set the Web tab's source code and working directory to
   `/home/YOURUSERNAME/DriveHub`, and the virtualenv to
   `/home/YOURUSERNAME/.virtualenvs/drivehub`.
4. Replace the contents of the Web tab's WSGI file with the following, replacing
   `YOURUSERNAME` and the generated secret. Keep the secret only in this WSGI
   file or another private environment configuration, never in Git:

   ```python
   import os
   import sys

   path = "/home/YOURUSERNAME/DriveHub"
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ["DJANGO_SETTINGS_MODULE"] = "DriveHub.settings"
   os.environ["SECRET_KEY"] = "PUT_A_UNIQUE_RANDOM_SECRET_HERE"
   os.environ["DEBUG"] = "False"
   os.environ["ALLOWED_HOSTS"] = "YOURUSERNAME.pythonanywhere.com,localhost,127.0.0.1"
   os.environ["CSRF_TRUSTED_ORIGINS"] = "https://YOURUSERNAME.pythonanywhere.com"

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

   Generate a key in the Bash console with:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. Add these Static files mappings on the Web tab:

   | URL | Directory |
   | --- | --- |
   | `/static/` | `/home/YOURUSERNAME/DriveHub/staticfiles` |
   | `/media/` | `/home/YOURUSERNAME/DriveHub/media` |

6. Reload the web app and visit `https://YOURUSERNAME.pythonanywhere.com`.

The database will start empty; migrations create its schema. Existing local user
uploads and database records are not in the public repository. SQLite is
available on PythonAnywhere, though its filesystem-backed performance can be
limited under concurrent production traffic.

## Deploying updates

```bash
cd ~/DriveHub
git pull
workon drivehub
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then reload the web app in the Web tab.
