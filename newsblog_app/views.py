from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views import generic
from django.template.defaultfilters import slugify
from django.urls import reverse_lazy, reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
import requests
from decouple import config


from .models import Blog
from .forms import UserCreateForm
from .serializers import BlogSerializer


# for cache
articles = []


@login_required
def index(request):
    # use cache
    global articles
    # TODO: NOTE: (render spins down after certain time,
    # so no need to handle cache refresh for now)
    if not articles:
        API_KEY = config("NEWS_API_KEY")
        r = requests.get(
            f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}&pageSize=8"
        )

        # TODO: chk status code
        print("stts", r.status_code)

        articles = r.json()["articles"]

    blogs = Blog.objects.filter(author=request.user).order_by("-created_on")
    if request.user.is_superuser:
        # show all blogs for the admin
        blogs = Blog.objects.order_by("-created_on")

    # .json().articles can work as list of dictionary itself...

    return render(
        request=request,
        template_name="index.html",
        context={"blog_list": blogs, "news_list": articles},
    )


#################################################################
# user
#################################################################
class UserCreateView(generic.CreateView):
    form_class = UserCreateForm
    template_name = "register.html"

    def get_success_url(self):
        return reverse("user-detail", kwargs={"pk": self.object.id})


def login_view(request):
    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                # NOTE: also respect ?next parameter provided by Django
                return redirect(request.GET.get("next") or "index")

    form.helper = FormHelper()
    form.helper.add_input(Submit("submit", "Submit"))
    return render(request=request, template_name="login.html", context={"form": form})


def logout_view(request):
    messages.info(request, "Logged out successfully.")
    logout(request)
    return redirect("login")


class UserDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "user_detail.html"
    # success_url = reverse_lazy('blog-detail')
    model = User


#################################################################
# blog
#################################################################
class BlogListView(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        if self.request.user.is_superuser:
            # show all blogs for the admin
            return Blog.objects.order_by("-created_on")

        return Blog.objects.filter(author=self.request.user).order_by("-created_on")


class BlogDetailView(generic.DetailView):
    model = Blog
    # template_name = 'blog_detail.html'


class BlogDeleteView(LoginRequiredMixin, PermissionRequiredMixin, generic.DeleteView):
    model = Blog
    success_url = reverse_lazy("index")
    permission_required = "delete_own_blog"

    def has_permission(self):
        obj = self.get_object()
        return obj.can_delete(self.request.user)


class BlogCreateView(LoginRequiredMixin, generic.CreateView):
    model = Blog
    fields = ["title", "content"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.add_input(Submit("submit", "Submit"))
        return form

    def form_valid(self, form):
        # append author, slug and save
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        # TODO: check if starts with "add", because there's a URL "blogs/add"
        self.object.slug = slugify(self.object.title)
        self.object.save()
        return super().form_valid(form)


class BlogUpdateView(LoginRequiredMixin, PermissionRequiredMixin, generic.UpdateView):
    model = Blog
    fields = ["title", "content"]
    permission_required = "edit_own_blog"

    def has_permission(self):
        obj = self.get_object()
        return obj.can_edit(self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.add_input(Submit("submit", "Update"))
        return form

    def form_valid(self, form):
        # append author, slug and save
        self.object = form.save(commit=False)
        # TODO: check if starts with "add", because there's a URL "blogs/add"
        self.object.slug = slugify(self.object.title)
        self.object.save()
        return super().form_valid(form)


#################################################################
# blog admin API
#################################################################
class BlogViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAdminUser] # (IsAdminUser is the default perm class already)
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
