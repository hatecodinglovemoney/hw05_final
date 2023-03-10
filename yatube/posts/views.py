from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_ON_PAGE_NUMB
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def paginator_page(queryset, request, posts_on_page_numb=POSTS_ON_PAGE_NUMB):
    return Paginator(queryset, posts_on_page_numb).get_page(
        request.GET.get("page"))


def index(request):
    return render(request, "posts/index.html", {
        "page_obj": paginator_page(Post.objects.all(),
                                   request)
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, "posts/group_list.html", {
        "group": group,
        "page_obj": paginator_page(group.posts.all(),
                                   request)
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    return render(request, "posts/profile.html", {
        "author": author,
        "page_obj": paginator_page(author.posts.all(), request),
        "following":
            request.user != author
            and request.user.is_authenticated
            and Follow.objects.filter(
                user=request.user,
                author=author,
        ).exists(),  # тесты на сайте принимают только так:(
    })


def post_detail(request, post_id):
    return render(request, "posts/post_detail.html", {
        "post": get_object_or_404(Post, pk=post_id),
        "form": CommentForm(request.POST or None),
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None,)
    if not form.is_valid():
        return render(request, "posts/create_post.html", {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("posts:post_detail", post.pk)
    form = PostForm(request.POST or None,
                    instance=post,
                    files=request.FILES or None)
    if not form.is_valid():
        return render(request, "posts/create_post.html", {
            "form": form,
            "post": post,
        })
    form.save()
    return redirect("posts:post_detail", post.pk)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    post = Post.objects.filter(author__following__user=request.user)
    return render(request, "posts/follow.html", {
        "page_obj": paginator_page(post, request)
    })


@login_required
def profile_follow(request, username):
    if username != request.user.username:
        user = get_object_or_404(User, username=username)
        Follow.objects.get_or_create(user=request.user, author=user)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow,
        author__username=username,
        user=request.user,
    ).delete()
    return redirect("posts:profile", username=username)
