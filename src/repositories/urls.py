from django.urls import path

from repositories import views

app_name = "repositories"

urlpatterns = [
    path("", views.RepositoryListView.as_view(), name="repository_list"),
    path("create/", views.RepositoryCreateView.as_view(), name="repository_create"),
    path("<int:pk>/", views.RepositoryDetailView.as_view(), name="repository_view"),
    path("<int:pk>/delete/", views.repository_delete_view, name="repository_delete"),
    path("<int:pk>/settings/", views.RepositorySettingsFormView.as_view(), name="repository_settings"),
    path("<int:pk>/commits/create", views.CommitCreateView.as_view(), name="commit_create"),
    path("<int:pk>/commits/", views.CommitsListView.as_view(), name="commit_list"),
    path("<int:pk>/commits/<int:commit_id>/", views.CommitDetailView.as_view(), name="commit_view"),
    path("<int:pk>/return/<int:commit_id>", views.CompareView.as_view(), name="return_version"),
    path("<int:pk>/merge/", views.MergeFormView.as_view(), name="merge"),
    path("<int:pk>/members/add", views.add_member_to_repository, name="add_member"),
    path("<int:pk>/members/delete", views.delete_member_from_repository, name="delete_member"),
]
