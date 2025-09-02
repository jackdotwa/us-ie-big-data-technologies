# Start from a standard Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code into the container
COPY main.py .

# The command to run when the container starts
CMD ["python", "main.py"]

