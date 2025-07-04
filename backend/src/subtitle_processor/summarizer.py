# subtitle_processor/summarizer.py
import os
import time
from openai import OpenAI, RateLimitError, APIError
from tenacity import retry, stop_after_attempt, wait_exponential

# Initialize the OpenAI client (or any other LLM client)
# It's good practice to use environment variables for API keys.
client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))
def summarize_text(text: str, model: str = "microsoft/phi-3.5-mini-128k-instruct") -> str:
    """
    Summarizes a given text using the specified AI model.
    Includes exponential backoff for retries on failures.
    """
    try:
        prompt = f"Summarize the following text concisely in one sentence:\n\n---\n{text}\n---\n\nSummary:"
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=100,
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except (RateLimitError, APIError) as e:
        print(f"API error or rate limit exceeded: {e}. Retrying...")
        raise
    except Exception as e:
        print(f"An unexpected error occurred during summarization: {e}")
        return f"Error summarizing: {e}"

