import collections
import os
import time

from openai import OpenAI

# Defaults to local Ollama. Set LLM_BASE_URL, LLM_API_KEY and LLM_MODEL to use another provider.
client = OpenAI(
    api_key=os.environ.get("LLM_API_KEY", "ollama"),
    base_url=os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1"),
    max_retries=0,
)
MODEL = os.environ.get("LLM_MODEL", "gemma4:31b")
PAUSE = float(os.environ.get("LLM_PAUSE", "0"))  # use 18 for Gemini to avoid rate limit
RUNS = 5 # int(os.environ.get("LLM_RUNS", "5")) that line for gemini

PROMPTS = [
    "Name the second largest city in Czechia. Reply with one word.",           
    "Name one Nordic capital city. Reply with one word.",                      
    "Pick a random number between 1 and 10. Reply with the number only.",      
    "Suggest a name for a coffee shop in Prague. Reply with the name only.",   
]

for prompt in PROMPTS:
    print(f"\n{prompt}")
    for temperature in (0.0, 1.5):
        counts = collections.Counter()
        for _ in range(RUNS):
            r = client.chat.completions.create(
                model=MODEL,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            counts[r.choices[0].message.content.strip()] += 1
            time.sleep(PAUSE)
        summary = ", ".join(f"{answer!r} x{n}" for answer, n in counts.most_common())
        print(f"  temperature={temperature}: {summary}")



# with rate limit 
# import collections
# import os
# import time

# from openai import OpenAI, RateLimitError

# client = OpenAI(
#     api_key=os.environ["GEMINI_API_KEY"],
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
# )
# PAUSE = 18  


# def ask(temperature: float) -> str:
#     for attempt in range(4):
#         try:
#             r = client.chat.completions.create(
#                 model= os.environ.get("LLM_MODEL", "gemma4:31b"), # "gemini-3.8-flash",
#                 reasoning_effort="low",
#                 temperature=temperature,
#                 messages=[{"role": "user", "content": "Name one Nordic capital city. Reply with one word."}],
#             )
#             return r.choices[0].message.content.strip()
#         except RateLimitError:
#             wait = 15 * (attempt + 1)  # back off a little more each time
#             print(f"rate limited, waiting {wait}s")
#             time.sleep(wait)
#     raise RuntimeError("still rate limited after 4 attempts")


# counts = collections.Counter()
# for temperature in (0.0, 1.5):
#     for i in range(5):
#         answer = ask(temperature)
#         counts[(temperature, answer)] += 1
#         print(f"temperature={temperature} run {i + 1}: {answer}")
#         time.sleep(PAUSE)

# print()
# for (temperature, answer), n in sorted(counts.items()):
#     print(f"temperature={temperature}  {answer!r}  x{n}")