# app/core/neo4j.py
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

assert NEO4J_URI, "NEO4J_URI not set!"
assert NEO4J_USER, "NEO4J_USER not set!"
assert NEO4J_PASSWORD, "NEO4J_PASSWORD not set!"

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _driver

def close_driver():
    global _driver
    if _driver:
        _driver.close()
        _driver = None
