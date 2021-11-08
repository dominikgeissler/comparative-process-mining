# image
# FROM python:3.9
FROM pm4py/pm4py-core:latest
# ----
# set enviroment variables
# ----
ENV DockerHOME=/home/app/webapp

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
ENV PYTHONDONTWRITEBYTECODE 1

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED
ENV PYTHONUNBUFFERED 1
# ----

# create path
RUN mkdir -p ${DockerHOME}

# set as workdir
WORKDIR ${DockerHOME}

COPY requirements.txt ${DockerHOME}

# update pip and install dependencies
RUN pip install --upgrade pip \
&& pip install -r requirements.txt

# copy current files to created work directory
COPY . ${DockerHOME}

# open django port
EXPOSE 8000

# idle
CMD ["/bin/bash", "-c", "--", "while true; do sleep 30; done;"]
# start django server
# CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
