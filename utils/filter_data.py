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


def obj_id_exist(col, name_id, obj_id):
    for obj in col.find():
        if obj["entry"][0]["changes"][0]["value"][name_id] == obj_id:
            return True
    return False


def get_obj(col, name_id, obj_id):
    if name_id == "post_id":
        return col.find_one({"entry.changes.value.post_id": obj_id})
    return col.find_one({"entry.changes.value.comment_id": obj_id})


def filter_data():
    col_feed = get_collection("feeds")
    col_user = get_collection("feeds_van_users")
    for doc in col_feed.find(query).sort("entry.changes.value.created_time", -1):
        # insert user
        user_id = doc["entry"][0]["changes"][0]["value"]["from"]["id"]
        if not user_exist(user_id, col_user):
            col_user.insert_one(doc["entry"][0]["changes"][0]["value"]["from"])
            q_ = {"id": doc["entry"][0]["changes"][0]["value"]["from"]["id"]}
            col_user.update_one(q_, {"$set": {"sys_status": "unblock"}})

        if doc["entry"][0]["changes"][0]["value"]["item"] == "status":
            col = get_collection("feeds_van_posts")
            name_id = "post_id"
        else:
            col = get_collection("feeds_van_cmts")
            name_id = "comment_id"

        obj_id = doc["entry"][0]["changes"][0]["value"][name_id]
        if not obj_id_exist(col, name_id, obj_id):
            col.insert_one(doc)
        else:
            verb = doc["entry"][0]["changes"][0]["value"]["verb"]
            obj_col = get_obj(col, name_id, obj_id)
            if verb in ["edited", "hide"]:
                # compare created time feeds and col
                if (
                    doc["entry"][0]["changes"][0]["value"]["created_time"]
                    > obj_col["entry"][0]["changes"][0]["value"]["created_time"]
                ):
                    col.delete_one(obj_col)
                    col.insert_one(doc)
            elif verb == "remove":
                try:
                    message = obj_col["entry"][0]["changes"][0]["value"]["message"]
                except:
                    message = "Nội dung này không ở dạng text."
                col.delete_one(obj_col)
                col.insert_one(doc)
                col.update_one(doc, {"$set": {"entry.0.changes.0.value.message": message}})
    col_feed.update_many(query, {"$set": {"sys_status": True}})


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(filter_data, "interval", minutes=0.1)
    scheduler.start()
