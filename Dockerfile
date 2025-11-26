FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV APP_ENV dev

# Create the working directory
WORKDIR /app

COPY . /app

# Install required packages
RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8080
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]