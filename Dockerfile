FROM python:3.9-buster as base

FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && \
pip install --target=/install -r /requirements.txt

FROM base
COPY --from=builder /install /usr/local/lib/python3.9
COPY . /app
WORKDIR /app
CMD ["/bin/bash", "-c", "--", "while true; do sleep 30; done"]