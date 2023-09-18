from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView

from .models import Post
from .forms import EmailPostForm


# Create your views here.


def post_share(request, post_id: int):
    # Retrieve the post by id
    post = get_object_or_404(Post, id=post_id)
    sent = False
    if request.method == 'POST':
        # Form has been submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Fields have passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends your read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'kwamefosu33@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


def post_list(request):
    all_posts = Post.published.all()
    # Pagination with 3 posts per page
    paginator = Paginator(all_posts, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer, deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range, deliver the last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year: int, month: int, day: int, post: Post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request, 'blog/post/detail.html', {'post': post})


class PostListView(ListView):
    """
    Alternate Post List View
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
