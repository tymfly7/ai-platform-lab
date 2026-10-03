import os

import psycopg
from fastembed import TextEmbedding
from pgvector.psycopg import register_vector

DSN = os.environ.get("PLATFORM_DSN", "postgresql://llm:llm@localhost:5433/platform")

# (id, acl_group, text) - replace with your own documents later
DOCS = [
    ("hr-001", "staff", "Employees get 5 weeks of paid holiday per year."),
    ("hr-002", "staff", "Remote work is allowed. Office attendance is optional."),
    ("it-001", "staff", "Report security incidents to the on-call engineer within 1 hour."),
    ("fin-001", "finance", "Quarterly budget reviews happen in the first week of each quarter."),
]

model = TextEmbedding("BAAI/bge-small-en-v1.5")  # 384 dimensions

with psycopg.connect(DSN, autocommit=True) as conn:
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS docs ("
        " id text PRIMARY KEY, acl_group text NOT NULL,"
        " content text NOT NULL, embedding vector(384))"
    )
    vectors = list(model.embed([text for _, _, text in DOCS]))
    for (doc_id, group, text), vec in zip(DOCS, vectors):
        conn.execute(
            "INSERT INTO docs VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO UPDATE"
            " SET acl_group = EXCLUDED.acl_group, content = EXCLUDED.content,"
            " embedding = EXCLUDED.embedding",
            (doc_id, group, text, vec),
        )
print(f"ingested {len(DOCS)} documents")