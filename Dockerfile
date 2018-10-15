
FROM python:alpine

LABEL description="Panos Bootstrap Builder Tool"
LABEL version="0.3"
LABEL maintainer="nembery@paloaltonetworks.com"

WORKDIR /app
RUN apk add --update --no-cache cdrkit
RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN apk del gcc musl-dev python3-dev libffi-dev openssl-dev
COPY bootstrapper /app/bootstrapper
COPY tests /app/tests

EXPOSE 5000
ENV FLASK_APP=/app/bootstrapper/bootstrapper.py
ENV PATH /app/bootstrapper:$PATH

#ENTRYPOINT ["python"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
