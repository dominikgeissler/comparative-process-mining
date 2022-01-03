# base image
FROM python:3.9-buster as base

# build stage
FROM base as builder
# get requirements.txt
COPY requirements.txt /requirements.txt
# upgrade pip and install all packages
RUN mkdir /install && \ 
pip install --upgrade pip && \
pip install --target=/install -r /requirements.txt

# run stage
FROM base
# get installed packages from previous stage
COPY --from=builder /install /usr/local/lib/python3.9
# make app folder
RUN mkdir /app
# copy project
COPY . /app
WORKDIR /app
# run project
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]