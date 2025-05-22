# django-a2a

![Django 5.0](https://github.com/ppak10/django-a2a/actions/workflows/django_5.yml/badge.svg)
![Django 4.0](https://github.com/ppak10/django-a2a/actions/workflows/django_4.yml/badge.svg)

## Installation
### 1. Install `django-a2a` via pip
```bash
pip install django-a2a
```
### 2. Add `django_a2a` in `INSTALLED_APP` within `settings.py`
```python
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Django A2A
    'django_a2a',
]
```

### 3. Migrate database.
```bash
python manage.py migrate
```

## Contributing

## Testing
### Using Act to run GitHub Actions locally
#### Ubuntu
```bash
curl --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash && ./bin/act
```