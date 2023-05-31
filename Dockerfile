# start by pulling the python image
FROM python:3.10-alpine

RUN pip install --upgrade setuptools
RUN pip install --upgrade pip
RUN pip install virtualenv

ENV VIRTUAL_ENV=/venv
RUN virtualenv venv -p python3

ENV PATH="VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
ADD . /app

# install dependencies
RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev
RUN pip install -r requirements.txt

# expose port
EXPOSE 80

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["app.py" ]


# run application
# CMD ["python", "app_light.py"]