from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post


# Create your views here.


def post_list(request):
    all_posts = Post.published.all()
    # Pagination with 3 posts per page
    paginator = Paginator(all_posts, 3)
    page_number = request.GET.get('page', 1)
    posts = paginator.page(page_number)
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post})
