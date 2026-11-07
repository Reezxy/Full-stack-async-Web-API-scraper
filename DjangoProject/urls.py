from django.contrib import admin
from django.urls import path

from DjangoProject.app.API.Views.scrape_view import scrape_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("scrape/", scrape_view, name="scrape"),
]
