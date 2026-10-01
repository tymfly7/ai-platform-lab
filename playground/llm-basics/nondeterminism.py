import collections
import os
import time

from openai import OpenAI, RateLimitError

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
PAUSE = 13  # free tier allows about 5 requests per minute per model


def ask(temperature: float) -> str:
    for attempt in range(4):
        try:
            r = client.chat.completions.create(
                model="gemini-3.8-flash",
                reasoning_effort="low",
                temperature=temperature,
                messages=[{"role": "user", "content": "Name one Nordic capital city. Reply with one word."}],
            )
            return r.choices[0].message.content.strip()
        except RateLimitError:
            wait = 15 * (attempt + 1)  # back off a little more each time
            print(f"rate limited, waiting {wait}s")
            time.sleep(wait)
    raise RuntimeError("still rate limited after 4 attempts")


counts = collections.Counter()
for temperature in (0.0, 1.5):
    for i in range(5):
        answer = ask(temperature)
        counts[(temperature, answer)] += 1
        print(f"temperature={temperature} run {i + 1}: {answer}")
        time.sleep(PAUSE)

print()
for (temperature, answer), n in sorted(counts.items()):
    print(f"temperature={temperature}  {answer!r}  x{n}")