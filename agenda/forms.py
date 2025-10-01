from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Servico, Agendamento, Disponibilidade, Barbearia

# ------------------------------
# Registro de Clientes
# ------------------------------
class RegistroClienteForm(UserCreationForm):
    """
    Formulário para registrar clientes.
    Inclui campo telefone obrigatório.
    """
    telefone = forms.CharField(
        max_length=20,
        required=True,
        label="Telefone",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "(XX) XXXXX-XXXX"})
    )

    class Meta:
        model = Usuario
        fields = ("username", "email", "telefone", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Digite seu usuário"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Digite seu email"}),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo = "cliente"
        usuario.telefone = self.cleaned_data["telefone"]
        if commit:
            usuario.save()
        return usuario


# ------------------------------
# Registro de Barbeiro
# ------------------------------
class RegistroBarbeiroForm(UserCreationForm):
    """
    Formulário para registrar barbeiros.
    Só pode criar barbeiros para a barbearia do admin logado.
    """
    class Meta:
        model = Usuario
        fields = [
            "username", "email", "password1", "password2",
            "apelido", "telefone", "cpf", "rg", "sexo", "data_nascimento",
            "estado", "cidade", "bairro", "rua", "cep", "numero", "complemento",
            "observacao", "foto", "comissao"
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
            "cpf": forms.TextInput(attrs={"class": "form-control"}),
            "rg": forms.TextInput(attrs={"class": "form-control"}),
            "sexo": forms.Select(attrs={"class": "form-control"}),
            "data_nascimento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "estado": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.TextInput(attrs={"class": "form-control"}),
            "bairro": forms.TextInput(attrs={"class": "form-control"}),
            "rua": forms.TextInput(attrs={"class": "form-control"}),
            "cep": forms.TextInput(attrs={"class": "form-control"}),
            "numero": forms.TextInput(attrs={"class": "form-control"}),
            "complemento": forms.TextInput(attrs={"class": "form-control"}),
            "observacao": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "comissao": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        # Recebe a barbearia do admin logado
        self.barbearia = kwargs.pop("barbearia", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo = "barbeiro"
        usuario.barbearia = self.barbearia  # associa barbeiro à barbearia do admin
        if commit:
            usuario.save()
        return usuario


# ------------------------------
# Registro Admin Barbearia
# ------------------------------
class RegistroAdminBarbeariaForm(UserCreationForm):
    """
    Formulário para registrar o administrador principal de uma nova barbearia.
    Inclui nome e logo da barbearia.
    """
    nome_barbearia = forms.CharField(
        max_length=150,
        label="Nome da Barbearia",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome da nova barbearia"})
    )
    logo = forms.ImageField(
        required=False,
        label="Logotipo da Barbearia",
        widget=forms.FileInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Usuario
        fields = ("username", "email", "password1", "password2", "nome_barbearia", "logo")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Digite seu usuário"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Digite seu email"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo = "admin_barbearia"
        if commit:
            usuario.save()
            barbearia = Barbearia.objects.create(
                nome=self.cleaned_data["nome_barbearia"],
                logo=self.cleaned_data.get("logo")
            )
            usuario.barbearia = barbearia
            usuario.save()
        return usuario


# ------------------------------
# Formulário Barbearia
# ------------------------------
class BarbeariaForm(forms.ModelForm):
    class Meta:
        model = Barbearia
        fields = ['nome', 'endereco', 'telefone', 'descricao', 'logo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome da barbearia'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua, número, bairro, cidade'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXX-XXXX'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Breve descrição da barbearia', 'rows': 3}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


# ------------------------------
# Serviços
# ------------------------------
class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ["nome", "preco", "duracao"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "preco": forms.NumberInput(attrs={"class": "form-control"}),
            "duracao": forms.TextInput(attrs={"class": "form-control", "placeholder": "HH:MM:SS"}),
        }


# ------------------------------
# Disponibilidade
# ------------------------------
class DisponibilidadeForm(forms.ModelForm):
    class Meta:
        model = Disponibilidade
        fields = ["dia", "hora_inicio", "hora_fim"]
        widgets = {
            "dia": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hora_inicio": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "hora_fim": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
        }


# ------------------------------
# Agendamento
# ------------------------------
class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ["barbeiro", "servico", "data"]
        widgets = {
            "barbeiro": forms.Select(attrs={"class": "form-control"}),
            "servico": forms.Select(attrs={"class": "form-control"}),
            "data": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        barbearia_id = kwargs.pop("barbearia_id", None)
        super().__init__(*args, **kwargs)

        # Filtrar barbeiros pela barbearia
        queryset_barbeiros = Usuario.objects.filter(tipo="barbeiro")
        if barbearia_id:
            queryset_barbeiros = queryset_barbeiros.filter(barbearia_id=barbearia_id)
        self.fields["barbeiro"].queryset = queryset_barbeiros

        # Filtrar serviços pelo barbeiro selecionado
        if "barbeiro" in self.data:
            try:
                barbeiro_id = int(self.data.get("barbeiro"))
                self.fields["servico"].queryset = Servico.objects.filter(barbeiro_id=barbeiro_id)
            except (ValueError, TypeError):
                self.fields["servico"].queryset = Servico.objects.none()
        elif self.instance.pk and self.instance.barbeiro:
            self.fields["servico"].queryset = self.instance.barbeiro.servicos.all()
        else:
            self.fields["servico"].queryset = Servico.objects.none()
