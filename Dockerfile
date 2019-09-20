# start from an official image
FROM python:3.6.9

# arbitrary location choice: you can change the directory
RUN mkdir -p /opt/services/djangoapp/src
WORKDIR /opt/services/djangoapp/src

# install our two dependencies
RUN pip install gunicorn django django-crispy-forms social-auth-app-django path.py stripe pytz Pillow

# copy our project code
COPY . /opt/services/djangoapp/src

# expose the port 8000
EXPOSE 8000

# define the default command to run when starting the container
CMD ["gunicorn", "--chdir", "mysite", "--bind", ":8000", "mysite.wsgi:application"]
#CMD ["python","manage.py","runserver","0:8000"]
RUN python /opt/services/djangoapp/src/manage.py makemigrations
RUN python /opt/services/djangoapp/src/manage.py migrate
