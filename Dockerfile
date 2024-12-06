FROM python:3.13

WORKDIR /app
COPY . .
RUN pip install .

EXPOSE 80
CMD ["uvicorn", "inventory:app", "--interface=wsgi", "--host=0.0.0.0", "--port=80"]
