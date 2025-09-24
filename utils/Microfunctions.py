# Description: This module contains utility functions for various micro tasks.
# import libraries
import re
from django.http import JsonResponse


# Define a function to validate email addresses using regex
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def dummy_view(request):
    """
    A simple view to check if the server is running.
    """
    return JsonResponse({"status": "ok"})
