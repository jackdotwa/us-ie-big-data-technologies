# Start from the official Cassandra image
FROM cassandra:latest

# Switch to the root user to install packages
USER root

# Update, install Git, Python, and Pip, then clean up
RUN apt-get update && \
    apt-get install -y git python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Switch back to the default cassandra user
USER cassandra
