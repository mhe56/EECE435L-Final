# Dockerfile for service3
FROM python:3.10-slim

WORKDIR /service3

COPY . /service3

RUN pip install --no-cache-dir --timeout=100 --index-url https://pypi.org/simple -r requirements.txt

EXPOSE 5002  

CMD ["flask", "run", "--host=0.0.0.0", "--port=5002"]
