# Dockerfile for service2
FROM python:3.10-slim

WORKDIR /service2

COPY . /service2

RUN pip install --no-cache-dir --timeout=100 --index-url https://pypi.org/simple -r requirements.txt

EXPOSE 5001  

CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]
