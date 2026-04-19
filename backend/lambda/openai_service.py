import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://is215-openai.upou.io/v1"
)

def ask_openai(query, context):
    system_prompt = open("prompt.txt").read()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}"}
        ]
    )

    return response.choices[0].message.content