# app/main.py
from fastapi import FastAPI
from app.core.neo4j import get_driver, close_driver
from app.api.ingest import router as ingest_router
from app.api.generate import router as generate_router
def create_app():
    return FastAPI()

app = create_app()


def create_constraints():
    def _constraints(tx):
        tx.run("""
            CREATE CONSTRAINT keyword_name_unique IF NOT EXISTS
            FOR (k:Keyword) REQUIRE k.name IS UNIQUE
        """)
    driver = get_driver()
    with driver.session() as session:
        session.execute_write(_constraints)

@app.on_event("startup")
def on_startup():
    try:
        create_constraints()
        print("Constraints ensured")
    except Exception as e:
        print("Could not create constraints:", e)

@app.on_event("shutdown")
def on_shutdown():
    close_driver()
app.include_router(ingest_router, prefix="/api")
app.include_router(generate_router, prefix="/api")
@app.get("/ping")
def ping():
    return {"ping": "pong"}