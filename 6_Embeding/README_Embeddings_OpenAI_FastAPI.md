# Embeddings with OpenAI API — Step-by-Step Practice Guide

This project continues the AI learning path:

```text
FastAPI
   ↓
OpenAI API
   ↓
Prompt Engineering
   ↓
Structured Output
   ↓
Function / Tool Calling
   ↓
Embeddings   ← YOU ARE HERE
   ↓
Vector Database
   ↓
RAG
   ↓
AI Agents
   ↓
Model Context Protocol (MCP)
   ↓
Agentic Workflows
   ↓
Evaluation & Observability
   ↓
Docker
   ↓
Cloud Deployment
```

The goal of this README is to understand what embeddings are, how to generate them with the OpenAI API, how to compare them, and how they become the foundation for semantic search, vector databases, and RAG.

---

# 1. What is an Embedding?

An embedding is a numerical representation of text.

Example:

```text
"How do I reset my password?"
        ↓
Embedding Model
        ↓
[0.021, -0.145, 0.832, ...]
```

The key idea is:

```text
Similar meaning
      ↓
Similar vectors
```

So these two sentences:

```text
"How do I reset my password?"
"I forgot my password. How can I change it?"
```

should have relatively similar embedding vectors.

---

# 2. Why Embeddings Matter

Embeddings are useful for:

```text
Semantic Search
RAG
Document Retrieval
Recommendation Systems
Clustering
Classification
Duplicate Detection
Similarity Matching
Knowledge Bases
FAQ Search
```

They allow your application to search by meaning instead of exact words.

---

# 3. Keyword Search vs Semantic Search

Traditional keyword search may struggle with:

```text
Query:
"How can I change my login credentials?"
```

Document:

```text
"To reset your password, click Forgot Password."
```

The exact words are different, but the meaning is similar.

Embedding-based search can recognize that similarity.

---

# 4. Embeddings Mental Model

```text
Text
  ↓
Embedding Model
  ↓
Vector
  ↓
Store Vector
  ↓
Compare Vectors
  ↓
Find Similar Meaning
```

Later, this becomes:

```text
Documents
   ↓
Embeddings
   ↓
Vector Database
   ↓
User Question
   ↓
Question Embedding
   ↓
Similarity Search
   ↓
Relevant Documents
   ↓
LLM
   ↓
Answer
```

That is the core idea behind RAG.

---

# 5. OpenAI Embedding Models

OpenAI currently documents these third-generation embedding models:

```text
text-embedding-3-small
text-embedding-3-large
```

A good learning default is:

```text
text-embedding-3-small
```

Default vector sizes:

```text
text-embedding-3-small → 1536 dimensions
text-embedding-3-large → 3072 dimensions
```

The API also supports reducing the vector size using the `dimensions` parameter.

---

# 6. Install Requirements

```bash
pip install openai fastapi uvicorn python-dotenv numpy
```

Update requirements:

```bash
pip freeze > requirements.txt
```

---

# 7. Environment Variable

Your `.env` file:

```text
OPENAI_API_KEY=your-api-key
```

Your `.gitignore` should include:

```text
.env
.venv/
__pycache__/
*.pyc
```

---

# 8. First Embedding Example

```python
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Artificial intelligence is changing software development."
)

embedding = response.data[0].embedding

print(embedding)
```

You will see a long list of floating-point numbers.

---

# 9. Check the Vector Length

```python
print(len(embedding))
```

For:

```text
text-embedding-3-small
```

the default length is:

```text
1536
```

---

# 10. Create a Reusable Embedding Function

```python
def get_embedding(
    text: str,
    model: str = "text-embedding-3-small"
):
    response = client.embeddings.create(
        model=model,
        input=text
    )

    return response.data[0].embedding
```

Use it:

```python
embedding = get_embedding(
    "What is machine learning?"
)
```

---

# 11. Clean Input

```python
def get_embedding(
    text: str,
    model: str = "text-embedding-3-small"
):
    text = text.replace("\n", " ")

    response = client.embeddings.create(
        model=model,
        input=text
    )

    return response.data[0].embedding
```

---

# 12. Generate Embeddings for Multiple Texts

```python
texts = [
    "Artificial intelligence is powerful.",
    "Machine learning learns patterns from data.",
    "FastAPI is a Python web framework."
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

for item in response.data:
    print(item.index)
    print(len(item.embedding))
```

This is often more efficient than making one request per string.

---

# 13. Compare Two Embeddings

A common technique is:

```text
Cosine Similarity
```

The general idea:

