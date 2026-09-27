import os
import sys
import chromadb
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from mcp.server import MCPServer

# 1. Load API keys from .env
load_dotenv()

# 2. Initialize MCP Server
mcp = MCPServer(name="docs-retriever")

# 3. Connect to Project 1's ChromaDB persistence path
CHROMA_PATH = os.path.abspath(
    os.getenv("CHROMA_PATH", r"D:\Desktop\projects\rag-agent-project\chroma_db")
)
print(f"Connecting to ChromaDB at: {CHROMA_PATH}", file=sys.stderr)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# 4. Initialize Gemini embeddings matching Project 1 (gemini-embedding-001 -> 3072 dimensions)
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Warning: Neither GOOGLE_API_KEY nor GEMINI_API_KEY found in environment.", file=sys.stderr)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=api_key,
)


@mcp.tool(
    name="search_docs",
    description="Retrieve relevant documentation chunks and citations from ChromaDB.",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
    },
)
def search_docs(query: str, top_k: int = 3) -> str:
    """Performs similarity search against ChromaDB using Gemini embeddings."""
    clean_query = query.strip()
    if not clean_query:
        return "Error: Search query cannot be blank."

    if top_k < 1 or top_k > 20:
        return "Error: top_k must be between 1 and 20."

    try:
        collections = chroma_client.list_collections()
        if not collections:
            return "Error: No collections found in ChromaDB."

        collection = chroma_client.get_collection(collections[0].name)

        # Embed user query using Gemini to produce matching 3072-dimension vector
        query_vector = embeddings.embed_query(clean_query)

        # Query ChromaDB using the vector directly
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            return f"No results found for '{clean_query}'."

        formatted = []
        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), start=1):
            source = meta.get("source", "Unknown") if meta else "Unknown"
            score = f"{(1 - dist):.4f}" if dist is not None else "N/A"
            formatted.append(
                f"--- Result {i} ---\nSource: {source} | Score: {score}\n{doc.strip()}\n"
            )

        return "\n".join(formatted)

    except Exception as e:
        print(f"Retrieval error: {str(e)}", file=sys.stderr)
        return f"Error executing document search: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")