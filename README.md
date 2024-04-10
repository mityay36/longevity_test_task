# Test task for longevity 

This project aims to provide a custom authentication system using email as the backend and integrating Celery for asynchronous task processing.

## Technologies Used

- Python 3.9
- Django 2.2.16
- Django Rest Framework 3.12.4
- Celery 5.3.5
- Redis 5.0.3
- PostgreSQL
- Docker

## Installation of the project:
Clone the repository and change into it on the command line:

	git clone https://github.com/mityay36/longevity_test_task/

Make your own .env file in main directory. All required variables are listed in .env.example

#### Start Docker Compose in daemon mode

    docker-compose -f docker-compose.yml up --build

#### Make migrations and collect static of your project
    docker-compose -f docker-compose.yml exec backend python manage.py makemigrations
    docker-compose -f docker-compose.yml exec backend python manage.py migrate
    docker-compose -f docker-compose.yml exec backend python manage.py collectstatic
    docker-compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/

#### Perform your own superuser
    docker-compose -f docker-compose.yml exec backend python manage.py createsuperuser

### Congrats! Now you can access the application at [localhost](http://localhost:8000)

## Author
[Dmitry Pokrovsky](https://github.com/mityay36)