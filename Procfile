web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 2
worker: celery -A core worker -l info --concurrency=2
beat: celery -A core beat -l info --pidfile=/tmp/celerybeat.pid