```text
1.0  → very similar
0.0  → unrelated
-1.0 → opposite direction
```

Do not assume one universal similarity cutoff. Test thresholds using your own data.

---

# 14. Cosine Similarity with NumPy

```python
import numpy as np


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float]
):
    a = np.array(vector_a)
    b = np.array(vector_b)

    return np.dot(a, b) / (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )
```

---

# 15. Compare Similar Sentences

```python
text1 = "How do I reset my password?"
text2 = "I forgot my password. How can I change it?"

embedding1 = get_embedding(text1)
embedding2 = get_embedding(text2)

score = cosine_similarity(
    embedding1,
    embedding2
)

print(score)
```

The result should usually be relatively high because the meanings are similar.

---

# 16. Compare Unrelated Sentences

Try:

```python
text1 = "How do I reset my password?"
text2 = "What is the weather in Los Angeles?"
```

Compare again.

The similarity should generally be lower than the password-related pair.

---

# 17. Build a Tiny Semantic Search Engine

```python
documents = [
    "To reset your password, click Forgot Password.",
    "Our office is open Monday through Friday.",
    "You can update your billing address in Account Settings.",
    "Machine learning finds patterns in historical data."
]
```

Generate embeddings:

```python
document_embeddings = []

for document in documents:
    embedding = get_embedding(document)

    document_embeddings.append(
        {
            "text": document,
            "embedding": embedding
        }
    )
```

---

# 18. Search by Meaning

```python
query = "I cannot remember my password."

query_embedding = get_embedding(query)

results = []

for item in document_embeddings:
    score = cosine_similarity(
        query_embedding,
        item["embedding"]
    )

    results.append(
        {
            "text": item["text"],
            "score": float(score)
        }
    )

results.sort(
    key=lambda x: x["score"],
    reverse=True
)

for result in results:
    print(
        result["score"],
        result["text"]
    )
```

The password document should normally rank near the top.

---

# 19. What Did We Just Build?

You built a small in-memory vector search system.

```text
Documents
   ↓
Embeddings
   ↓
Python Memory
   ↓
User Query
   ↓
Query Embedding
   ↓
Cosine Similarity
   ↓
Ranked Documents
```

The next step will replace:

```text
Python Memory
```

with:

```text
Vector Database
```

---

# 20. FastAPI Embedding Endpoint

```python
from pydantic import BaseModel


class EmbeddingRequest(BaseModel):
    text: str
```

Endpoint:

```python
@app.post("/embedding")
def create_embedding(
    request: EmbeddingRequest
):
    embedding = get_embedding(
        request.text
    )

    return {
        "text": request.text,
        "dimensions": len(embedding),
        "embedding": embedding
    }
```

---

# 21. Production Note

Returning all embedding values through a public API is often unnecessary.

For learning, this is fine.

For production, you may prefer:

```json
{
  "text": "What is RAG?",
  "dimensions": 1536,
  "status": "created"
}
```

while storing the vector internally.

---

# 22. FastAPI Similarity Endpoint

```python
class SimilarityRequest(BaseModel):
    text1: str
    text2: str
```

```python
@app.post("/similarity")
def compare_text(
    request: SimilarityRequest
):
    embedding1 = get_embedding(
        request.text1
    )

    embedding2 = get_embedding(
        request.text2
    )

    score = cosine_similarity(
        embedding1,
        embedding2
    )

    return {
        "text1": request.text1,
        "text2": request.text2,
        "similarity": float(score)
    }
```

---

# 23. Test Similarity in Swagger

Request:

```json
{
  "text1": "I forgot my password.",
  "text2": "How do I reset my login password?"
}
```

Then try:

```json
{
  "text1": "I forgot my password.",
  "text2": "How is the weather?"
}
```

Compare the scores.

---

# 24. FastAPI Semantic Search Endpoint

```python
class SearchRequest(BaseModel):
    query: str
```

```python
@app.post("/search")
def semantic_search(
    request: SearchRequest
):
    query_embedding = get_embedding(
        request.query
    )

    results = []

    for document in document_embeddings:
        score = cosine_similarity(
            query_embedding,
            document["embedding"]
        )

        results.append(
            {
                "text": document["text"],
                "score": float(score)
            }
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return {
        "query": request.query,
        "results": results
    }
```

---

# 25. Top-K Search

Usually you do not need every document.

```python
top_results = results[:3]
```

This is commonly called:

```text
Top-K Retrieval
```

Example:

```text
k = 3
```

---

# 26. Store Metadata with Embeddings

Do not store only the vector.

Store useful metadata too.

Example:

