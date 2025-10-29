from django.contrib import admin
from django.utils.html import format_html
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    def thumb(self, obj):
        if getattr(obj, 'thumbnail', None):
            try:
                return format_html('<img src="{}" alt="" style="width:48px;height:auto;border-radius:6px;box-shadow:0 1px 6px rgba(0,0,0,.2)">', obj.thumbnail.url)
            except Exception:
                return ''
        return ''
    thumb.short_description = 'Image'

    list_display = ('thumb','title', 'author', 'category', 'created_at', 'published', 'key')
    list_display_links = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title', 'content', 'author', 'tags', 'category')
    list_filter = ('published', 'created_at', 'category')
    readonly_fields = ('key',)
