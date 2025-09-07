"""
Use csql to test things directly by hopping onto the container, 
then port those statements here, parameterize them, and 
test them by running the script with 

    python student 

You need the cassanda instance to be running, and can launch that 
with `docker-compose up`, or `docker-compose up cassandra` if you
want start with an uninitialised dataset.
"""
import os
import time
import uuid
from datetime import datetime
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
import logging
from datetime import date, timedelta


## Sort out the logging - we are using log.answer to define the answers - you need not change that in the code

# --- LOGGING --- Basic logging setup for demonstration
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)

log = logging.getLogger()

# --- Custom Log Level Definition ---
# Define a custom log level for marking answers.
# We choose a value between INFO (20) and WARNING (30).
ANSWER_LEVEL_NUM = 25
logging.addLevelName(ANSWER_LEVEL_NUM, "ANSWER")

def answer(self, message, *args, **kws):
    # This function is added to the Logger class.
    if self.isEnabledFor(ANSWER_LEVEL_NUM):
        # The '_log' method is the internal method Logger uses.
        self._log(ANSWER_LEVEL_NUM, message, args, **kws)

# Add the 'answer' method to all logger instances.
logging.Logger.answer = answer

# change this back to logging.INFO if you want to see all messages - for the assignment, it must remain as below
logging.basicConfig(level=ANSWER_LEVEL_NUM)


# --- YOUR IMPLEMENTATION STARTS HERE ---

def get_readings_for_day(session, turbine_id, day):
    """
    Retrieves two sensor readings for a specific turbine on a given day.
    
    Args:
        session: The Cassandra session object.
        turbine_id (uuid.UUID): The UUID of the turbine.
        day (str): The day in 'YYYY-MM-DD' format.

    Returns:
        A list of row objects from Cassandra.
    """
    log.info(f"Getting readings two sensor readings for turbine {turbine_id} on {day}...")

    # TODO: Write your CQL query and session.execute call here.
    # The query should select all columns from sensor_readings.
    # The WHERE clause should filter by turbine_id and day.

    # UPDATE THIS
    cql_query = """"""
    
    rows = []
    if cql_query: 
        try: 
            # Prepare the statement for better performance and security.
            prepared_statement = session.prepare(cql_query)
            # Execute the query with the provided parameters - you will need to modify these based on the 
            # parameters of cql_query
            rows = session.execute(prepared_statement, (turbine_id, day))
            # The result is iterable, so we convert it to a list before returning.
        except Exception as e:
            log.info(f'Question not answered or error in cql_query statement')
    

    return list(rows)

def get_reading_for_turbine(session, turbine_id, day):
    """
    Retrieves the single most recent sensor reading for a turbine on a given day.
    
    Args:
        session: The Cassandra session object.
        turbine_id (uuid.UUID): The UUID of the turbine.
        day (str): The day in 'YYYY-MM-DD' format.

    Returns:
        A single row object representing the latest reading, or None if no readings are found.
    """
    log.info(f"Executing Task 2 for turbine {turbine_id} on {day}...")
    # TODO: Write your CQL query and session.execute call here.
    # Hint: Use the LIMIT clause to get only one result. The table is already ordered!
    return None

def get_number_of_readings_in_range(session, turbine_id, day, start_time, end_time):
    """
    Retrieves number of readings within a start_time and end_time range for a turbine.
    
    Args:
        session: The Cassandra session object.
        turbine_id (uuid.UUID): The UUID of the turbine.
        day (str): The day in 'YYYY-MM-DD' format.
        start_time (datetime): The start of the time range.
        end_time (datetime): The end of the time range.

    Returns:
        A list of row objects from Cassandra.
    """
    log.info(f"Getting number of readings in range on {turbine_id} on {day}...")
    
    ## UPDATE THIS QUERY
    cql_query = """"""
    rows = []
    if cql_query: 
        try: 
            # Prepare the statement for better performance and security.
            prepared_statement = session.prepare(cql_query)
            # Execute the query with the provided parameters - you will need to modify these based on the 
            # parameters of cql_query
            rows = session.execute(prepared_statement, (turbine_id, day, start_time, end_time))
            # The result is iterable, so we convert it to a list before returning.
        except Exception as e:
            log.info(f'Question not answered or error in cql_query statement')
            log.error(e)
    

    return list(rows)

def get_last_update_for_day(session, day):
    """
    Retrieves the last update record for a given day.
    
    Args:
        session: The Cassandra session object.
        day (str): The day in 'YYYY-MM-DD' format.

    Returns:
        A single row object representing the last update
    """
    log.info(f"Get last updated record {day}...")

    ## UPDATE THIS QUERY
    cql_query = """"""
    rows = []
    if cql_query: 
        try: 
            # Prepare the statement for better performance and security.
            prepared_statement = session.prepare(cql_query)
            # Execute the query with the provided parameters - you will need to modify these based on the 
            # parameters of cql_query
            rows = session.execute(prepared_statement, (day,)) # the comma is important, don't remove it
            # The result is iterable, so we convert it to a list before returning.
        except Exception as e:
            log.info(f'Question not answered or error in cql_query statement')
            log.error(e)

    return list(rows)


    # TODO: Write your CQL query for the `latest_readings` table.
    # This should be a simple SELECT with a WHERE clause for the day and a LIMIT.
    return None


