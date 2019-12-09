from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from utils.db_connect import get_collection


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/login")
    else:
        form = UserCreationForm
    return render(request, "register.html", {"form": form})


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


class PostListView(LoginRequiredMixin, ListView):
    context_object_name = "post_list"
    template_name = "post_list.html"
    paginate_by = 10
    col = get_collection("feeds_van_posts")

    def get_queryset(self):
        message = self.request.GET.get("message", "")
        verb = self.request.GET.get("verb", "")
        if message and verb:
            queryset_find = self.col.find(
                {
                    "$and": [
                        {"entry.changes.value.message": {"$regex": message}},
                        {"entry.changes.value.verb": verb},
                    ]
                }
            )
        elif message and not verb:
            queryset_find = self.col.find({"entry.changes.value.message": {"$regex": message}})
        elif not message and verb:
            queryset_find = self.col.find({"entry.changes.value.verb": verb})
        else:
            queryset_find = self.col.find()
        return queryset_last(list(queryset_find), "post_id")


class PostDetailView(LoginRequiredMixin, ListView):
    context_object_name = "comment_list"
    template_name = "post_detail.html"
    paginate_by = 10

    def get_queryset(self):
        col = get_collection("feeds_van_comments")
        message = self.request.GET.get("message", "")
        verb = self.request.GET.get("verb", "")
        if message and verb:
            queryset_find = col.find(
                {
                    "$and": [
                        {"entry.changes.value.message": {"$regex": message}},
                        {"entry.changes.value.verb": verb},
                        {"entry.changes.value.post_id": self.kwargs["post_id"]},
                    ]
                }
            )
        elif message and not verb:
            queryset_find = col.find(
                {
                    "$and": [
                        {"entry.changes.value.message": {"$regex": message}},
                        {"entry.changes.value.post_id": self.kwargs["post_id"]},
                    ]
                }
            )
        elif not message and verb:
            queryset_find = col.find(
                {
                    "$and": [
                        {"entry.changes.value.verb": verb},
                        {"entry.changes.value.post_id": self.kwargs["post_id"]},
                    ]
                }
            )
        else:
            queryset_find = col.find({"entry.changes.value.post_id": self.kwargs["post_id"]})
        return queryset_last(list(queryset_find), "comment_id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        col = get_collection("feeds_van_posts")
        post = col.find_one({"entry.changes.value.post_id": self.kwargs["post_id"]})
        context["post"] = post
        return context


class UserListView(LoginRequiredMixin, ListView):
    context_object_name = "user_list"
    template_name = "user_list.html"
    paginate_by = 10
    col = get_collection("feeds_van_users")

    def get_queryset(self):
        name = self.request.GET.get("name", "")
        if name:
            queryset = self.col.find({"name": {"$regex": name}}).sort("_id", -1)
        else:
            queryset = self.col.find().sort("_id", -1)
        return list(queryset)


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
