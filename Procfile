release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn the_kit_box.wsgi