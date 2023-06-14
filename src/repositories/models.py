import os

from django.conf import settings
from django.db import models
from django.urls import reverse

from documents_workers.utils import convert_ooxml_to_docx, convert_to_pdf
from documents_workers.visualizer import DocumentVisualizer
from repositories.utils import get_ooxml, validate_xml


class Repository(models.Model):
    name = models.CharField(max_length=250, verbose_name="Название", blank=False)
    repository_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="repositories.RepositoryMember",
        verbose_name="Участники",
        related_name="repositories",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Repository"
        verbose_name_plural = "Repositories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("repositories:repository_view", kwargs={"pk": self.pk})


class RepositoryMember(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Repository member"
        verbose_name_plural = "Repository members"

    def __str__(self):
        return f"{self.repository} - {self.user}"

    def get_absolute_url(self):
        return reverse("RepositoryMember_detail", kwargs={"pk": self.pk})


class Commit(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="commits")
    message = models.CharField(max_length=100)
    changes = models.TextField(validators=[validate_xml])
    document = models.FileField(upload_to="documents/%Y/%m/%d")
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name="commits")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Commit"
        verbose_name_plural = "Commits"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.repository} - {self.message[:50]}"

    def get_absolute_url(self):
        return reverse("repositories:commit_view", kwargs={"pk": self.repository.pk, "commit_id": self.pk})

    @property
    def pdf_doocument(self):
        pdf_document_path = os.path.join(settings.MEDIA_ROOT, "tmp", f"commit-{str(self.pk)}.pdf")
        if not os.path.exists(pdf_document_path):
            convert_to_pdf(self.document.path, pdf_document_path)

        return pdf_document_path

    def get_compare_document(self):
        previous_commit = Commit.objects.filter(repository=self.repository, created_at_lt=self.created_at).first()
        if previous_commit:
            tmp_docx_path = os.path.join(settings.MEDIA_ROOT, "tmp", f"commit-compare-{str(self.pk)}.docx")
            convert_ooxml_to_docx(
                DocumentVisualizer(self.changes, get_ooxml(previous_commit.document.path)), tmp_docx_path
            )
            pdf_document_path = os.path.join(settings.MEDIA_ROOT, "tmp", f"commit-{str(self.pk)}.pdf")
            if not os.path.exists(pdf_document_path):
                convert_to_pdf(self.document.path, pdf_document_path)

            return pdf_document_path


class DocumentsCache(models.Model):
    document = models.FileField(upload_to="cache/%Y/%m/%d")

    class Meta:
        verbose_name = "Cache Document"
        verbose_name_plural = "Cache Documents"
