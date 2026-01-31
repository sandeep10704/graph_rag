from app.core.neo4j import get_driver
driver = get_driver()
import uuid

# Generate ONE graph_id per ingest
def generate_graph_id():
    return str(uuid.uuid4())


def store_chunks(chunks, graph_id):
    with driver.session() as session:
        for c in chunks:
            session.execute_write(insert_chunk, c, graph_id)

        session.execute_write(link_chunks, graph_id)

    return graph_id



def insert_chunk(tx, chunk, graph_id):
    tx.run(
        """
        MERGE (c:Chunk {id: $id, graph_id: $graph_id})
        SET c.text = $text
        WITH c
        UNWIND $keywords AS kw
        MERGE (k:Keyword {name: kw, graph_id: $graph_id})
        MERGE (c)-[:HAS_KEYWORD {graph_id: $graph_id}]->(k)
        """,
        id=chunk["id"],
        text=chunk["text"],
        keywords=chunk["keywords"],
        graph_id=graph_id
    )



def link_chunks(tx, graph_id):
    tx.run(
        """
        MATCH (c1:Chunk {graph_id: $graph_id})
              -[:HAS_KEYWORD {graph_id: $graph_id}]->
              (k:Keyword {graph_id: $graph_id})
              <-[:HAS_KEYWORD {graph_id: $graph_id}]-
              (c2:Chunk {graph_id: $graph_id})
        WHERE c1.id < c2.id
        MERGE (c1)-[:RELATED_TO {graph_id: $graph_id}]->(c2)
        """,
        graph_id=graph_id
    )

# def create_constraints():
#     with driver.session() as session:
#         session.execute_write(_create_constraints)



# def _create_constraints(tx):
#     tx.run(
#         """
#         CREATE CONSTRAINT chunk_unique_per_graph IF NOT EXISTS
#         FOR (c:Chunk)
#         REQUIRE (c.id, c.graph_id) IS UNIQUE
#         """
#     )

#     tx.run(
#         """
#         CREATE CONSTRAINT keyword_unique_per_graph IF NOT EXISTS
#         FOR (k:Keyword)
#         REQUIRE (k.name, k.graph_id) IS UNIQUE
#         """


