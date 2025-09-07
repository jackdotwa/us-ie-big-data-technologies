import os
import time
import logging
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement, BatchStatement
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.protocol import SyntaxException
import loader

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)

log  = logging.getLogger(__name__)


def execute_cql_file(session, filepath):
    """
    Reads a CQL file and executes the commands against the Cassandra session.
    Args:
        session: A cassandra.cluster.Session object connected to the cluster.
        filepath: The path to the .cql file to be executed.
    """
    log.info(f"Reading and executing schema from {filepath}...")
    try:
        with open(filepath, 'r') as f:
            cql_script = f.read()
            # Split the script into individual statements, filtering out empty ones.
            lines = cql_script.splitlines()
            script_without_comments = "\n".join([line.split('--', 1)[0] for line in lines])
            statements = [s.strip() for s in script_without_comments.split(';') if s.strip()]


            for statement in statements:
                try:
                    log.info(f"Executing: {statement[:64]}...") # Log the start of the statement
                    session.execute(statement)
                    log.info("...Success.")
                except SyntaxException as e:
                    log.error(f"!!! Syntax error in statement: {statement}")
                    log.error(f"Error details: {e}")
                    raise  # Stop execution on error
    except FileNotFoundError:
        log.error(f"!!! Error: CQL file not found at '{filepath}'")
        raise
    except Exception as e:
        log.error(f"!!! Failed to execute CQL file '{filepath}'. Error: {e}")
        raise

def main():
    """
    Main function to connect to Cassandra and set up the schema from a file.
    It will retry connecting to the cluster to handle startup delays.
    """
    # Use an environment variable for Cassandra hosts, defaulting to localhost.
    CASSANDRA_NODES = os.getenv('CASSANDRA_NODES', '127.0.0.1').split(',')
    CQL_FILE_PATH = 'schema.cql'  # Assumes schema.cql is in the same directory
    MAX_RETRIES = 10
    RETRY_DELAY_SECONDS = 5

    cluster = None
    session = None

    for attempt in range(MAX_RETRIES):
        try:
            log.info(f"Attempting to connect to Cassandra at {CASSANDRA_NODES} (Attempt {attempt + 1}/{MAX_RETRIES})...")
            lb_policy = DCAwareRoundRobinPolicy(local_dc='datacenter1')
            cluster = Cluster(CASSANDRA_NODES, load_balancing_policy=lb_policy, port=9042)
            session = cluster.connect()
            log.info("Successfully connected to Cassandra.")
            break
        except Exception as e:
            log.warning(f"Connection failed: {e}")
            if attempt < MAX_RETRIES - 1:
                log.info(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                log.error("Could not connect to Cassandra after several retries. Exiting.")
                return

    if session:
        try:
            execute_cql_file(session, CQL_FILE_PATH)
            log.info("Schema setup process completed successfully.")

            loader.load(session)
        except Exception as e:
            log.error(f"An error occurred after connection: {e}")
        finally:
            log.info("Closing connection.")
            session.shutdown()
            cluster.shutdown()

if __name__ == "__main__":
    main()
