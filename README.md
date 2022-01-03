# Comparative Process Mining
## Setup
### Requirements
[docker-desktop](https://www.docker.com/products/docker-desktop)

### Start project (Docker)
* Open a command line in the location you cloned this repo to
* Build the image using `docker build . -t <name>` 
* Run the container using `docker run -d -p 8000:8000 <name>`
* Visit `localhost:8000`. The project is now available.

### Start project (without Docker)
* Install the dependencies with `pip install -r requirements.txt`
* Run `python manage.py runserver 0.0.0.0:8000`
* Visit `localhost:8000`. The project is now available.
* _Note: Dependent on the OS you need to use python3 or pip3 instead of the commands above_

## Project structure
````
├── cpm         Django settings
├── doc         Documentation
├── logs        Main project
├── media       Saved logs
├── static      CSS / JS / Img
└── templates   HTML templates
````
# Further information
* We use the [PEP-8](https://www.python.org/dev/peps/pep-0008/) coding convention.
