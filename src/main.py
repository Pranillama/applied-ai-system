import os
import sys
import argparse
from src.recommender import load_songs
from src.rag_pipeline import init_gemini, MusicRAG
from src.guardrails import verify_output, GuardrailError

def main() -> None:
    parser = argparse.ArgumentParser(description="Applied AI Music Recommender (RAG Edition)")
    parser.add_argument("--query", type=str, help="Natural language query for the music you want.")
    args = parser.parse_args()

    # 1. Initialize System
    try:
        init_gemini()
    except Exception as e:
        print(f"Error initializing AI: {e}")
        print("Make sure you have created your .env file with GEMINI_API_KEY as shown in steps!")
        sys.exit(1)

    # 2. Load Catalog
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs from the catalog.")
    
    # 3. Initialize RAG
    print("Embedding catalog (this takes a moment)...")
    rag = MusicRAG(songs)
    
    # 4. Get User Query
    query = args.query
    if not query:
        print("\nWelcome to the Applied AI Music Recommender!")
        query = input("Tell me what kind of music you're looking for today: ")
        if not query.strip():
            print("No query entered. Exiting.")
            sys.exit(0)

    print("\n" + "=" * 60)
    print(f"  Query: '{query}'")
    print("=" * 60)

    # 5. Retrieve
    print("\nRetrieving matching songs from catalog...")
    top_matches = rag.retrieve(query, top_k=3)
    for rank, (song, sim) in enumerate(top_matches, 1):
        print(f" -> Found: {song['title']} by {song['artist']} (Score: {sim:.2f})")

    # 6. Generate Response using RAG
    print("\nGenerating AI recommendation...")
    try:
        response_text = rag.generate_recommendation(query, top_matches)
        
        # 7. Guardrail Check!
        verify_output(response_text, top_matches)
        
        # 8. Print Results
        print("\n★★★ AI RECOMMENDER RESPONSE ★★★\n")
        print(response_text)
        print("\n" + "=" * 60 + "\n")
        
    except GuardrailError as ge:
        print(f"\n[BLOCKED BY GUARDRAIL] \n{ge}")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
