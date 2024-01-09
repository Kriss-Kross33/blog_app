from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.db.models import Count
from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


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


def post_list(request, tag_slug=None):
    all_posts = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        all_posts = all_posts.filter(tags__in=[tag])
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
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag})


def post_detail(request, year: int, month: int, day: int, post: Post):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # List of active comments for the post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()
    post_tag_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tag_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request,
                  'blog/post/detail.html',
                  {'post': post, 'form': form, 'similar_posts': similar_posts,
                   "comments": comments})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # Comment has been posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a comment object without saving to db
        comment = form.save(commit=False)
        # Assign post to the comment
        comment.post = post
        # Save the comment to db
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})


class PostListView(ListView):
    """
    Alternate Post List View
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
