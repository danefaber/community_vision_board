# Community Vision Board

A free, ad-free community bulletin board for Valentine, Nebraska. Residents can post volunteering opportunities, help wanted, lost pets, gatherings, and events, and city moderators review posts before they go live.

Built with Django 5.2 and MySQL by team Goons for Intro to Software Engineering.

## Setting up on your computer

You need Python 3 and MySQL installed. On a Mac, if `pip install` fails on `mysqlclient`, run `brew install mysql pkg-config` first.

**1. Clone the repo and open the folder**
```
git clone <repo-url>
cd community_vision_board
```

**2. Make and activate a virtual environment**
```
python3 -m venv venv
source venv/bin/activate
```
You should see `(venv)` at the start of your terminal prompt. Run the `source` line again every time you open a new terminal.

**3. Install the packages**
```
pip install -r requirements.txt
```

**4. Create a local MySQL database**

Log in to MySQL (`mysql -u root -p`) and run:
```sql
CREATE DATABASE community_vision_board;
```

**5. Make your `.env` file**

Copy `.env.example` to a new file called `.env` in the same folder (next to `manage.py`), then fill in your values. Generate your own secret key with:
```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Put it inside single quotes: `SECRET_KEY='your-key-here'`.

`.env` is ignored by git, so your passwords never get pushed. Never commit it.

**6. Set up the database tables and an admin account**
```
python manage.py migrate
python manage.py createsuperuser
```

**7. Run the site**
```
python manage.py runserver
```
- `localhost:8000/admin` lets you log in and add test data (categories, posts, events).
- Emails (like notifications) print in the terminal instead of actually sending.

## Adding a page

1. Write a view function in `board/views.py`.
2. Add a line for it in `board/urls.py`, for example:
   ```python
   path('calendar/', views.calendar, name='calendar'),
   ```
3. Make a template in `board/templates/board/` that starts with:
   ```html
   {% extends "board/base.html" %}
   {% block content %}
     your page here
   {% endblock %}
   ```

## Troubleshooting

| Problem | Fix |
|---|---|
| "SECRET_KEY is missing" | Add `SECRET_KEY` to your `.env`, and make sure `.env` is next to `manage.py` |
| "Bad Request (400)" in the browser | Add `ALLOWED_HOSTS=localhost,127.0.0.1` to your `.env` |
| "unapplied migration(s)" | Run `python manage.py migrate` |
| Can't connect to MySQL | Make sure MySQL is running and the `DB_` values in `.env` are right |
| Can't see `.env` in Finder | Press `Cmd+Shift+.` to show hidden files |
| Commands say "No module named django" | Your venv isn't active. Run `source venv/bin/activate` |
