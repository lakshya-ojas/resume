import pymongo
from generate_embedding import generate_embedding
from datetime import datetime
import __main__

# Function to establish connection to MongoDB
def connect_to_mongodb():
    try:
        client = pymongo.MongoClient("mongodb+srv://lakshyaagrawal:Lakshya12@cluster0.suugkij.mongodb.net/")
        return client
    except pymongo.errors.ConnectionFailure as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

# Function to insert data into MongoDB
def insert_data(summary_text):
    try:
        client = connect_to_mongodb()
        db = client.Ojas_database
        collection = db.resume

        embedding_data = generate_embedding(summary_text)
        print("Embedding generated for the summary text")

        now = datetime.now()
        document = {
            'Summary': summary_text,
            'embedding': embedding_data,
            'timestamp': now
        }
        insert_result = collection.insert_one(document)
        print(f"Inserted document id: {insert_result.inserted_id}")

    except Exception as e:
        print(f"Error inserting data: {e}")

    finally:
        client.close()



# Async function to find similar documents based on query embedding
async def find_similar_documents(query_embedding):
    try:
        client = connect_to_mongodb()
        db = client.Ojas_database
        collection = db.resume

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
                    "Summary": 1,
                    "score": { "$meta": "vectorSearchScore" }
                }
            }
        ]

        documents = list(collection.aggregate(pipeline))
        return documents
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        client.close()


# Function to search text and return similar documents
async def search_text(game):
    query = "hello"
    query_embedding = generate_embedding(query)
    return await find_similar_documents(query_embedding)


if __name__ == "__main__":
    import asyncio

    async def test_search_text():
        result = await search_text("This is a sample summary text for testing purposes.")
        print(result)

    asyncio.run(test_search_text())
