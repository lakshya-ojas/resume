from gradio_client import Client

def get_summery(prompt):

    client = Client("huggingface-projects/gemma-2-9b-it")
    new_prompt = "Summarize this text: " + prompt + "in uft-8"
    result = client.predict(
            message=prompt,
            max_new_tokens=1024,
            temperature=0.6,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.2,
            api_name="/chat"
    )
    return result

# prompt = "hi there how are you ?"
# result = get_summery(prompt)
# print(result)
# print("done")