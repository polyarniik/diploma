from typing import Any

from django import forms
from django.contrib.auth import get_user_model

import repositories
from repositories import models

User = get_user_model()


class CompareForm(forms.Form):
    left_document = forms.FileField()
    right_document = forms.FileField()


class RepositoryCreateForm(forms.ModelForm):
    name = forms.CharField(max_length=250)
    document = forms.FileField()
    commit = forms.CharField(required=False, initial="Документ добавлен")

    def save(self, commit: bool = ...) -> Any:
        repository = super().save()
        return repository

    class Meta:
        model = models.Repository
        fields = ["name", "document", "commit"]


class MergeDocumentForm(forms.Form):
    document = forms.FileField()


class CommitCreateForm(forms.ModelForm):
    author = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    repository = forms.ModelChoiceField(queryset=models.Repository.objects.all(), required=False)

    class Meta:
        model = models.Commit
        fields = ["author", "message", "document", "repository"]


class RepositorySettingsForm(forms.ModelForm):
    class Meta:
        model = models.Repository
        fields = ["name"]
