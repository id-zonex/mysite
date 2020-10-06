from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .models import Post, FavouriteTags
from .forms import *
from taggit.models import Tag
from django.db.models import Count
from django.contrib.auth.models import User

USER = User.objects.get(username='admin')

def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    context = {
        'page': page,
        'posts': posts,
        'tag': tag,
    }
    return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    comments = post.comments.filter(active=True)
    new_comment = None
    comment_form = CommentForm()
    save_form = SavedForm()
    if request.method == 'POST':
        if 'comment' in request.POST:
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.post = post
                new_comment.save()

        if 'save' in request.POST:
            try:
                save_data = SavedPosts.objects.get(post=post, user=USER)
            except:
                create_data = SavedPosts.objects.create(post=post, user=USER)
                create_data.save()
                print('ulala')
            else:
                save_data.delete()
                print('no')
    else:
        comment_form = CommentForm()
        save_form = SavedForm()

    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'save_form': save_form,
    }
    return render(request,
                  'blog/post/detail.html', context)


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            sent = True
    else:
        form = EmailPostForm()

    context = {
        'post': post,
        'form': form,
        'sent': sent
    }
    return render(request, 'blog/post/share.html', context)


def post_recommendation(request):
    tags_list = []
    tags = FavouriteTags.objects.all()

    for tag in tags:
        tags_list.append(tag.tag_name.id)
    print(tags_list)
    recommended_posts = Post.published.filter(tags__in=tags_list)
    recommended_posts = recommended_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')
    paginator = Paginator(recommended_posts, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,

    }
    return render(request, 'blog/post/recommendation.html', context)