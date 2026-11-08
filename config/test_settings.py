from .settings import *

# Use a temporary SQLite database for automated tests.
# The actual application continues using MySQL.

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
#Allow Django test client hostnames.
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
