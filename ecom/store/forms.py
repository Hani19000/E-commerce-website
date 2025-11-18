from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, SetPasswordForm, PasswordResetForm
from django import forms
from .models import Profile
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox


User = get_user_model()

class UserInfoForm(forms.ModelForm):
	phone = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'phone number'}), required=False)
	address1 = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'address1'}), required=False)
	address2 = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'address2'}), required=False)
	city = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'city'}), required=False)
	state = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'state'}), required=False)
	zipcode = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'zipcode'}), required=False)
	country = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'country'}), required=False)

	class Meta :
		model = Profile
		fields = ('phone', 'address1', 'address2', 'city', 'state', 'zipcode', 'country')

#changer le MDP quand l'utiisateur est deja login
class ChangePasswordForm(SetPasswordForm):
	class Meta:
		model = User
		field = ['new_password1', 'new_password2']

#changer le MDP quand l'utiisateur n'est pas login
class PasswordResetForm(PasswordResetForm):
	def __init__(self, *args, **kwargs):
		super(PasswordResetForm, self).__init__(*args, **kwargs)

	captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

class UpdateUserForm(UserChangeForm):
	email = forms.EmailField(label="Email Address", widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'jozetzthn.doe@example.com', 'id':'email'}), required=False)
	first_name = forms.CharField(label="First Name", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'John', 'id':'first_name'}), required=False)
	last_name = forms.CharField(label="Last Name", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Doe', 'id':'last_name'}), required=False)

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email')

	def __init__(self, *args, **kwargs):
		super(UpdateUserForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'johndoe'
		self.fields['username'].widget.attrs['id'] = 'username'
		self.fields['username'].label = 'Username'
		self.fields['username'].help_text = '<small>Choose a unique username (letters, numbers, and underscores only)</small>'


class SignInForm(AuthenticationForm):
	def __init__(self, *args, **kwargs):
		super(SignInForm, self).__init__(*args, **kwargs)
	username  = forms.CharField(
		label="Username or Email",
		widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter your email', 'id':'username'}),
		required=True
	)
	password = forms.CharField(
		label="Password",
		widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Enter your password', 'id':'password'}),
		required=True
	)

	captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="Email Address", widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'jozetzthn.doe@example.com', 'id':'email'}), required=False)
	first_name = forms.CharField(label="First Name", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'John', 'id':'first_name'}), required=False)
	last_name = forms.CharField(label="Last Name", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Doe', 'id':'last_name'}), required=False)

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
