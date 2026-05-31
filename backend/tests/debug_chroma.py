"""
Debug script to verify Chroma indexing
"""

from app.core.vector_store import client, collection

print("=" * 60)
print("CHROMA DEBUG")
print("=" * 60)

# Check total documents
total_count = collection.count()
print(f"\nTotal chunks in collection: {total_count}")

# Get all docs and extract video_ids
all_docs = collection.get()

videos = set(
    m["video_id"]
    for m in all_docs["metadatas"]
)

print(f"\nVideo IDs in collection: {videos}")

# Count chunks per video
from collections import Counter

video_counts = Counter(
    m["video_id"]
    for m in all_docs["metadatas"]
)

print(f"\nChunks per video:")
for vid, count in video_counts.items():
    print(f"  Video {vid}: {count} chunks")

# Get creators
creators = set(
    m["creator"]
    for m in all_docs["metadatas"]
)

print(f"\nCreators indexed: {creators}")

print("\n" + "=" * 60)
