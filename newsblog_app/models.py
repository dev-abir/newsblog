from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField


# TODO: check on deletes, on updates


class Blog(models.Model):
    slug = models.CharField(max_length=50, unique=True)
    # updated_on = models.DateTimeField(auto_now= True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, unique=True)
    # content = models.TextField(max_length=1000)
    content = RichTextField()

    class Meta:
        permissions = [
            ("edit_own_blog", "Can edit own blog"),
            ("delete_own_blog", "Can delete own blog"),
        ]

    def get_absolute_url(self):
        return reverse("blog-detail", kwargs={"slug": self.slug})

    def can_edit(self, user):
        return self.author == user

    def can_delete(self, user):
        return self.author == user

    def __str__(self) -> str:
        return self.title
