from notifications.utils import create_notification
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Book, PurchaseRequest
from .forms import SellBookForm, PurchaseRequestForm


def book_list_view(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(status='available').order_by('-created_at')
    
    if query:
        books = books.filter(book_name__icontains=query)
    
    return render(request, 'books/book_list.html', {
        'books': books,
        'query': query,
    })


def book_detail_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    already_requested = False
    
    if request.user.is_authenticated:
        already_requested = PurchaseRequest.objects.filter(
            book=book, buyer=request.user
        ).exists()
    
    form = PurchaseRequestForm()
    
    return render(request, 'books/book_detail.html', {
        'book': book,
        'already_requested': already_requested,
        'form': form,
    })


@login_required
def send_purchase_request_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    # seller cannot buy their own book
    if book.seller == request.user:
        messages.error(request, 'You cannot send a purchase request for your own book.')
        return redirect('books:detail', pk=pk)
    
    # check if already requested
    if PurchaseRequest.objects.filter(book=book, buyer=request.user).exists():
        messages.error(request, 'You have already sent a purchase request for this book.')
        return redirect('books:detail', pk=pk)
    
    if not request.user.phone_number:
        messages.error(request, 'Please add your phone number in your profile before sending a purchase request.')
        return redirect('accounts:edit_profile')
    
    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        if form.is_valid():
            purchase_request = PurchaseRequest.objects.create(
    book=book,
    buyer=request.user,
    message=form.cleaned_data.get('message', ''),
    buyer_agreed_terms=True
)
            book.status = 'pending'
            book.save()
            create_notification(
    recipient=book.seller,
    sender=request.user,
    notification_type='purchase_request',
    message=f'{request.user.student_name} sent a purchase request for your book "{book.book_name}".',
    link=f'/books/my-books/'
)

            # notify seller by email
            send_mail(
                subject='Someone wants to buy your book — Social Network',
                message=render_to_string('books/email/purchase_request_email.html', {
                    'book': book,
                    'buyer': request.user,
                    'purchase_request': purchase_request,
                }),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[book.seller.email],
                fail_silently=False,
                html_message=render_to_string('books/email/purchase_request_email.html', {
                    'book': book,
                    'buyer': request.user,
                    'purchase_request': purchase_request,
                }),
            )
            messages.success(request, 'Purchase request sent successfully. Seller will be notified.')
            return redirect('books:detail', pk=pk)
    
    return redirect('books:detail', pk=pk)


@login_required
def sell_book_view(request):
    if request.method == 'POST':
        form = SellBookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.seller = request.user
            book.seller_agreed_terms = True
            book.save()
            messages.success(request, 'Your book has been listed successfully.')
            if not request.user.phone_number:
                messages.error(request, 'Please add your phone number in your profile before listing a book.')
                return redirect('accounts:edit_profile')
    
            if request.method == 'POST':
                return redirect('books:list')
    else:
        form = SellBookForm()

    
    
    return render(request, 'books/sell_book.html', {'form': form})




@login_required
def approve_request_view(request, request_id):
    purchase_request = get_object_or_404(PurchaseRequest, pk=request_id)
    
    # only seller can approve
    if purchase_request.book.seller != request.user:
        messages.error(request, 'You are not authorized to approve this request.')
        return redirect('books:list')
    
    purchase_request.status = 'approved'
    purchase_request.save()
    
    purchase_request.book.status = 'sold'
    purchase_request.book.save()

    create_notification(
    recipient=purchase_request.buyer,
    sender=request.user,
    notification_type='purchase_approved',
    message=f'Your purchase request for "{purchase_request.book.book_name}" has been approved. Check your email for contact details.',
    link='/books/my-books/'
)

    # send contact details to both buyer and seller
    # email to buyer
    send_mail(
        subject='Your purchase request has been approved — Social Network',
        message=render_to_string('books/email/approval_email_buyer.html', {
            'book': purchase_request.book,
            'seller': purchase_request.book.seller,
            'buyer': purchase_request.buyer,
        }),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[purchase_request.buyer.email],
        fail_silently=False,
        html_message=render_to_string('books/email/approval_email_buyer.html', {
            'book': purchase_request.book,
            'seller': purchase_request.book.seller,
            'buyer': purchase_request.buyer,
        }),
    )

    # email to seller
    send_mail(
        subject='You approved a purchase request — Social Network',
        message=render_to_string('books/email/approval_email_seller.html', {
            'book': purchase_request.book,
            'seller': purchase_request.book.seller,
            'buyer': purchase_request.buyer,
        }),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[purchase_request.book.seller.email],
        fail_silently=False,
        html_message=render_to_string('books/email/approval_email_seller.html', {
            'book': purchase_request.book,
            'seller': purchase_request.book.seller,
            'buyer': purchase_request.buyer,
        }),
    )

    messages.success(request, 'Request approved. Contact details sent to both parties.')
    return redirect('books:my_books')


@login_required
def reject_request_view(request, request_id):
    purchase_request = get_object_or_404(PurchaseRequest, pk=request_id)
    
    if purchase_request.book.seller != request.user:
        messages.error(request, 'You are not authorized to reject this request.')
        return redirect('books:list')
    
    purchase_request.status = 'rejected'
    purchase_request.save()
    
    purchase_request.book.status = 'available'
    purchase_request.book.save()

    create_notification(
    recipient=purchase_request.buyer,
    sender=request.user,
    notification_type='purchase_rejected',
    message=f'Your purchase request for "{purchase_request.book.book_name}" was rejected by the seller.',
    link='/books/list/'
)

    # notify buyer
    send_mail(
        subject='Your purchase request was rejected — Social Network',
        message=f"Hi {purchase_request.buyer.student_name}, your request for '{purchase_request.book.book_name}' was rejected by the seller.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[purchase_request.buyer.email],
        fail_silently=False,
    )

    messages.success(request, 'Request rejected.')
    return redirect('books:my_books')


@login_required
def my_books_view(request):
    my_listings = Book.objects.filter(seller=request.user).order_by('-created_at')
    incoming_requests = PurchaseRequest.objects.filter(
        book__seller=request.user,
        status='pending'
    ).order_by('-created_at')

    # purchase history - books i requested and got approved
    purchase_history = PurchaseRequest.objects.filter(
        buyer=request.user,
        status='approved'
    ).order_by('-created_at')

    return render(request, 'books/my_books.html', {
        'my_listings': my_listings,
        'incoming_requests': incoming_requests,
        'purchase_history': purchase_history,
    })

@login_required
def delete_book_view(request, pk):
    book = get_object_or_404(Book, pk=pk, seller=request.user)
    book.delete()
    messages.success(request, 'Book listing removed successfully.')
    return redirect('books:my_books')

@login_required
def edit_book_view(request, pk):
    book = get_object_or_404(Book, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = SellBookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book details updated successfully.')
            return redirect('books:my_books')
    else:
        form = SellBookForm(instance=book)
    
    return render(request, 'books/edit_book.html', {'form': form, 'book': book})
    