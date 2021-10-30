# base image  
FROM python:3.9-slim   
# setup environment variable  
ENV DockerHOME=/home/app/webapp  

# set work directory  
RUN mkdir -p $DockerHOME  

# where your code lives  
WORKDIR $DockerHOME  

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  
# install dependencies  
RUN pip install --upgrade pip  
# copy whole project to your docker home directory. 
COPY requirements.txt ${DockerHOME}

RUN /usr/local/bin/python -m pip install --upgrade pip  
RUN pip install -r requirements.txt  


COPY . $DockerHOME  
# run this command to install all dependencies
# port where the Django app runs  
EXPOSE 8000  
# start server 
CMD ["/bin/bash", "-c", "--", "while true; do sleep 30; done;"]
# CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]