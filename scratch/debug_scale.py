import requests
import numpy as np

INFRA_URL = "http://localhost:8080"
VECTOR_DIM = 128
headers = {"X-Internal-Key": "Recallix-Core-8892"}

scale = 1000
raw_vectors = np.random.randn(scale, VECTOR_DIM).astype('float32')
raw_vectors /= np.linalg.norm(raw_vectors, axis=1)[:, np.newaxis]
python_ids = [f"vec_{j}" for j in range(scale)]

requests.post(f"{INFRA_URL}/clear", headers=headers)

chunk = []
for j in range(scale):
    chunk.append({"id": python_ids[j], "vector": raw_vectors[j].tolist()})
res = requests.post(f"{INFRA_URL}/bulk_add", json={"vectors": chunk}, headers=headers)
print("Bulk add response:", res.status_code, res.text)
