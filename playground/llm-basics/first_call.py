import os 
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

resp = client.chat.completions.create(
    model="gemini-3.8-flash",
    reasoning_effort="low",
    messages=[
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "Explain what an LLM gateway does in two sentences."},
    ],
)
print(resp.choices[0].message.content)
print(resp.usage)  # prompt, completion and total tokens