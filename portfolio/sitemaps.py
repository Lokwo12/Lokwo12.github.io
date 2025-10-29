from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils.text import slugify
from blog.models import Post
from .models import Project


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        # Named URL patterns to include
        return [
            'portfolio:home',
            'portfolio:about',
            'portfolio:html_sitemap',
            'portfolio:gallery',
            'portfolio:project_list',
            'portfolio:contact',
            'portfolio:privacy',
            'portfolio:terms',
            'blog:post_list',
        ]

    def location(self, item):
        return reverse(item)


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Post.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.date


class BlogCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        cats = set()
        for p in Post.objects.filter(published=True).exclude(category__isnull=True).exclude(category=""):
            cats.add(slugify(p.category))
        return sorted(cats)

    def location(self, item):
        return reverse('blog:post_list_by_category', kwargs={'category': item})


class BlogTagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        tags = set()
        for p in Post.objects.filter(published=True):
            for t in (getattr(p, 'tag_list', []) or []):
                tags.add(slugify(t))
        return sorted(tags)

    def location(self, item):
        return reverse('blog:post_list_by_tag', kwargs={'tag': item})
