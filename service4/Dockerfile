# Dockerfile for service4
FROM python:3.10-slim

WORKDIR /service4

COPY . /service4

RUN pip install --no-cache-dir --timeout=100 --index-url https://pypi.org/simple -r requirements.txt

EXPOSE 5003  

CMD ["flask", "run", "--host=0.0.0.0", "--port=5003"]
