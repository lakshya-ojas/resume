import requests

hf_token = "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"
embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

def generate_embedding(text: str) -> list[float]:
    response = requests.post(
        embedding_url,
        headers={"Authorization": f"Bearer {hf_token}"},
        json={"inputs": text}  # Wrap text in a list
    )

    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")
    else:
        return response.json()

# ans = generate_embedding("MongoDB is awesome")
# print(ans)

