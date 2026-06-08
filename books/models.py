from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


class Book(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
    ]

    # Seller info
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='books_selling')

    # Book details
    book_name = models.CharField(max_length=200)
    publisher_name = models.CharField(max_length=200)
    edition_year = models.PositiveIntegerField()
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    price = models.PositiveIntegerField()  # in rupees
    description = models.TextField(blank=True, null=True)
    book_photo = models.ImageField(upload_to='book_photos/')

    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(default=timezone.now)
    seller_agreed_terms = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.book_name} by {self.seller.student_name}"


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='purchase_requests')
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='purchase_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    message = models.TextField(blank=True, null=True)  # optional message from buyer to seller
    buyer_agreed_terms = models.BooleanField(default=False)

    class Meta:
        # one buyer can only send one request per book
        unique_together = ('book', 'buyer')

    def __str__(self):
        return f"{self.buyer.student_name} → {self.book.book_name} ({self.status})"