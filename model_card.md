# 🎧 Model Card - Applied AI Music Recommender (RAG Edition)

## 1. Model Name
> VibeFinder AI 2.0 (Gemini RAG Integration)

---

## 2. Intended Use
This system takes conversational text inputs, retrieves matching songs from a small local CSV dataset, and uses Google's Gemini LLM to generate a personalized recommendation explanation. It is an educational Applied AI system designed to test Retrieval-Augmented Generation and Output Guardrailing.

---

## 3. How It Works (Short Explanation)
When you type a request (like "Find me a sad relaxing song"), the system converts your words into a numeric map (an embedding) and compares it to similar numeric maps of the 20 songs in our catalog to find the mathematically closest fit. 

It then passes those 3 closest songs, along with your original request, to Google Gemini. Gemini acts like a virtual DJ, analyzing the retrieved songs and explaining to you exactly *why* they fit your request. Finally, our code features a "guardrail" script that double checks the AI's math, ensuring it hasn't recommended a song that isn't actually in the catalog.

---

## 4. Personal Reflection: AI Collaboration

*(Please fill in these reflections below!)*

**One time the AI gave me a helpful suggestion:**
> The AI was incredibly helpful in designing the Architecture and Guardrail logic. It suggested checking the final LLM output against the retrieved song titles as a simple string-matching guardrail, which saved me hours of complex prompt engineering and effectively blocked any out-of-catalog hallucinations.

**One time the AI gave me a flawed or incorrect suggestion:**
> The AI originally suggested building the RAG pipeline using the older `google-generativeai` SDK. This caused compatibility and syntax issues during the actual build, requiring me to manually debug and refactor the code to use the modern `google-genai` Python SDK (using `genai.Client`).

---

## 5. Strengths
- **Conversational Interface:** Users no longer have to construct dictionaries of genre/mood strings. They can type like a human.
- **Dynamic Reasoning:** Gemini can contextualize the song logically, mapping "workout" to "high energy pop/rock" on the fly.
- **Safe Outputs:** The output guardrails successfully capture instances where the LLM forgets the context or hallucinates external music.

---

## 6. Limitations and Biases
- **Hallucination Risk:** LLMs inherently "want" to help the user. If a user asks for a very specific real-world song (e.g. "Do you have any Taylor Swift?"), the LLM may initially lie and say "Yes!" even if we didn't retrieve any. Our guardrail catches and blocks this, but it results in a broken interaction rather than a graceful fallback.
- **Embedding Bias:** The embedding model may over-index on genres it has seen often in training (like Pop) while poorly mapping niche indie genres. 

---

## 7. Future Work
If I were to improve this system further:
- I would use **Function Calling (Tool Use)**. Instead of raw RAG, the LLM could execute a tool called `search_catalog(genre="pop", min_energy=0.8)` which would give it structured database abilities instead of fuzzy semantic search.
- I would expand the catalog sizes dynamically utilizing a live music API (like Spotify's API).
