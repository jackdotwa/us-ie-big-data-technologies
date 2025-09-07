



## Getting Started with Cassandra

After checking this code out, you can get the cassandra instance up and populate it with data in `assignment` by running

```bash
docker-compose up
```

You will notice that it takes some time for the cassandra instance to initialise and for the data loader component in the `assignment` folder to populate the database. 

You can test if your cassandra instance is up by access the SQL terminal with 

```bash
docker exec -it cassandra-db cqlsh
```

This will allow you to run queries against the database. Similar to the tutorial with Postgres, you can work directly in this manner and execute the queries as needed. The last question requires you to move it over to Python, but you need to work through all the options with CSQL first - be sure to read the code to see how the data is generated. There is a wind turbine UUID that you can use as your example when querying.


If you are struggling with the compose command, it is also possible to spin up just the cassandra instance with 

```bash
docker-compose up cassandra
```

or directly as a docker container

```bash
docker run --name cassandra-db -p 9042:9042 -d cassandra:latest
```

You can see the output to the terminal in the latter case with


```bash
docker logs cassandra-db
```

You will then need to populate the database yourself by running `python main.py` in the `assignments` folder while the docker container is up. Note, you will need to install the requirements in `requirements.txt` to be able to run the code. That is

```bash
python3 -m venv .venv
source .venv/bin/activate  # here we are using a virtual environment  - you could install the requirements directly too
pip install -r requirements
python main.py  # this will populate the cassandra database in the running container.
```

You may of course, also access that running docker container from a Jupyter notebook, but will also need to install the requirements.


If you are having trouble with all of these options, you can create a Dockerfile container based on cassandra, which has python installed:

```bash
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

You can build, run, and hop onto this container with 

```bash
docker build -t cassandra-with-tools .
docker run --rm --name cassandra-db -p 9042:9042 -d cassandra-with-tools
docker exec -it cassandra-db /bin/bash
cd tmp # work in the tmp directory
git clone https://github.com/jackdotwa/us-ie-big-data-technologies.git
cd us-ie-big-data-technologies/cassandra/
```


## Submitting and auto-marking

You need to modify the `assignment/student.py` file to contain parametrised queries. That means that you will need to add the `cassandra` to your working repository for the course. The easiest way to achieve this is to have docker and git running locally. If you use the method of working in a temporary container (as discussed just above), you will need to ensure that you can push from that container to your repository. 
