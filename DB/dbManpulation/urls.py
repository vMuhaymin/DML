from django.urls import path
from . import views

urlpatterns = [
    # Admin features
    path("admin-panel/add-race/", views.add_race_view, name="add_race"),
    path("admin-panel/delete-owner/", views.delete_owner_view, name="delete_owner"),
    path("admin-panel/move-horse/", views.move_horse_view, name="move_horse"),
    path("admin-panel/approve-trainer/", views.approve_trainer_view, name="approve_trainer"),

    # Guest features
    path("guest/horses-by-owner/", views.horses_by_owner_view, name="horses_by_owner"),
    path("guest/winning-trainers/", views.winning_trainers_view, name="winning_trainers"),
    path("guest/trainer-winnings/", views.trainer_winnings_view, name="trainer_winnings"),
    path("guest/track-stats/", views.track_stats_view, name="track_stats"),
]
