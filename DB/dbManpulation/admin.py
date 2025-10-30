from django.contrib import admin
from .models import Stable, Horse, Owner, Owns, Trainer, Track, Race, Raceresults

@admin.register(Stable)
class StableAdmin(admin.ModelAdmin):
    list_display = ("stableid", "stablename", "location", "colors")
    search_fields = ("stableid", "stablename", "location")


@admin.register(Horse)
class HorseAdmin(admin.ModelAdmin):
    list_display = ("horseid", "horsename", "age", "gender", "stableid")
    list_filter = ("gender", "stableid")
    search_fields = ("horseid", "horsename")


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("ownerid", "fname", "lname")
    search_fields = ("ownerid", "fname", "lname")


@admin.register(Owns)
class OwnsAdmin(admin.ModelAdmin):
    list_display = ("ownerid", "horseid")
    search_fields = ("ownerid__ownerid", "horseid__horseid")


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ("trainerid", "fname", "lname", "stableid")
    search_fields = ("trainerid", "fname", "lname")


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("trackname", "location", "length")
    search_fields = ("trackname", "location")


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ("raceid", "racename", "trackname", "racedate", "racetime")
    list_filter = ("trackname", "racedate")
    search_fields = ("raceid", "racename")


@admin.register(Raceresults)
class RaceResultsAdmin(admin.ModelAdmin):
    list_display = ("raceid", "horseid", "results", "prize")
    list_filter = ("results",)
    search_fields = ("raceid__raceid", "horseid__horseid")
