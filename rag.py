import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise RuntimeError(
        "GROQ_API_KEY must be set in the environment"
    )

# Create Groq client
client_groq = Groq(api_key=groq_api_key)

# -----------------------------------
# ChromaDB Client
# -----------------------------------
CHROMA_DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "chroma_db"
)

client = chromadb.PersistentClient(
    path=CHROMA_DB_PATH
)

# -----------------------------------
# Lightweight Embedding Function
# Uses ONNX Runtime (much smaller than PyTorch)
# -----------------------------------
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="documents",
    embedding_function=embedding_fn
)


# -----------------------------------
# Text Chunking
# -----------------------------------
def chunk_text(
    text,
    chunk_size=500,
    overlap=100
):
    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# -----------------------------------
# Clear Chroma Collection
# -----------------------------------
def clear_chroma_collection():
    global collection

    try:
        # Delete old collection
        client.delete_collection("documents")
        print("✅ Old Chroma collection deleted.")

    except Exception:
        # Ignore if collection doesn't exist
        pass

    # Create fresh empty collection
    collection = client.get_or_create_collection(
        name="documents",
        embedding_function=embedding_fn
    )

    print("✅ New empty Chroma collection created.")


# -----------------------------------
# Store Document
# -----------------------------------
def store_document_in_chroma(
    text,
    file_name
):
    chunks = chunk_text(text)

    ids = [
        f"{file_name}_{i}"
        for i in range(len(chunks))
    ]

    # Let ChromaDB handle embeddings via its
    # built-in DefaultEmbeddingFunction (ONNX-based)
    collection.add(
        documents=chunks,
        ids=ids
    )

    return len(chunks)
# -----------------------------------
# Ask Question
# -----------------------------------
def ask_question(
    question,
    chat_history=None
):
    if chat_history is None:
        chat_history = []

    # Let ChromaDB handle the query embedding
    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    retrieved_chunks = results.get("documents", [[]])[0]
    if not retrieved_chunks:
        return {
            "answer": "I could not find this in the document.",
            "citation": ""
        }

    # Best chunk for citation
    best_chunk = retrieved_chunks[0]

    # Context for LLM
    context = "\n".join(
        retrieved_chunks
    )
    history_text = ""

    for chat in chat_history:

        if "question" in chat:
            history_text += (
               f"User: {chat['question']}\n"
        )

        if "answer" in chat:
           history_text += (
               f"Assistant: {chat['answer']}\n"
        )
    
    prompt = f"""
       You are an intelligent AI assistant.

       Your job:
        - Answer ONLY using the provided document context.
        - Also understand previous conversations.
        - If user says:
           "explain simply"
           "summarize"
           "short answer"
          then use previous answer.

       Previous Conversation:
       {history_text}

       Document Context:
       {context}

       Current Question:
       {question}

       Rules:
       - Be helpful and conversational.
       - Keep answer clear.
       - Do not hallucinate.
       - If not found in document say:
       'I could not find this in the document.'
    """

    response = client_groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    answer = response.choices[
        0
    ].message.content

    return {
        "answer": answer,
        "citation": best_chunk
    }