def get_health(session, turbine_id, day):
    """
    Determine if the provided turbine was heathy on the provided day
    
    Args:
        session: The Cassandra session object.
        turbine_id (uuid.UUID): The UUID of the turbine.
        day (str): The day in 'YYYY-MM-DD' format.

    Return:
        a string 'Healthy' or 'Not Healthy'
    """
    log.info(f"Getting readings two sensor readings for turbine {turbine_id} on {day}...")

    # TODO: Write your CQL query and session.execute call here.
    # The query should select all columns from sensor_readings.
    # The WHERE clause should filter by turbine_id and day.



    # UPDATE THIS ---

    # determine these values by quering Cassandra
    is_wind_speed_healthy=True
    is_power_output_healthy=False

    try:
        
        if is_wind_speed_healthy and is_power_output_healthy:
            return "Healthy"
        else:
            return "Not Healthy"

    except Exception as e:
        log.error(f"An error occurred during the health check: {e}")
        return "Could not determine health (Error)"


# --- YOUR IMPLEMENTATION ENDS HERE ---



def get_total_readings(session, wind_turbine_id, day):
    """
    This is a simple example query to count the number of sensor readings
    for a specific turbine on a particular day.

    This confirms your connection
    is working and that data exists for the partition key you are using.
    The result is a single row with a single value (the count).

    Due to the nature of the data generated, we will use the day prior to the current
    day - typically you would pass the day value in to search optimally - we will 
    be seeing it ourselves.

    Args:
        session: The Cassandra session object.
        day (str): The day in 'YYYY-MM-DD' format.

    Returns:
        A single row object containing the turbine_id, or None if not found.
    """
    try:
        log.info(f'Querying total readings for turbine: {wind_turbine_id} on {day}...')

        # --- Corrected CQL Query ---
        # Use '?' as the placeholder for parameters in prepared statements.
        # Do not use f-strings or %-formatting here.
        cql_query = """
            SELECT COUNT(*)
            FROM wind_turbine_data.sensor_readings
            WHERE turbine_id = ? AND day = ?
        """

        # --- Prepare and Execute ---
        # Prepare the statement for better performance and security.
        prepared_statement = session.prepare(cql_query)

        # Execute the query with the provided parameters.
        rows = session.execute(prepared_statement, (wind_turbine_id, day))

        # The result for a COUNT query is a single row with one value.
        result = rows.one()
        if result:
            log.info(f"Found {result.count} readings.")
            return result.count
        else:
            log.warning("Query executed but returned no rows.")
            return 0

    except Exception as e:
        log.error(f"An error occurred while querying Cassandra: {e}")
        return None



def main():
    """
    A main function to allow students to test their solutions.
    This function will not be used by the marker.
    """
  # --- Configuration ---
    # Get the contact points from the environment variable set in docker-compose
    CASSANDRA_NODES = os.getenv('CASSANDRA_NODES', '127.0.0.1').split(',')

    try:
        # Specify the load balancing policy and your local datacenter name
        policy = DCAwareRoundRobinPolicy(local_dc='datacenter1')
        cluster = Cluster(['127.0.0.1'], load_balancing_policy=policy, protocol_version=4)
        session = cluster.connect('wind_turbine_data')
        log.info("Successfully connected to Cassandra.")
    except Exception as e:
        log.info(f"Could not connect to Cassandra. Please ensure it's running. Error: {e}")
        return

    # --- Sample data for testing ---
    test_turbine_id = uuid.UUID('610e4ad5-09c4-4055-9ff4-948fe6b4f832') # do not change
    # You can change these values to test your functions - unless explicitly stated otherwise
    # fixing the date

    test_day_date = (date.today() - timedelta(days=1))
    # get the string representation of the test day - use the date object for other calculations
    test_day = test_day_date.strftime('%Y-%m-%d')


    log.answer(f'Readings for {test_turbine_id} : {get_total_readings(session, test_turbine_id, test_day)}')


    log.info("\n--- RUNNING TESTS/ANSWERING QUESTIONS ---")
    
    # Question 4.4.1 : Retrieve the last updated record for a given day. (1)
    last_update = get_last_update_for_day(session, test_day)
    log.answer(f'4.4.1: {last_update}')


    # Question 4.4.2: Retrieve two sensor readings for a turbine on a given day. (1)
    readings = get_readings_for_day(session, test_turbine_id, test_day)
    log.answer(f'4.4.2: {readings}')


    # Question 4.4.3. Retrieve the total number of readings on a given turbine and day, between (and including) 2025-09-07T09:00:00+0000 and 2025-09-07T10:00:00+0000. (1)
    # continue to use the day variable as set above.
    test_start_time = datetime.strptime(f'{test_day}T09:00:00+0000', '%Y-%m-%dT%H:%M:%S%z')
    test_end_time = datetime.strptime(f'{test_day}T10:00:00+0000', '%Y-%m-%dT%H:%M:%S%z')
    in_range = get_number_of_readings_in_range(session, test_turbine_id, test_day, test_start_time, test_end_time)
    log.answer(f'4.4.3: {in_range}')

   
    # Question 4.4.4.  Determine if a specific turbine is ‘healthy’ on a specific day
    log.answer(f'4.4.4: {get_health(session, test_turbine_id, test_day)}')


    session.shutdown()
    cluster.shutdown()


if __name__ == "__main__":
    main()

