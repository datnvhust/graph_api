from .db_connect import get_collection
import time

col = get_collection("feeds_van")
col_post = get_collection("feeds_van_posts")
col_cmt = get_collection("feeds_van_comments")

query = {
    "$and": [
        {"entry.changes.value.item": {"$in": ["status", "comment"]}},
        {"sys_status": {"$exists": False}},
    ]
}

# while True:
for doc in col.find(query):
    if doc["entry"][0]["changes"][0]["value"]["item"] == "status":
        col_post.insert_one(doc)
    else:
        col_cmt.insert_one(doc)

col.update_many(query, {"$set": {"sys_status": 1}})
# time.sleep(10)
