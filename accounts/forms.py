from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from .models import College

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    student_name = forms.CharField(max_length=100)
    college = forms.ModelChoiceField(
    queryset=College.objects.filter(is_active=True),
    label='Select Your College',
    empty_label='-- Select your college --',
    help_text='⚠ This cannot be changed after registration.'
)
    branch = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=15)
    year = forms.ChoiceField(choices=[
        (1, '1st Year'),
        (2, '2nd Year'),
        (3, '3rd Year'),
        (4, '4th Year'),
    ])
    city = forms.CharField(max_length=100)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    id_card_photo = forms.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'student_name',
            'college',
            'branch',
            'year',
            'city',
            'address',
            'phone_number',
            'id_card_photo',
            'password1',
            'password2',
        ]


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')


class EditProfileForm(forms.ModelForm):

    phone_number = forms.CharField(
        max_length=15,
        required=True,
        error_messages={'required': 'Phone number is required.'}
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'student_name',
            'college_name',
            'branch',
            'year',
            'city',
            'address',
            'phone_number',
            'profile_photo',
            'cover_photo',
        ]
        widgets = {
            'year': forms.Select(choices=[
                (1, '1st Year'),
                (2, '2nd Year'),
                (3, '3rd Year'),
                (4, '4th Year'),
            ]),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class CollegeAdminRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    student_name = forms.CharField(max_length=100, label='Full Name')
    city = forms.CharField(max_length=100)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    phone_number = forms.CharField(max_length=15)

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'student_name',
            'city',
            'address',
            'phone_number',
            'password1',
            'password2',
        ]