```python
{
    "id": 101,
    "text": "To reset your password...",
    "category": "Account",
    "source": "help-center",
    "embedding": [...]
}
```

Metadata becomes very important in a vector database.

---

# 27. Metadata Filtering

Imagine your knowledge base contains:

```text
Banking
Insurance
HR
Technology
```

You may want:

```text
Search only Insurance documents
```

This combines:

```text
Semantic Search
+
Metadata Filtering
```

---

# 28. What is Chunking?

Large documents are normally divided into smaller pieces before generating embeddings.

```text
100-page policy manual
       ↓
Chunk 1
Chunk 2
Chunk 3
...
```

Each chunk gets its own embedding.

---

# 29. Why Chunk Documents?

A large document may discuss many different topics.

One vector for the whole document can be too broad.

Smaller chunks make retrieval more precise.

---

# 30. Simple Chunking Function

```python
def chunk_text(
    text: str,
    chunk_size: int = 500
):
    return [
        text[i:i + chunk_size]
        for i in range(
            0,
            len(text),
            chunk_size
        )
    ]
```

---

# 31. Character vs Token Chunking

The example above uses characters.

Production systems may chunk by:

```text
Tokens
Sentences
Paragraphs
Sections
Headings
Semantic boundaries
```

Structure-aware or token-aware chunking is often better.

---

# 32. Chunk Overlap

Chunks often overlap.

Example:

```text
Chunk 1: 0–500
Chunk 2: 450–950
```

Overlap:

```text
50 characters
```

This reduces the chance of losing context at chunk boundaries.

---

# 33. Overlapping Chunk Function

```python
def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunks.append(
            text[start:end]
        )

        start += (
            chunk_size - overlap
        )

    return chunks
```

---

# 34. Create Embeddings for Chunks

```python
chunks = chunk_text(
    long_document
)

chunk_embeddings = []

for index, chunk in enumerate(chunks):
    embedding = get_embedding(
        chunk
    )

    chunk_embeddings.append(
        {
            "chunk_id": index,
            "text": chunk,
            "embedding": embedding
        }
    )
```

This is very close to the indexing phase of RAG.

---

# 35. Batch Embeddings for Chunks

Instead of one request per chunk:

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=chunks
)
```

Then:

```python
chunk_embeddings = []

for item in response.data:
    chunk_embeddings.append(
        {
            "chunk_id": item.index,
            "text": chunks[item.index],
            "embedding": item.embedding
        }
    )
```

---

# 36. Embedding Pipeline

```text
Document
   ↓
Clean Text
   ↓
Chunk Text
   ↓
Generate Embeddings
   ↓
Store:
- Vector
- Text
- Document ID
- Chunk ID
- Metadata
```

Later:

```text
User Question
   ↓
Create Query Embedding
   ↓
Vector Search
   ↓
Retrieve Relevant Chunks
```

---

# 37. Using the `dimensions` Parameter

You can request shorter embeddings.

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="What is RAG?",
    dimensions=512
)
```

Then:

```python
print(
    len(
        response.data[0].embedding
    )
)
```

returns:

```text
512
```

Smaller vectors use less storage, though retrieval quality can trade off against lower dimensionality.

---

# 38. Small vs Large Embedding Model

Conceptually:

```text
text-embedding-3-small
    ↓
Smaller vectors
Lower cost
Good default

text-embedding-3-large
    ↓
Larger vectors
Potentially stronger retrieval quality
More storage and cost
```

For learning:

```text
Start with text-embedding-3-small
```

---

# 39. Embeddings Are Not Generated Text

This:

```python
client.responses.create(...)
```

generates model output.

This:

```python
client.embeddings.create(...)
```

generates vectors.

Compare:

```text
Responses API
    ↓
Text / structured output / tool use

Embeddings API
    ↓
Numeric vectors
```

---

# 40. Embeddings Do Not Answer Questions

An embedding itself does not answer:

```text
What is our refund policy?
```

It helps find relevant information.

```text
Question
  ↓
Embedding
  ↓
Search
  ↓
Relevant Text
  ↓
LLM
  ↓
Answer
```

That becomes RAG.

---

# 41. Complete FastAPI Embedding Learning API

