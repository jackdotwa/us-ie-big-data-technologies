
# Getting Started with Cassandra

This guide will help you set up the Cassandra database, populate it with data, and begin working on your assignment.

---
## 🚀 Recommended Setup: Docker Compose

This is the simplest and most reliable way to get started. It handles both the database and the data population in one step.

**1. Launch the Services**

From your terminal, run the following command. This will build the necessary images and start the Cassandra database and the data loader service.

```bash
docker compose up
````

*(Note: If your system uses an older version, you may need the hyphenated command: `docker-compose up`)*

Please be patient, as it takes a few moments for the Cassandra instance to initialize before the `data-loader` can populate it with the wind turbine data.

**2. Verify the Database**

Once the logs slow down, you can check if the database is running and accessible. Open a **new terminal window** and run:

```bash
docker exec -it cassandra-db cqlsh
```

This command gives you direct access to the Cassandra Query Language shell (`cqlsh`), allowing you to run queries against your data. Be sure to read the loader code to see how the data is generated; you can use one of the turbine UUIDs for your queries.

**3. Shut Down the Services**

When you're finished working, stop and remove the containers by pressing `Ctrl+C` in the terminal where compose is running, and then executing:

```bash
docker compose down
```

-----

## 🔧 Alternative Setup Methods

If you have issues with the primary method, these alternatives provide more manual control.

### Method A: Running a Local Script Against a Docker Container

This approach involves running the Cassandra database in Docker and then running the Python data loader script from your local machine.

**1. Start the Cassandra Container**

```bash
docker run --name cassandra-db -p 9042:9042 -d cassandra:latest
```

You can monitor its startup progress with `docker logs -f cassandra-db`.

**2. Prepare Your Local Python Environment**

You'll need to install the required Python libraries. It's best practice to use a virtual environment.

```bash
# Navigate to the assignment directory
cd assignment

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

**3. Configure and Run the Data Loader**

The script needs to know where to find the database. Set the environment variable and then run the script:

```bash
# Tell the script to connect to your local Docker instance
export CASSANDRA_NODES=127.0.0.1

# Run the script to populate the database
python main.py
```

### Method B: All-in-One Development Container

This advanced option is for situations where you cannot install tools locally. It creates a custom Docker image containing Cassandra, Python, and Git.

**1. Create a `Dockerfile`**

Create a file named `Dockerfile` with the following content:

```dockerfile
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
```

**2. Build, Run, and Access the Container**

```bash
# Build the image
docker build -t cassandra-with-tools .

# Run the container in the background
docker run --rm --name cassandra-db -p 9042:9042 -d cassandra-with-tools

# Get a shell inside the running container
docker exec -it cassandra-db /bin/bash
```

**3. Clone the Project Inside the Container**

Once inside the container, you can clone the project and work from there.

```bash
# Navigate to a temporary directory
cd /tmp

# Clone the repository and navigate into the project
git clone [https://github.com/jackdotwa/us-ie-big-data-technologies.git](https://github.com/jackdotwa/us-ie-big-data-technologies.git)
cd us-ie-big-data-technologies/cassandra/
```

-----

## ✅ Submitting Your Assignment

Your task is to modify the `assignment/student.py` file to contain the required parameterized queries.

Ensure this `cassandra` directory is committed and pushed to your course repository for auto-marking. If you are using Method B, you will need to configure Git inside the container to push your changes to your remote repository.

