import os
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from documents_workers.comparator import Comparator
from documents_workers.delta_converter import XMLDiffToDeltaConverter
from documents_workers.merger import Merger
from documents_workers.utils import convert_ooxml_to_docx, convert_to_pdf
from documents_workers.visualizer import DocumentVisualizer
from repositories import forms, models
from repositories.utils import generate_random_hash, get_ooxml

User = get_user_model()


class CompareView(generic.FormView):
    form_class = forms.CompareForm
    template_name = "repositories/compare.html"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.GET.get("path", None):
            return render(request, "repositories/details.html", {"path": request.GET.get("path", None)})
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: forms.CompareForm) -> HttpResponse:
        left_document = form.cleaned_data["left_document"]
        rigth_document = form.cleaned_data["rigth_document"]
        left_document_path = os.path.join(
            settings.MEDIA_ROOT,
            "tmp",
            f"{generate_random_hash(15)}.{left_document.data.name.split('.')[-1].lower()}",
        )
        rigth_document_path = os.path.join(
            settings.MEDIA_ROOT,
            "tmp",
            f"{generate_random_hash(15)}.{rigth_document.data.name.split('.')[-1].lower()}",
        )
        with open(left_document_path, "w") as file:
            for chunk in left_document.chunks():
                file.write(chunk)

        with open(rigth_document_path, "w") as file:
            for chunk in rigth_document.chunks():
                file.write(chunk)

        left_document_ooxml = get_ooxml(left_document_path)
        document = DocumentVisualizer(
            XMLDiffToDeltaConverter(
                left_document_ooxml,
                Comparator(left_document_path, rigth_document_path).compare(),
            ).convert(),
            left_document_ooxml,
        ).to_view()
        docx_compare_path = os.path.join(
            settings.MEDIA_ROOT,
            "tmp",
            f"{generate_random_hash(15)}.docx",
        )
        convert_ooxml_to_docx(document, docx_compare_path)
        pdf_compare_path = os.path.join(
            settings.MEDIA_ROOT,
            "compare",
            f"{generate_random_hash(15)}.pdf",
        )

        convert_to_pdf(docx_compare_path, pdf_compare_path)

        return redirect(reverse("compare_view") + f"?path={pdf_compare_path}")


class RepositoryListView(LoginRequiredMixin, generic.ListView):
    queryset = models.Repository.objects.all()
    context_object_name = "repositories"
    template_name = "repositories/repositories.html"

    def get_queryset(self) -> QuerySet[Any]:
        return self.queryset.filter(repository_members=self.request.user)


class RepositoryCreateView(LoginRequiredMixin, generic.CreateView):
    queryset = models.Repository.objects.all()
    form_class = forms.RepositoryCreateForm
    template_name = "repositories/create.html"

    def get_queryset(self) -> QuerySet[Any]:
        return self.queryset.filter(repository_members=self.request.user)

    def form_valid(self, form: forms.RepositoryCreateForm) -> HttpResponse:
        self.object = form.save()
        self.object.repository_members.add(self.request.user)
        models.Commit.objects.create(
            author=self.request.user,
            repository=self.object,
            message=form.cleaned_data["commit"],
            document=form.cleaned_data["document"],
        )
        return HttpResponseRedirect(self.object.get_absolute_url())


class RepositoryDetailView(LoginRequiredMixin, generic.DetailView):
    queryset = models.Repository.objects.all()
    template_name = "repositories/repository.html"
    context_object_name = "repository"

    def get_queryset(self) -> QuerySet[Any]:
        return self.queryset.filter(repository_members=self.request.user)


class RepositorySettingsFormView(LoginRequiredMixin, generic.UpdateView):
    queryset = models.Repository.objects.all()
    model = models.Repository
    template_name = "repositories/settings.html"
    form_class = forms.RepositorySettingsForm
    context_object_name = "repository"

    def get_queryset(self) -> QuerySet[Any]:
        return self.queryset.filter(repository_members=self.request.user)


@login_required
def repository_delete_view(request, pk):
    if request.POST:
        repository = models.Repository.objects.filter(pk=pk).first()
        if repository:
            repository.delete()

    return redirect("repositories:repository_list")


