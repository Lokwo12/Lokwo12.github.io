from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post
from django.utils.text import slugify
from django.views.decorators.cache import cache_page

@cache_page(60 * 10)
def post_list(request):
    q = request.GET.get('q', '').strip()
    posts_qs = Post.objects.filter(published=True)
    if q:
        posts_qs = posts_qs.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q) |
            Q(author__icontains=q) |
            Q(tags__icontains=q) |
            Q(category__icontains=q)
        )
    paginator = Paginator(posts_qs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/post_list.html', {'page_obj': page_obj, 'q': q, 'posts': page_obj.object_list})

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    # Rough reading time: 200 wpm
    words = len(post.content.split()) if post.content else 0
    reading_time = max(1, round(words / 200))
    # Prev/next posts
    newer = Post.objects.filter(published=True, created_at__gt=post.created_at).order_by('created_at').first()
    older = Post.objects.filter(published=True, created_at__lt=post.created_at).order_by('-created_at').first()
    return render(request, 'blog/post_detail.html', {'post': post, 'reading_time': reading_time, 'newer': newer, 'older': older})


@cache_page(60 * 10)
def post_list_by_category(request, category):
    """Pretty URL filter by category slug, reusing the same template."""
    posts_qs = Post.objects.filter(published=True)
    cat_slug = (category or '').strip().lower()
    # Filter in Python to match slugified category values reliably
    filtered = [p for p in posts_qs if p.category and slugify(p.category) == cat_slug]
    paginator = Paginator(filtered, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    ctx = {
        'page_obj': page_obj,
        'q': '',
        'posts': page_obj.object_list,
        'active_category': category,
        'base_path': request.path,
    }
    return render(request, 'blog/post_list.html', ctx)


@cache_page(60 * 10)
def post_list_by_tag(request, tag):
    """Pretty URL filter by tag slug, reusing the same template."""
    posts_qs = Post.objects.filter(published=True)
    tag_slug = (tag or '').strip().lower()
    filtered = []
    for p in posts_qs:
        tags = getattr(p, 'tag_list', []) or []
        if any(slugify(t) == tag_slug for t in tags):
            filtered.append(p)
    paginator = Paginator(filtered, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    ctx = {
        'page_obj': page_obj,
        'q': '',
        'posts': page_obj.object_list,
        'active_tag': tag,
        'base_path': request.path,
    }
    return render(request, 'blog/post_list.html', ctx)
