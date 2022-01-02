# base image
FROM python:3.9-buster as base

# build stage
FROM base as builder
# create install folder
RUN mkdir /install
# get requirements.txt
COPY requirements.txt /requirements.txt
# upgrade pip and install all packages
RUN pip install --upgrade pip && \
pip install --target=/install -r /requirements.txt

# run stage
FROM base
# get installed packages from previous stage
COPY --from=builder /install /usr/local/lib/python3.9
# copy project
COPY . /app
# run project
CMD ["python", "/app/manage.py", "runserver", "0.0.0.0:8000"]