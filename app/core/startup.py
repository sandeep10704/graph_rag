from app.core.neo4j import get_driver
driver = get_driver()  


def create_constraints():
    with driver.session() as session:
        session.execute_write(_constraints)

def _constraints(tx):
    tx.run("""
    CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS
    FOR (c:Chunk) REQUIRE c.id IS UNIQUE
    """)
    tx.run("""
    CREATE CONSTRAINT keyword_name_unique IF NOT EXISTS
    FOR (k:Keyword) REQUIRE k.name IS UNIQUE
    """)
