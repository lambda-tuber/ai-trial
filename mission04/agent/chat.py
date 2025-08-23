from openai import OpenAI

client = OpenAI(
    api_key="dummy",
    base_url="http://localhost:11434/v1"
)

response = client.chat.completions.create(
    model="gemma3:12b",
    messages=[
        {"role": "user", "content": "こんにちは、ローカル LLM から返答してください。"}
    ]
)

print(response.choices[0].message.content)


