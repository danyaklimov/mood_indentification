from django.contrib import admin
from django.contrib.admin import ModelAdmin

from reviews.models import Review

from reviews.models import Metrics


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    pass

@admin.register(Metrics)
class MetricsAdmin(ModelAdmin):
    pass
