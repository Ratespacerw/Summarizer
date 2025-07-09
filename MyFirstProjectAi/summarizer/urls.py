# MyFirstProjectAi/summarizer/urls.py
from django.urls import path
from . import views  # Imports views.py from the current directory (the summarizer app)

urlpatterns = [
    # When a request comes to the path 'process/',
    # Django will call the 'process_text_view' function from your views.py.
    # The name='process_text' is optional but good practice for referring to this URL elsewhere.
    path('process/', views.process_text_view, name='process_text'),
]

