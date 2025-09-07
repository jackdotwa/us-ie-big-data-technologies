# Start from a standard Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install the cassandra-driver
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python scripts and the CQL schema file into the container
COPY loader.py /app
COPY main.py /app
# FIX: The schema.cql file was missing and must be copied into the image
COPY schema.cql /app

# The command to run when the container starts
CMD ["python", "main.py"]
