FROM python:3.11-slim

WORKDIR /app
COPY requirements-core.txt /app/
RUN pip install --no-cache-dir -r requirements-core.txt

COPY app /app/app
COPY resources /app/resources
ENV PYTHONPATH=/app

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8080", "--proxy-headers"]
