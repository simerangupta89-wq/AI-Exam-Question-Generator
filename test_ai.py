
import ollama

print("Starting AI test...")

response = ollama.chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "Give me one MCQ about Operating Systems."
        }
    ]
)

print("AI RESPONSE:")
print(response.message.content)