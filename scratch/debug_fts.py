import re
import sqlite3
import os

# 1. Regex Test
patterns = [(r"\bGalaxy X-\d+\b", "galaxy")]
content = "Galaxy X-69 Primary Emission: synchrotron radiation."
entities = []
for p, t in patterns:
    found = re.findall(p, content, re.IGNORECASE)
    for f in found:
        entities.append({"type": t, "id": f.strip()})
print(f"Regex Entities: {entities}")

# 2. FTS5 Test
db_path = "backend/storage/sqlite_db/memory.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Try different search styles
    query_entity = "Galaxy X-69"
    phrase = f'"{query_entity.replace("-", " ")}"'
    print(f"Testing FTS5 Phrase Search: {phrase}")
    
    cursor.execute("SELECT content FROM episodic_fts WHERE content MATCH ?", (phrase,))
    rows = cursor.fetchall()
    print(f"FTS5 Results: {rows}")
    conn.close()
else:
    print("DB not found")