class CommitsListView(LoginRequiredMixin, generic.ListView):
    queryset = models.Commit.objects.all()
    template_name = "repositories/commits.html"
    context_object_name = "commits"

    def get_queryset(self) -> QuerySet[Any]:
        return self.queryset.filter(repository__repository_members=self.request.user)


class CommitDetailView(LoginRequiredMixin, generic.DetailView):
    queryset = models.Commit.objects.all()
    template_name = "repositories/commit_details.html"
    context_object_name = "commit"
    pk_url_kwarg = "commit_id"

    def get_queryset(self) -> QuerySet[Any]:
        return self.queryset.filter(repository__repository_members=self.request.user)


class CommitCreateView(LoginRequiredMixin, generic.CreateView):
    queryset = models.Commit.objects.all()
    template_name = "repositories/commit_create.html"
    form_class = forms.CommitCreateForm

    def form_valid(self, form: forms.CommitCreateForm) -> HttpResponse:
        instance = form.save(False)
        instance.repository_id = self.kwargs["pk"]
        instance.author = self.request.user
        instance = form.save()
        previous_commit = models.Commit.objects.filter(
            repository=instance.repository, created_at_lt=instance.created_at
        ).first()
        instance.changes = XMLDiffToDeltaConverter(
            get_ooxml(instance.document.path),
            Comparator(previous_commit.document.path, instance.document.path).compare(),
        ).convert()
        return HttpResponseRedirect(self.get_success_url())


class MergeFormView(LoginRequiredMixin, generic.FormView):
    form_class = forms.MergeDocumentForm
    template_name = "repositories/merge.html"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.GET.get("path", None):
            return render(request, "repositories/merge_details.html", {"path": request.GET.get("path", None)})
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: forms.MergeDocumentForm) -> HttpResponse:
        last_commit = models.Repository.objects.get(pk=self.kwargs["id"]).commits.first
        left_document = last_commit.document
        rigth_document = form.cleaned_data["rigth_document"]
        left_document_path = left_document.path
        rigth_document_path = os.path.join(
            settings.MEDIA_ROOT,
            "tmp",
            f"{generate_random_hash(15)}.{rigth_document.data.name.split('.')[-1].lower()}",
        )

        with open(rigth_document_path, "w") as file:
            for chunk in rigth_document.chunks():
                file.write(chunk)

        left_document_ooxml = get_ooxml(left_document_path)
        rigth_document_ooxml = get_ooxml(rigth_document_path)
        left_delta = last_commit.changes
        right_delta = XMLDiffToDeltaConverter(
            left_document_ooxml,
            Comparator(left_document_path, rigth_document_path).compare(),
        ).convert()
        document = Merger(left_delta, right_delta, left_document_ooxml, rigth_document_ooxml).merge()
        docx_compare_path = os.path.join(
            settings.MEDIA_ROOT,
            "tmp",
            f"{generate_random_hash(15)}.docx",
        )
        convert_ooxml_to_docx(document, docx_compare_path)
        pdf_compare_path = os.path.join(
            settings.MEDIA_ROOT,
            "compare",
            f"{generate_random_hash(15)}.pdf",
        )

        convert_to_pdf(docx_compare_path, pdf_compare_path)

        return redirect(reverse("merge", args=[self.kwargs["pk"]]) + f"?path={pdf_compare_path}")


@login_required
def add_member_to_repository(request, pk):
    user = User.objects.filter(username=request.POST.get("username", None)).first()
    repository = get_object_or_404(models.Repository, pk=pk)
    if user:
        if not repository.repository_members.filter(username=user.username).exists():
            repository.repository_members.add(user)
    return redirect("repositories:repository_settings", pk=pk)


@login_required
def delete_member_from_repository(request, pk):
    user = User.objects.filter(username=request.POST.get("username", None)).first()
    repository = get_object_or_404(models.Repository, pk=pk)
    if user:
        if repository.repository_members.filter(username=user.username).exists():
            repository.repository_members.remove(user)
    return redirect("repositories:repository_settings", pk=pk)
