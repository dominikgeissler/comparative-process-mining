# image
FROM python:3.8

# set enviroment variable
ENV DockerHOME=/home/app/webapp

# create folder (and path)
RUN mkdir -p ${DockerHOME}

# set as workdir
WORKDIR ${DockerHOME}

# env variables for python

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
ENV PYTHONDONTWRITEBYTECODE 1

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED
ENV PYTHONUNBUFFERED 1

# set up pip and dependencies
RUN pip install --upgrade pip

# copy current files to created work directory
COPY . ${DockerHOME}

# install all dependencies from dependency list
RUN pip install -r dependencies.txt

# open django port
EXPOSE 8000

CMD ["/bin/bash", "-c", "--", "while true; do sleep 30; done;"]
# start django server
# CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
