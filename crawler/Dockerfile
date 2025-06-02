FROM python:latest

WORKDIR /usr/local/crawl
COPY . .
ADD ./crontabFile /etc/cron.d/crontabFile
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get -y install cron
RUN chmod 0644 /etc/cron.d/crontabFile
RUN crontab /etc/cron.d/crontabFile
RUN chmod +x cron.sh

CMD ["cron", "-f"]
