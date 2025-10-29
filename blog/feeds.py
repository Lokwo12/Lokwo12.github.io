from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Post


class LatestPostsFeed(Feed):
    title = "Denis Lokwo — Blog"
    link = "/blog/"
    description = "Latest posts from the blog"

    def items(self):
        return Post.objects.filter(published=True).order_by('-created_at')[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        # Simple truncation; could render Markdown/HTML if used
        return (item.content or '')[:300]

    def item_link(self, item):
        return item.get_absolute_url()
