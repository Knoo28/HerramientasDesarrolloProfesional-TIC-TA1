FROM python:3.14-alpine
WORKDIR /app
COPY app.py .
EXPOSE 4200
CMD ["python", "-u", "app.py"]