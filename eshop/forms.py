from django.contrib.auth.models import User
from django import forms
from .models import Profile


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        self.fields['password'].required = False
        self.fields['password2'].required = False

    def clean(self):
        super(UserForm, self).clean()
        data = self.cleaned_data
        if data["username"] == True:
            raise forms.ValidationError({'username': ["username already exists"]})
        elif data["password"] == "":
            raise forms.ValidationError({'password': ["Password invalid."]})
        elif data["password"] != data["password2"]:
            raise forms.ValidationError({'password': ["Passwords must be the same."]})
        elif len(data["password"]) < 1:
            raise forms.ValidationError({'password': ["password must be at least 6 characters"]})

        if data["email"] == True:
            raise forms.ValidationError({'email': ["email is already in use"]})

        return data

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'placeholder': 'Confirm your password'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'placeholder': 'Your password'}))
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your username', }),
        max_length=30,
        required=True)
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email'}),
        required=True,
        max_length=75)



    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']


class ProfileForm(forms.ModelForm):
    job = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    street = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    street2 = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    country = forms.ChoiceField(required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=Profile.pays,
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    mobile = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    class Meta:
        model = Profile
        fields = ('avatar','street','city','country', 'mobile','job','title')

