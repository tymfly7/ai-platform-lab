import os
import sys

import psycopg
from fastembed import TextEmbedding
from pgvector.psycopg import register_vector

DSN = os.environ.get("PLATFORM_DSN", "postgresql://llm:llm@localhost:5433/platform")
vec = next(TextEmbedding("BAAI/bge-small-en-v1.5").embed([sys.argv[1]]))

with psycopg.connect(DSN) as conn:
    register_vector(conn)
    rows = conn.execute(
        "SELECT id, content, embedding <=> %s AS distance FROM docs ORDER BY distance LIMIT 3", 
        (vec,),
    ).fetchall()

for doc_id, content, distance in rows:
    print(f"{distance:.3f} [{doc_id}] {content}")