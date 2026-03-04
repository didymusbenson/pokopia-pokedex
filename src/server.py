from mcp.server.fastmcp import FastMCP
import chromadb
from uuid import uuid4
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

mcp = FastMCP("open-brain")

client = chromadb.PersistentClient(path=str(DATA_DIR))
collection = client.get_or_create_collection(
    name="brain",
    metadata={"hnsw:space": "cosine"},
)


@mcp.tool()
def save_thought(content: str, tags: str = "", category: str = "general") -> str:
    """Save a thought, note, decision, or piece of knowledge to the brain.

    Args:
        content: The thought or knowledge to save
        tags: Comma-separated tags (e.g. "python,debugging,tip")
        category: One of: general, decision, insight, reference, project, preference
    """
    thought_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    collection.add(
        documents=[content],
        metadatas=[{"tags": tags, "category": category, "created_at": now, "updated_at": now}],
        ids=[thought_id],
    )
    return f"Saved thought {thought_id}"


@mcp.tool()
def search_brain(query: str, n_results: int = 5, category: str | None = None) -> str:
    """Semantically search the brain for relevant thoughts.

    Args:
        query: Natural language search query
        n_results: Number of results to return (default 5)
        category: Filter by category (optional)
    """
    where = {"category": category} if category else None
    results = collection.query(query_texts=[query], n_results=n_results, where=where)

    if not results["documents"][0]:
        return "No matching thoughts found."

    output = []
    for i, (doc, meta, dist) in enumerate(
        zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
    ):
        similarity = 1 - dist
        output.append(
            f"[{i+1}] (id: {results['ids'][0][i]})\n"
            f"    Similarity: {similarity:.2f}\n"
            f"    Category: {meta.get('category', 'general')}\n"
            f"    Tags: {meta.get('tags', '')}\n"
            f"    Created: {meta.get('created_at', 'unknown')}\n"
            f"    Content: {doc}"
        )
    return "\n\n".join(output)


@mcp.tool()
def list_recent(n: int = 10, category: str | None = None) -> str:
    """List the most recent thoughts in the brain.

    Args:
        n: Number of recent thoughts to return (default 10)
        category: Filter by category (optional)
    """
    where = {"category": category} if category else None
    results = collection.get(where=where)

    if not results["documents"]:
        return "Brain is empty."

    items = list(zip(results["ids"], results["documents"], results["metadatas"]))
    items.sort(key=lambda x: x[2].get("created_at", ""), reverse=True)
    items = items[:n]

    output = []
    for id_, doc, meta in items:
        preview = doc[:200] + ("..." if len(doc) > 200 else "")
        output.append(
            f"[{id_}]\n"
            f"    Category: {meta.get('category', 'general')}\n"
            f"    Tags: {meta.get('tags', '')}\n"
            f"    Created: {meta.get('created_at', 'unknown')}\n"
            f"    Content: {preview}"
        )
    return "\n\n".join(output)


@mcp.tool()
def delete_thought(thought_id: str) -> str:
    """Delete a thought from the brain by its ID.

    Args:
        thought_id: The UUID of the thought to delete
    """
    try:
        collection.delete(ids=[thought_id])
        return f"Deleted thought {thought_id}"
    except Exception as e:
        return f"Error deleting thought: {e}"


@mcp.tool()
def update_thought(
    thought_id: str,
    content: str | None = None,
    tags: str | None = None,
    category: str | None = None,
) -> str:
    """Update an existing thought in the brain.

    Args:
        thought_id: The UUID of the thought to update
        content: New content (optional)
        tags: New comma-separated tags (optional)
        category: New category (optional)
    """
    existing = collection.get(ids=[thought_id])
    if not existing["documents"]:
        return f"Thought {thought_id} not found."

    old_meta = existing["metadatas"][0]
    new_meta = {
        "tags": tags if tags is not None else old_meta.get("tags", ""),
        "category": category if category is not None else old_meta.get("category", "general"),
        "created_at": old_meta.get("created_at", ""),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    new_content = content if content is not None else existing["documents"][0]

    collection.update(ids=[thought_id], documents=[new_content], metadatas=[new_meta])
    return f"Updated thought {thought_id}"


@mcp.tool()
def brain_stats() -> str:
    """Get statistics about the brain - total thoughts, categories, and top tags."""
    count = collection.count()
    if count == 0:
        return "Brain is empty."

    all_data = collection.get()
    categories: dict[str, int] = {}
    all_tags: dict[str, int] = {}

    for meta in all_data["metadatas"]:
        cat = meta.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1
        for tag in meta.get("tags", "").split(","):
            tag = tag.strip()
            if tag:
                all_tags[tag] = all_tags.get(tag, 0) + 1

    output = f"Total thoughts: {count}\n\nCategories:\n"
    for cat, cnt in sorted(categories.items(), key=lambda x: -x[1]):
        output += f"  {cat}: {cnt}\n"

    if all_tags:
        output += "\nTop tags:\n"
        for tag, cnt in sorted(all_tags.items(), key=lambda x: -x[1])[:15]:
            output += f"  {tag}: {cnt}\n"

    return output


if __name__ == "__main__":
    mcp.run()
