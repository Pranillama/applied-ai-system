import re
from typing import List, Tuple, Dict

class GuardrailError(Exception):
    """Raised when the LLM output violates our guardrails."""
    pass

def verify_output(llm_response: str, retrieved_songs: List[Tuple[Dict, float]]) -> bool:
    """
    Guardrail: Check that the LLM response actually includes at least one of the 
    retrieved song titles. This ensures the model isn't completely hallucinating 
    a random fake song and ignoring the retrieved context.
    """
    if not retrieved_songs:
        # If nothing was retrieved, we expect a graceful fallback message
        return True
    
    titles = [song['title'].lower() for song, score in retrieved_songs]
    response_lower = llm_response.lower()
    
    # Check if ANY of the retrieved titles are in the response
    found_any = any(title in response_lower for title in titles)
    
    if not found_any:
        raise GuardrailError(
            "Guardrail Failed: The AI did not recommend any of our actual catalog songs! "
            "It may have hallucinated or ignored the context."
        )
        
    return True
