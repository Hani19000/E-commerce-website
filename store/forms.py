from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms


class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="Email Address", widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'jozetzthn.doe@example.com', 'id':'email'}))
	first_name = forms.CharField(label="First Name", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'John', 'id':'first_name'}))
	last_name = forms.CharField(label="Last Name", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Doe', 'id':'last_name'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'johndoe'
		self.fields['username'].widget.attrs['id'] = 'username'
		self.fields['username'].label = 'Username'
		self.fields['username'].help_text = '<small>Choose a unique username (letters, numbers, and underscores only)</small>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Enter a strong password'
		self.fields['password1'].widget.attrs['id'] = 'password'
		self.fields['password1'].label = 'Password'
		self.fields['password1'].help_text = '<small>At least 8 characters with letters and numbers</small>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'
		self.fields['password2'].widget.attrs['id'] = 'password2'
		self.fields['password2'].label = 'Confirm Password'
		self.fields['password2'].help_text = '<small>Enter the same password as before, for verification.</small>'
