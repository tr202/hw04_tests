from functools import wraps

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from users.check_user import authorized_only

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


def is_post_author(view):
    @wraps(view)
    def wrap(request, post_id, *args, **kwargs):
        if request.user == Post.objects.get(pk=post_id).author:
            return view(request, post_id, *args, **kwargs)
        return HttpResponseRedirect(
            reverse('posts:post_detail', args=(post_id,))
        )
    return wrap


@authorized_only
@is_post_author
def post_edit(request, post_id):
    form = PostForm(request.POST or None)
    if form.is_valid():
        text = form.cleaned_data['text']
        group = form.cleaned_data['group']
        Post.objects.filter(pk=post_id).update(text=text, group=group)
        return HttpResponseRedirect(
            reverse('posts:post_detail', args=(post_id,))
        )
    post = Post.objects.get(pk=post_id)
    form = PostForm(instance=post)
    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id,
    }
    return render(request, 'posts/create_post.html', context)


@authorized_only
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        text = form.cleaned_data['text']
        group = form.cleaned_data['group']
        author = request.user
        p = Post(author=author, text=text, group=group)
        p.save(force_insert=True)
        return redirect('posts:profile', author)
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'posts/create_post.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, settings.PAGE_POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'post_list': post_list,
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGE_POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.PAGE_POSTS_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)
