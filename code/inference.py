import os
import sys
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_client():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables.")
        print("Please copy .env.template to .env and add your API key.")
        sys.exit(1)

    # OpenRouter uses the OpenAI client but with a different base URL
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        # Optional: headers for OpenRouter rankings
        default_headers={
            "HTTP-Referer": os.getenv("YOUR_SITE_URL", "https://localhost"),
            "X-Title": os.getenv("YOUR_SITE_NAME", "Local Inference Script"),
        }
    )
    return client

def run_inference(prompt, model="x-ai/grok-4.1-fast", max_retries=4, timeout=60):
    """
    Runs inference using OpenRouter API with retry logic and exponential backoff.

    Args:
        prompt (str): The input text prompt.
        model (str): The model identifier to use.
        max_retries (int): Maximum number of retry attempts (default: 4).
        timeout (int): Timeout in seconds for the API call (default: 60).

    Returns:
        str: The model's response content, or None if all retries fail.
    """
    client = get_client()

    print(f"Sending request to OpenRouter (Model: {model})...")

    for attempt in range(max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                timeout=timeout,
            )

            response_content = completion.choices[0].message.content
            print("\nResponse:")
            print("-" * 50)
            print(response_content)
            print("-" * 50)
            return response_content

        except Exception as e:
            error_msg = f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}"
            print(error_msg)

            # Check if we should retry
            if attempt < max_retries:
                # Exponential backoff: 2s, 4s, 8s, 16s
                wait_time = 2 ** (attempt + 1)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                # All retries exhausted
                final_error = f"All retry attempts exhausted. Last error: {e}"
                print(final_error)
                with open("error.log", "a") as f:
                    f.write(f"{final_error}\n")
                return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run inference with OpenRouter")
    parser.add_argument("prompt", nargs="*", default=["Explain quantum computing in one sentence."], help="The prompt to send")
    parser.add_argument("--model", default="x-ai/grok-4.1-fast", help="Model to use")
    
    args = parser.parse_args()
    user_prompt = " ".join(args.prompt)
    
    run_inference(user_prompt, model=args.model)
