from django.apps import AppConfig
from utils import filter_data


class GraphApiConfig(AppConfig):
    name = "graph_api"

    def ready(self):
        filter_data.start()
