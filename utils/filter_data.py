from apscheduler.schedulers.background import BackgroundScheduler
from utils.db_connect import get_collection

query = {
    "$and": [
        {"entry.changes.value.item": {"$in": ["status", "comment"]}},
        {"sys_status": {"$exists": False}},
    ]
}


def user_exist(user_id, col_user):
    for user in col_user.find():
        if user["id"] == user_id:
            return True
    return False


def filter_data():
    col_feed = get_collection("feeds")
    col_post = get_collection("feeds_van_posts")
    col_cmt = get_collection("feeds_van_comments")
    col_user = get_collection("feeds_van_users")
    for doc in col_feed.find(query):
        user_id = doc["entry"][0]["changes"][0]["value"]["from"]["id"]
        if not user_exist(user_id, col_user):
            col_user.insert_one(doc["entry"][0]["changes"][0]["value"]["from"])
        if doc["entry"][0]["changes"][0]["value"]["item"] == "status":
            col_post.insert_one(doc)
        else:
            col_cmt.insert_one(doc)
    col_feed.update_many(query, {"$set": {"sys_status": True}})


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(filter_data, "interval", minutes=0.1)
    scheduler.start()
