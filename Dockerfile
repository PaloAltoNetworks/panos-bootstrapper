
FROM python:3.6-alpine

LABEL description="Panos Bootstrap Builder Tool"
LABEL version="1.0"
LABEL maintainer="sp-solutions@paloaltonetworks.com"

WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN apk add --update --no-cache cdrkit gcc musl-dev python3-dev libffi-dev openssl-dev && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apk del gcc musl-dev python3-dev libffi-dev openssl-dev

COPY bootstrapper /app/bootstrapper
COPY tests /app/tests

EXPOSE 5000
ENV FLASK_APP=/app/bootstrapper/bootstrapper.py
ENV PATH /app/bootstrapper:$PATH

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
