import pymongo
from generate_embedding import generate_embedding

# MongoDB connection setup
client = pymongo.MongoClient("mongodb+srv://lakshyaagrawal:Lakshya12@cluster0.suugkij.mongodb.net/")
db = client.Ojas_database
collection = db.resume

# Example query
query = "space at war"

# Generate embedding vector for the query
query_embedding = generate_embedding(query)

async def find_similar_documents(query_embedding):
    try:
        pipeline = [
    {
        "$vectorSearch": {
            "index": "Resume_index",
            "queryVector": query_embedding,
            "path": "embedding",
            "limit": 5,
            "numCandidates": 100
        }
    },
    {
        "$project": {
            "_id": 1,
            "Summery": 1,
            # "embedding": 0,
            "score": { "$meta": "vectorSearchScore" } #vectorSearchScore searchScore
        }
    }
]


        documents =  list(collection.aggregate(pipeline))
        return documents
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

