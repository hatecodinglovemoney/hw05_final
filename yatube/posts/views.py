from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_ON_PAGE_NUMB
from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def paginator_page(queryset, request):
    return Paginator(queryset, POSTS_ON_PAGE_NUMB).get_page(
        request.GET.get("page"))


def index(request):
    return render(
        request,
        "posts/index.html",
        {"page_obj": paginator_page(Post.objects.all(), request)},
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(
        request,
        "posts/group_list.html",
        {"group": group,
         "page_obj": paginator_page(group.posts.all(), request)},
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    self_profile = True
    following = None
    if request.user.is_authenticated & (request.user != author):
        self_profile = False
        auth = User.objects.filter(following__user=request.user)
        if author in auth:
            following = True
    return render(
        request,
        "posts/profile.html",
        {
            "author": author,
            "page_obj": paginator_page(author.posts.all(), request),
            "following": following,
            "self_profile": self_profile,
        },
    )


def post_detail(request, post_id):
    return render(
        request,
        "posts/post_detail.html",
        {
            "post": get_object_or_404(Post, pk=post_id),
            "comments": Comment.objects.filter(
                post_id=post_id).order_by("-created"),
            "form": CommentForm(request.POST or None),
        },
    )


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, "posts/create_post.html", {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    form.save()
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
        return render(
            request,
            "posts/create_post.html",
            {
                "form": form,
                "post": post,
            },
        )
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
    return render(
        request,
        "posts/follow.html",
        {"page_obj": paginator_page(post, request)}
    )


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if (request.user != user) & (
        Follow.objects.filter(user=request.user, author=user).count() < 1
    ):
        Follow.objects.create(author=user, user=request.user)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=user).delete()
    return redirect("posts:profile", username=username)
