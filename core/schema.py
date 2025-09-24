# File: ./core/schema.py
from drf_yasg.generators import OpenAPISchemaGenerator


class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_paths(self, endpoints, components, request, public):
        # Call the parent method to get all paths
        paths, prefix = super().get_paths(endpoints, components, request, public)

        # Define the paths to exclude
        excluded_paths = {
            "/",
        }

        # Remove the excluded paths
        for path in excluded_paths:
            paths.pop(path, None)

        return paths, prefix
