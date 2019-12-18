from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.contrib.auth import get_user_model
from utils.db_connect import get_collection

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/login")
    else:
        form = UserCreationForm
    return render(request, "register.html", {"form": form})


"""
def sort_by_key(val):
    return val["entry"][0]["changes"][0]["value"]["created_time"]


def queryset_last(queryset_find, type_of_object):
    queryset = []
    obj_id_list = []
    rm_obj_list = []
    queryset_find.sort(key=sort_by_key, reverse=True)
    for doc in queryset_find:
        obj_id = doc["entry"][0]["changes"][0]["value"][type_of_object]
        verb = doc["entry"][0]["changes"][0]["value"]["verb"]

        if verb == "remove":
            rm_obj_list.append(obj_id)
        else:
            if obj_id not in obj_id_list:
                if obj_id in rm_obj_list:
                    doc["entry"][0]["changes"][0]["value"]["verb"] = "remove"
                    rm_obj_list.remove(obj_id)
                queryset.append(doc)
                obj_id_list.append(obj_id)

    return queryset
"""


class PostListView(LoginRequiredMixin, ListView):
    context_object_name = "post_list"
    template_name = "post_list.html"
    col = get_collection("feeds_van_posts")

    def get_queryset(self):
        query = list(self.col.find().sort("_id", -1))
        queryset = []
        post_id_list = []
        col_feeds = get_collection("feeds")
        for doc in col_feeds.find(
            {
                "$and": [
                    {"entry.changes.value.item": {"$in": ["status", "comment"]}},
                    {"sys_status": {"$exists": True}},
                ]
            }
        ).sort("_id", -1):
            post_id = doc["entry"][0]["changes"][0]["value"]["post_id"]
            if post_id not in post_id_list:
                for i in query:
                    if i["entry"][0]["changes"][0]["value"]["post_id"] == post_id:
                        queryset.append(i)

                post_id_list.append(post_id)
        return queryset


class PostDetailView(LoginRequiredMixin, ListView):
    context_object_name = "comment_list"
    template_name = "post_detail.html"

    def get_queryset(self):
        col = get_collection("feeds_van_cmts")
        queryset = col.find({"entry.changes.value.post_id": self.kwargs["post_id"]}).sort("_id", -1)
        return list(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        col = get_collection("feeds_van_posts")
        post = col.find_one({"entry.changes.value.post_id": self.kwargs["post_id"]})
        context["post"] = post
        return context


class UserListView(LoginRequiredMixin, ListView):
    context_object_name = "user_list"
    template_name = "user_list.html"
    col = get_collection("feeds_van_users")

    def get_queryset(self):
        queryset = self.col.find().sort("name", 1)
        return list(queryset)


class AdminView(LoginRequiredMixin, ListView):
    model = User
    context_object_name = "users"
    template_name = "managers/index.html"
    form_class = UserCreationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect("/managers")


def block_user(request):
    user_id = request.GET["user_id"]
    action = request.GET["action"]
    col = get_collection("feeds_van_users")
    user = col.find_one({"id": user_id})
    if action == "block":
        col.update_one(user, {"$set": {"sys_status": "block"}})
    else:
        col.update_one(user, {"$set": {"sys_status": "unblock"}})
    return JsonResponse({"detail": "successful"}, status=200)


"""
class CommentListView(ListView):
    context_object_name = "comments"
    template_name = "comment-list.html"

    def get_queryset(self):
        col = get_collection("feeds_van")
        queryset = col.find(
            {
                "$and": [
                    {"entry.changes.value.item": "comment"},
                    {"entry.changes.value.post_id": self.kwargs["post_id"]},
                ]
            }
        ).sort("_id", -1)
        return queryset
"""
