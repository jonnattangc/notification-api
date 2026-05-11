FROM python:3.12-slim

LABEL MAINTAINER="Jonnattan Griffiths"
LABEL VERSION=1.0
LABEL DESCRIPCION="Python Server Notificaciones"

ENV TZ='UTC'
ENV HOST_BD=''
ENV USER_BD=''
ENV PASS_BD=''
ENV WAZA_BEARER_TOKEN=''
ENV PHONE_ID=''
ENV UUID_WZ=''
ENV AWS_PINPOINT_APP_ID=''

ENV FLASK_APP=app
ENV FLASK_DEBUG=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN addgroup --gid 10101 jonnattan && \
    adduser --home /home/jonnattan --uid 10100 --gid 10101 --disabled-password jonnattan && \
    echo "jonnattan:jonnattan" | chpasswd && \
    mkdir -p /home/jonnattan/.local/bin && \
    chmod -R 755 /home/jonnattan && \
    chown -R jonnattan:jonnattan /home/jonnattan

WORKDIR /home/jonnattan

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /home/jonnattan/app

RUN chown -R jonnattan:jonnattan /home/jonnattan

WORKDIR /home/jonnattan/app

USER jonnattan

EXPOSE 8060

CMD ["python", "main.py", "8060"]

