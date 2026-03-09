release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn the-kit-box.wsgi