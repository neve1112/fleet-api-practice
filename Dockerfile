FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.main:create_app
EXPOSE 5000

CMD ["flask", "run", "--port", "5000"]
