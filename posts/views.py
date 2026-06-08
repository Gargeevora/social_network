from notifications.utils import create_notification
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, Like, Comment
from .forms import PostForm, CommentForm
from connections.models import Connection
from accounts.models import CustomUser
from events.models import Event
from django.utils import timezone
from django.db.models import Case, When, IntegerField, Value

def feed_view(request):
    friend_ids = []
    friends = []
    suggested_people = []
    upcoming_events = []

    if request.user.is_authenticated:
        connected_users = Connection.objects.filter(
            sender=request.user, status='accepted'
        ).values_list('receiver', flat=True)
        connected_users2 = Connection.objects.filter(
            receiver=request.user, status='accepted'
        ).values_list('sender', flat=True)

        friend_ids = list(connected_users) + list(connected_users2) + [request.user.id]

        friend_posts = Post.objects.filter(author__in=friend_ids).order_by('-created_at')
        other_posts = Post.objects.exclude(author__in=friend_ids).order_by('-created_at')
        posts = list(friend_posts) + list(other_posts)

        friends = CustomUser.objects.filter(pk__in=friend_ids).exclude(pk=request.user.pk)
        suggested_people = get_smart_suggestions(request.user, friend_ids)

        upcoming_events = Event.objects.filter(
            event_date__gte=timezone.now().date()
        ).order_by('event_date')[:3]

    else:
        posts = Post.objects.all().order_by('-created_at')

    comment_form = CommentForm()

    return render(request, 'posts/feed.html', {
        'posts': posts,
        'comment_form': comment_form,
        'friends': friends,
        'suggested_people': suggested_people,
        'upcoming_events': upcoming_events,
        'friend_ids': friend_ids,
    })

@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully.')
            return redirect('posts:feed')
    else:
        form = PostForm()

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
@require_POST
def like_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    create_notification(
    recipient=post.author,
    sender=request.user,
    notification_type='like',
    message=f'{request.user.student_name} liked your post.',
    link='/posts/'
)

    return JsonResponse({
        'liked': liked,
        'total_likes': post.total_likes(),
    })


@login_required
@require_POST
def add_comment_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.save()
        
        create_notification(
    recipient=post.author,
    sender=request.user,
    notification_type='comment',
    message=f'{request.user.student_name} commented on your post.',
    link='/posts/'
)
        return JsonResponse({
            'success': True,
            'comment_text': comment.text,
            'user_name': comment.user.student_name,
            'created_at': comment.created_at.strftime('%d %b %Y'),
            'total_comments': post.total_comments(),
        })
    return JsonResponse({'success': False})


@login_required
def delete_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, 'You cannot delete someone else\'s post.')
        return redirect('posts:feed')
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('posts:feed')

def get_smart_suggestions(user, friend_ids):
    candidates = CustomUser.objects.exclude(
        pk__in=friend_ids
    ).exclude(pk=user.pk)

    scored = []
    for person in candidates:
        score = 0
        if person.college_name.lower() == user.college_name.lower():
            score += 4
        if person.branch.lower() == user.branch.lower():
            score += 3
        if person.year == user.year:
            score += 2
        if person.city.lower() == user.city.lower():
            score += 1
        scored.append((score, person))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [person for score, person in scored[:5] if score > 0] or [person for score, person in scored[:5]]