```python
import numpy as np

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


app = FastAPI(
    title="Embeddings Learning API",
    version="1.0.0"
)


client = OpenAI()


EMBEDDING_MODEL = "text-embedding-3-small"


class EmbeddingRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=10000
    )


class SimilarityRequest(BaseModel):
    text1: str
    text2: str


class SearchRequest(BaseModel):
    query: str


def get_embedding(
    text: str
):
    text = text.replace(
        "\n",
        " "
    )

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding


def cosine_similarity(
    vector_a,
    vector_b
):
    a = np.array(vector_a)
    b = np.array(vector_b)

    denominator = (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b) /
        denominator
    )


DOCUMENTS = [
    "To reset your password, click Forgot Password.",
    "Our support department is open Monday through Friday.",
    "Customers can update billing information from Account Settings.",
    "RAG combines retrieval with language model generation."
]


DOCUMENT_INDEX = [
    {
        "id": index,
        "text": text,
        "embedding": get_embedding(text)
    }
    for index, text in enumerate(DOCUMENTS)
]


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/embedding")
def embedding(
    request: EmbeddingRequest
):
    try:
        vector = get_embedding(
            request.text
        )

        return {
            "text": request.text,
            "dimensions": len(vector),
            "embedding": vector
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate embedding."
        )


@app.post("/similarity")
def similarity(
    request: SimilarityRequest
):
    try:
        vector1 = get_embedding(
            request.text1
        )

        vector2 = get_embedding(
            request.text2
        )

        score = cosine_similarity(
            vector1,
            vector2
        )

        return {
            "text1": request.text1,
            "text2": request.text2,
            "similarity": score
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to compare text."
        )


@app.post("/search")
def search(
    request: SearchRequest
):
    try:
        query_vector = get_embedding(
            request.query
        )

        results = []

        for document in DOCUMENT_INDEX:
            score = cosine_similarity(
                query_vector,
                document["embedding"]
            )

            results.append(
                {
                    "id": document["id"],
                    "text": document["text"],
                    "score": score
                }
            )

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return {
            "query": request.query,
            "results": results[:3]
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to perform semantic search."
        )
```

---

# 42. Test in Swagger

Run:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Test:

```text
POST /embedding
POST /similarity
POST /search
```

---

# 43. Practice Exercise 1 — Similar Sentences

Compare:

```text
How do I reset my password?
```

with:

```text
I forgot my login password.
```

Then compare with:

```text
What is the weather today?
```

Observe the similarity scores.

---

# 44. Practice Exercise 2 — AI Course Search

Documents:

```text
FastAPI helps create APIs in Python.
Embeddings represent semantic meaning numerically.
RAG retrieves information before generating an answer.
Docker packages applications into containers.
```

Ask:

```text
How can AI understand similarity between sentences?
```

Which document ranks highest?

---

# 45. Practice Exercise 3 — Banking FAQ Search

Create documents for:

```text
Password reset
Wire transfer
Loan application
Credit card dispute
Account opening
```

Search:

```text
I see a transaction on my card that I did not make.
```

See whether the credit-card-dispute document ranks highest.

---

# 46. Practice Exercise 4 — Insurance Search

Create sample content:

```text
Claims
Policy renewal
Coverage
Premiums
Underwriting
```

Search:

```text
How do I report damage after an accident?
```

Measure which text is most similar.

---

# 47. Practice Exercise 5 — Batch Embeddings

Instead of:

```python
for text in documents:
    get_embedding(text)
```

use:

```python
client.embeddings.create(
    model=EMBEDDING_MODEL,
    input=documents
)
```

Map each vector back to its source text.

---

# 48. Practice Exercise 6 — Chunk a Document

Create a long text and split it with:

```python
chunk_text(
    text,
    chunk_size=500,
    overlap=50
)
```

Generate embeddings for every chunk.

---

# 49. Practice Exercise 7 — Top-K Search

Change:

```python
results[:3]
```

to:

```python
results[:1]
```

then:

```python
results[:5]
```

Observe how Top-K affects retrieval.

---

# 50. Practice Exercise 8 — Metadata

Store:

```python
{
    "id": 1,
    "text": "...",
    "category": "Banking",
    "department": "Customer Service",
    "embedding": [...]
}
```

Filter by:

```text
category = Banking
```

before similarity search.

---

# 51. Common Embedding Mistakes

Avoid:

```text
Creating one embedding for a huge document
Re-generating unchanged embeddings repeatedly
Mixing embedding models in one index
Comparing vectors with different dimensions
Ignoring metadata
Using arbitrary similarity thresholds without evaluation
Returning giant vectors unnecessarily to the frontend
Ignoring governance for sensitive data
```

---

# 52. Keep Model and Dimensions Consistent

If your stored documents use:

```text
text-embedding-3-small
1536 dimensions
```

your query embeddings should use the same compatible representation.

If you significantly change your embedding strategy, re-index your documents.

