FROM python:3.8.7-slim-buster

# Set environmental variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app

RUN pip install pipenv
RUN python -m venv /opt/venv


#Run to test in local
RUN pip install pip --upgrade && \
    pip install -r requirements.txt && \
    chmod +x entrypoint.sh

CMD ["/app/entrypoint.sh"]