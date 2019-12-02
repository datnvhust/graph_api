from django.apps import AppConfig


class GraphApiConfig(AppConfig):
    name = "graph_api"

    def ready(self):
        from utils import filter_data

        filter_data.start()
