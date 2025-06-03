FROM python:latest

WORKDIR /usr/local/server
COPY . .
RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", ":8080", "-w", "4", "app:app"]
