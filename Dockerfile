# Use an official Python runtime as a base image
FROM python:3.11.5-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the backend directory contents into the container at /app
COPY ./backend /app

# Install any needed packages specified in requirements.txt
# Ensure your requirements.txt is accessible; adjust path if it's outside backend
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables for the production environment
ENV FLASK_ENV=production

# Run app.py when the container launches using Gunicorn
CMD ["gunicorn", "--workers=3", "--bind", "0.0.0.0:5000", "app:app"]
