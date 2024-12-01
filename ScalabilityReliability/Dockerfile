# Dockerfile for service1
FROM python:3.10-slim

WORKDIR /ScalabilityReliability

COPY . /ScalabilityReliability

RUN pip install --no-cache-dir --timeout=100 --index-url https://pypi.org/simple -r requirements.txt

EXPOSE 5004  

CMD ["flask", "run", "--host=0.0.0.0", "--port=5004"]
