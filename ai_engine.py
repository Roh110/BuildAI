import subprocess

def get_ai_insights(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=60
        )
        return result.stdout.strip()
    except Exception as e:
        return f"AI error: {str(e)}"
