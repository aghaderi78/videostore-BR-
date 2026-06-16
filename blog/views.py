from django.shortcuts import render, get_object_or_404
from .models import Post, Category


def post_list_view(request):
    posts = Post.objects.filter(is_published=True)
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=selected_category)
    return render(request, 'blog/list.html', {
        'posts': posts,
        'categories': categories,
        'selected_category': selected_category,
    })


def post_detail_view(request, slug):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    post.views_count += 1
    post.save(update_fields=['views_count'])
    related = Post.objects.filter(is_published=True, category=post.category).exclude(id=post.id)[:3]
    return render(request, 'blog/detail.html', {
        'post': post,
        'related': related,
    })
