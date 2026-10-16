from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Plano


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='E-mail ou usuário',
        widget=forms.TextInput(attrs={'placeholder': 'seu@email.com', 'autofocus': True, 'class': 'form-input'})
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'class': 'form-input'})
    )


class CriarUsuarioForm(forms.ModelForm):
    password = forms.CharField(label='Senha inicial', min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 6 caracteres', 'class': 'form-input'}))

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'username', 'email',
                  'empresa', 'telefone', 'plano', 'data_expiracao', 'ativo', 'observacoes']
        widgets = {
            'first_name':      forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome'}),
            'last_name':       forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Sobrenome'}),
            'username':        forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'usuario'}),
            'email':           forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@exemplo.com'}),
            'empresa':         forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome do escritório'}),
            'telefone':        forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(XX) 9XXXX-XXXX'}),
            'plano':           forms.Select(attrs={'class': 'form-input'}),
            'data_expiracao':  forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'ativo':           forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'observacoes':     forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Notas internas...'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class EditarUsuarioForm(forms.ModelForm):
    nova_senha = forms.CharField(label='Nova senha (deixe vazio para não alterar)',
        required=False, min_length=6,
        widget=forms.PasswordInput(attrs={'placeholder': 'Nova senha', 'class': 'form-input', 'autocomplete': 'new-password'}))

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'empresa',
                  'telefone', 'plano', 'data_expiracao', 'ativo', 'observacoes']
        widgets = {
            'first_name':     forms.TextInput(attrs={'class': 'form-input'}),
            'last_name':      forms.TextInput(attrs={'class': 'form-input'}),
            'email':          forms.EmailInput(attrs={'class': 'form-input'}),
            'empresa':        forms.TextInput(attrs={'class': 'form-input'}),
            'telefone':       forms.TextInput(attrs={'class': 'form-input'}),
            'plano':          forms.Select(attrs={'class': 'form-input'}),
            'data_expiracao': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'ativo':          forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'observacoes':    forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        nova = self.cleaned_data.get('nova_senha')
        if nova:
            user.set_password(nova)
        if commit:
            user.save()
        return user
