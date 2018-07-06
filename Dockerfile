
FROM python:alpine

LABEL description="Panos Bootstrap Builder Tool"
LABEL version="0.3"
LABEL maintainer="nembery@paloaltonetworks.com"

WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN apk add --update cdrkit

COPY bootstrapper /app/bootstrapper
COPY tests /app/tests

EXPOSE 5000
ENV FLASK_APP=/app/bootstrapper/bootstrapper.py

#ENTRYPOINT ["python"]
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
