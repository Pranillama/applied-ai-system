import os
import json
from google import genai
from google.genai import types
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import math

gemini_client = None

def init_gemini():
    """Load API key and initialize Gemini."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("GEMINI_API_KEY not found in .env file. Please add your Google Gemini API key.")
    global gemini_client
    gemini_client = genai.Client(api_key=api_key)

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

def format_song_for_embedding(song: Dict) -> str:
    """Convert a song dictionary into a descriptive string for embedding."""
    return f"Title: {song['title']}, Artist: {song['artist']}, Genre: {song['genre']}, Mood: {song['mood']}, Energy: {song['energy']}"

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Get embeddings from Gemini for a list of texts."""
    response = gemini_client.models.embed_content(
        model="gemini-embedding-2",
        contents=texts,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    )
    return [e.values for e in response.embeddings]

def embed_query(query: str) -> List[float]:
    """Get embedding for a search query."""
    response = gemini_client.models.embed_content(
        model="gemini-embedding-2",
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
    )
    return response.embeddings[0].values

class MusicRAG:
    """Retrieval-Augmented Generation pipeline for Music Recommendations."""
    
    def __init__(self, catalog: List[Dict]):
        self.catalog = catalog
        self.embeddings = []
        
        # In a larger system, you would save/load these embeddings to disk.
        # Since we only have ~20 songs, we can embed them on initialization.
        texts = [format_song_for_embedding(song) for song in catalog]
        if texts:
            self.embeddings = embed_texts(texts)

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Retrieve the top_k most similar songs to the user's query."""
        query_embedding = embed_query(query)
        
        results = []
        for song, emb in zip(self.catalog, self.embeddings):
            sim = cosine_similarity(query_embedding, emb)
            results.append((song, sim))
            
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def generate_recommendation(self, query: str, retrieved_songs: List[Tuple[Dict, float]]) -> str:
        """Use Gemini to generate a response recommending the retrieved songs."""
        # Check if we have valid songs to recommend
        if not retrieved_songs:
            return "I couldn't find any songs matching that description in our catalog."
            
        # Format the context for the prompt
        context_parts = []
        for rank, (song, score) in enumerate(retrieved_songs, 1):
            context_parts.append(f"Rank {rank}: {song['title']} by {song['artist']} (Genre: {song['genre']}, Mood: {song['mood']})")
        context_str = "\n".join(context_parts)
        
        prompt = f"""You are a helpful and enthusiastic music recommendation assistant. 
The user is asking for: "{query}"

Here are the top matches retrieved from our catalog:
{context_str}

Please respond to the user and recommend these specific songs. Explain why they fit the user's request based on their genre and mood.
IMPORTANT RULES:
1. ONLY recommend the songs explicitly listed in the top matches above. Do NOT make up or recommend any other songs.
2. Keep your response conversational and engaging.
3. Mention the artist and title clearly in your explanation.
"""

        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