---

# 53. When Should You Recreate Embeddings?

Examples:

```text
Document text changes
Embedding model changes
Embedding dimensions change
Chunking strategy changes
You improve your retrieval pipeline
```

---

# 54. Embeddings and Cost

Usually:

```text
Indexing Phase
Documents
   ↓
Generate embeddings once
   ↓
Store them
```

Then:

```text
Search Phase
New question
   ↓
Generate one query embedding
   ↓
Search stored vectors
```

Do not regenerate every document embedding for each user query.

---

# 55. Embeddings and Security

Embeddings are derived from your data.

Treat them as application data.

Consider:

```text
Access control
Tenant isolation
Encryption
Sensitive information
Retention
Audit requirements
Data residency
Document permissions
```

Enterprise retrieval must respect the user's permissions.

---

# 56. Embeddings vs Vector Database

Embeddings:

```text
Generate vectors
```

Vector database:

```text
Store vectors
Index vectors
Search vectors efficiently
Filter metadata
Return nearest matches
```

This lesson uses Python memory so you understand the fundamentals first.

---

# 57. Embeddings vs RAG

```text
Embeddings
   ↓
Semantic representation

Vector Database
   ↓
Efficient retrieval

RAG
   ↓
Retrieval + LLM answer generation
```

---

# 58. Recommended Project Structure

```text
ai-fastapi-learning/
│
├── app/
│   ├── main.py
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── service.py
│   │   ├── similarity.py
│   │   └── chunking.py
│   │
│   ├── models/
│   │   ├── requests.py
│   │   └── responses.py
│   │
│   └── data/
│       └── sample_documents.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 59. Example Embedding Service

```python
# app/embeddings/service.py

from openai import OpenAI


client = OpenAI()

EMBEDDING_MODEL = (
    "text-embedding-3-small"
)


def get_embedding(
    text: str
):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding
```

---

# 60. Example Similarity Service

```python
# app/embeddings/similarity.py

import numpy as np


def cosine_similarity(
    a,
    b
):
    a = np.array(a)
    b = np.array(b)

    denominator = (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b) /
        denominator
    )
```

---

# 61. Current Learning Progress

```text
✅ FastAPI
✅ OpenAI API
✅ Prompt Engineering
✅ Structured Output
✅ Function / Tool Calling
✅ Embeddings

⬜ Vector Database
⬜ RAG
⬜ AI Agents
⬜ Model Context Protocol (MCP)
⬜ Agentic Workflows
⬜ Evaluation & Observability
⬜ Docker
⬜ Cloud Deployment
```

---

# 62. Next Step — Vector Database

Next:

```text
Embeddings
   ↓
Vector Database   ← NEXT
   ↓
RAG
```

Right now we store vectors in Python memory.

That works for a demo, but not for large-scale search.

A vector database lets you efficiently store and search large numbers of embeddings.

Examples you may encounter:

```text
PostgreSQL + pgvector
Pinecone
Qdrant
Weaviate
Milvus
Azure AI Search
OpenSearch
```

---

# 63. Recommended Practice Strategy

Learn embeddings in this order:

```text
Generate one embedding
        ↓
Inspect vector length
        ↓
Embed two sentences
        ↓
Calculate cosine similarity
        ↓
Embed several documents
        ↓
Create a query embedding
        ↓
Rank documents
        ↓
Return Top-K
        ↓
Add metadata
        ↓
Chunk documents
        ↓
Batch embeddings
        ↓
Move vectors to a Vector Database
```

The most important concept is:

```text
Embeddings do not generate answers.

They convert meaning into numbers so your application can compare and retrieve semantically related information.
```

---

# 64. Quick Reference

Generate one embedding:

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="What is RAG?"
)

embedding = (
    response.data[0].embedding
)
```

Generate several:

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=[
        "FastAPI",
        "Embeddings",
        "RAG"
    ]
)
```

Reduce dimensions:

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="What is RAG?",
    dimensions=512
)
```

Core pipeline:

```text
Text
 ↓
Embedding
 ↓
Vector
 ↓
Similarity Search
 ↓
Relevant Text
 ↓
Vector DB
 ↓
RAG
```

---

# 65. Current API Note

The current OpenAI embeddings API uses:

```python
client.embeddings.create(
    model="text-embedding-3-small",
    input="Your text"
)
```

and retrieves the vector from:

```python
response.data[0].embedding
```

OpenAI currently documents:

```text
text-embedding-3-small
text-embedding-3-large
```

Always check the current API documentation when changing models or upgrading SDK versions.
