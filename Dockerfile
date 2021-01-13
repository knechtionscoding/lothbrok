FROM python:3.9.1-alpine

RUN apk update && \
    apk add --no-cache git=2.26.2-r0

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./routes.py" ]
