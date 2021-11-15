# Comparative Process Mining
## Setup
### Requirements
[docker-desktop](https://www.docker.com/products/docker-desktop)

### Start project
* Build the container using `docker build . -t <name>` 
* Run the container using `docker run -d -p 8000:8000 <name>`
* Visit `localhost:8000`. The project is now available.

## Project structure
````
├── Dockerfile
├── README.md
├── cpm
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── helpers
│   ├── dfg_helper.py
│   ├── g6_helpers.py
│   └── metrics_helper.py
├── logs
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── media
├── requirements.txt
├── static
│   ├── css
│   ├── img
│   └── js
└── templates
    ├── base.html
    ├── compare.html
    ├── graph.html
    ├── home.html
    ├── manage_logs.html
    ├── metrics.html
    ├── navigation.html
    ├── select_comparisons.html
    └── select_logs.html
````
