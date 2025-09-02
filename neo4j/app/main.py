import os
import time
from neo4j import GraphDatabase

# --- Connection Logic (remains the same) ---
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password123')

driver = None
for _ in range(30):
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("✅ Neo4j connection successful!")
        break
    except Exception as e:
        print(f"⏳ Waiting for Neo4j... ({e})")
        time.sleep(5)
else:
    raise Exception("❌ Could not connect to Neo4j.")

# --- Minimal Example Logic ---

def load_data(tx):
    """
    Loads the movies.csv file into the graph.
    It creates (:Person) and (:Movie) nodes and connects them with either
    a [:ACTED_IN] or [:DIRECTED] relationship based on the 'role' column.
    """
    print("\n--- Loading Movie Data ---")
    query = """
    LOAD CSV WITH HEADERS FROM 'file:///movies.csv' AS row
    MERGE (p:Person {name: row.name})
    MERGE (m:Movie {title: row.movie_title, year: toInteger(row.movie_year)})
    FOREACH (_ IN CASE row.role WHEN 'actor' THEN [1] ELSE [] END |
        MERGE (p)-[:ACTED_IN]->(m)
    )
    FOREACH (_ IN CASE row.role WHEN 'director' THEN [1] ELSE [] END |
        MERGE (p)-[:DIRECTED]->(m)
    )
    """
    tx.run(query)
    print("✅ Data loaded.")
    # You can visualize this graph in the Neo4j Browser at http://localhost:7474
    # Run the query: MATCH (n) RETURN n

def question_1(tx):
    """
    Simple Traversal: Who acted in 'The Matrix'?
    """
    print("\n--- Question 1: Who acted in 'The Matrix'? ---")
    query = """
    MATCH (p:Person)-[:ACTED_IN]->(m:Movie {title: 'The Matrix'})
    RETURN p.name AS actor
    """
    result = tx.run(query)
    for record in result:
        print(f"- {record['actor']}")

def question_2(tx):
    """
    Reverse Traversal: What movies has Keanu Reeves acted in?
    """
    print("\n--- Question 2: What movies has Keanu Reeves acted in? ---")
    query = """
    MATCH (p:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(m:Movie)
    RETURN m.title AS movie
    """
    result = tx.run(query)
    for record in result:
        print(f"- {record['movie']}")

def question_3(tx):
    """
    Pattern Matching: Who are Keanu Reeves' co-stars?"""
    print("\n--- Question 3: Who are Keanu Reeves' co-stars? ---")
    # This query finds a path from Keanu, to a movie he acted in,
    # and then back out to other actors in that same movie.
    query = """
    MATCH (keanu:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(m:Movie)<-[:ACTED_IN]-(coActor:Person)
    WHERE keanu <> coActor
    RETURN coActor.name AS coActor, m.title as movie
    """
    result = tx.run(query)
    for record in result:
        print(f"- {record['coActor']} (in {record['movie']})")

# --- Execution ---
with driver.session(database="neo4j") as session:
    # First, clear the database to ensure a clean slate
    session.run("MATCH (n) DETACH DELETE n")
    # Run the transactions
    session.write_transaction(load_data)
    session.read_transaction(question_1)
    session.read_transaction(question_2)
    session.read_transaction(question_3)



driver.close()


