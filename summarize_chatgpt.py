import requests
from gradio_client import Client

def get_summery(prompt):

    client = Client("huggingface-projects/gemma-2-9b-it")
    new_prompt = "Only Summarize the text around 300 words and include important stuffs only: `" + prompt + "` in uft-8 formate only also give number of year of experiecse" 
    # print(new_prompt)
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

def get_summery2(prompt):
    client = Client("KingNish/OpenGPT-4o")
    new_prompt = "Only Summarize the text around 300 words and include important stuffs only: `" + prompt + "` in uft-8 formate only"

    result = client.predict(
            user_prompt={"text":new_prompt},
            model_selector="idefics2-8b-chatty",
            decoding_strategy="Top P Sampling",
            temperature=0.5,
            max_new_tokens=2048,
            repetition_penalty=1,
            top_p=0.9,
            web_search=False,
            api_name="/chat"
    )
    print(result)
    return result
# prompt = "hi there how are you ?"
# result = get_summery(prompt)
# print(result)
# print("done")

# from transformers import BertForQuestionAnswering, BertTokenizer
# import torch

def find_question_response(context, question):

    API_URL = "https://api-inference.huggingface.co/models/google-bert/bert-large-uncased-whole-word-masking-finetuned-squad"
    headers = {"Authorization": "Bearer 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"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
        
    output = query({
        "inputs": {
        "question": question,
        "context": context
    },
    })
    print("this is the find_question_response")
    print(output)
    print(output['answer'])
    return output['answer']