import datetime

from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .models import Category, Post, Comment

from django.contrib.auth.decorators import login_required
from .forms import EditProfileForm
from django.shortcuts import redirect
from django.contrib import messages
from .forms import PostForm, CommentForm
from django.db.models import Count
from django.urls import reverse


User = get_user_model()


def index(request):
    template_name = 'blog/index.html'

    posts = Post.objects.annotate(
        comment_count=Count('comments')
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.datetime.now()
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


def post_detail(request, id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(Post, pk=id)

    is_author = request.user.is_authenticated and post.author == request.user

    if not is_author:
        post = get_object_or_404(
            Post,
            pk=id,
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.datetime.now()
        )

    comments = post.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', id=id)
    else:
        form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    posts = Post.objects.annotate(
        comment_count=Count('comments')
    ).filter(
        category=category,
        is_published=True,
        pub_date__lte=datetime.datetime.now()
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


def profile_view(request, username):
    template_name = 'blog/profile.html'
    profile = get_object_or_404(User, username=username)

    posts = profile.post_set.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    is_owner = (
        request.user.is_authenticated and request.user.username == username)

    context = {
        'profile': profile,
        'page_obj': page_obj,
        'is_owner': is_owner,
    }
    return render(request, template_name, context)


@login_required
def edit_profile(request):
    template_name = 'blog/user.html'
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect(
                reverse('blog:profile',
                        kwargs={'username': request.user.username}))
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = EditProfileForm(instance=request.user)

    context = {
        'form': form
    }

    return render(request, template_name, context)


@login_required
def create_post(request):
    template_name = 'blog/create.html'
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Публикация успешно создана!')
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()

    context = {
        'form': form}

    return render(request, template_name, context)


@login_required
def edit_post(request, post_id):
    template_name = 'blog/create.html'
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Публикация успешно обновлена!')
            return redirect(
                reverse('blog:post_detail',
                        kwargs={'id': post_id}))
    else:
        form = PostForm(instance=post)

    context = {
        'form': form}

    return render(request, template_name, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect('blog:post_detail', id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)

    context = {
        'form': form,
        'comment': comment
    }

    return render(request, template_name, context)


@login_required
def delete_post(request, post_id):
    template_name = 'blog/create.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Публикация удалена!')
        return redirect(
            reverse('blog:profile',
                    kwargs={'username': request.user.username}))

    context = {
        'form': None,
        'post': post}

    return render(request, template_name, context)


@login_required
def delete_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий удален!')
        return redirect('blog:post_detail', id=post_id)

    context = {
        'form': None,
        'comment': comment
    }

    return render(request, template_name, context)
