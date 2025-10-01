from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta

# ------------------ BARBEARIA ------------------
class Barbearia(models.Model):
    nome = models.CharField("Nome da Barbearia", max_length=150)
    descricao = models.TextField("Descrição", blank=True, null=True)
    endereco = models.CharField("Endereço", max_length=255, blank=True, null=True)
    telefone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    logo = models.ImageField("Logotipo", upload_to='logos/', blank=True, null=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Barbearia"
        verbose_name_plural = "Barbearias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# ------------------ USUÁRIO ------------------
class Usuario(AbstractUser):
    TIPO_CHOICES = (
        ("cliente", "Cliente"),
        ("barbeiro", "Barbeiro"),
        ("admin_barbearia", "Administrador da Barbearia"),
        ("superadmin", "Super Administrador"),
    )

    tipo = models.CharField("Tipo de Usuário", max_length=20, choices=TIPO_CHOICES, default="cliente")
    barbearia = models.ForeignKey(
        Barbearia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
        verbose_name="Barbearia"
    )

    # Dados pessoais
    apelido = models.CharField("Apelido", max_length=50, blank=True, null=True)
    telefone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    cpf = models.CharField("CPF", max_length=14, blank=True, null=True)
    rg = models.CharField("RG", max_length=20, blank=True, null=True)
    sexo = models.CharField(
        "Sexo",
        max_length=10,
        choices=(('M', 'Masculino'), ('F', 'Feminino')),
        blank=True,
        null=True
    )
    data_nascimento = models.DateField("Data de Nascimento", blank=True, null=True)

    # Endereço
    estado = models.CharField("Estado", max_length=50, blank=True, null=True)
    cidade = models.CharField("Cidade", max_length=50, blank=True, null=True)
    bairro = models.CharField("Bairro", max_length=50, blank=True, null=True)
    rua = models.CharField("Rua", max_length=100, blank=True, null=True)
    cep = models.CharField("CEP", max_length=10, blank=True, null=True)
    numero = models.CharField("Número", max_length=10, blank=True, null=True)
    complemento = models.CharField("Complemento", max_length=50, blank=True, null=True)
    observacao = models.TextField("Observação", blank=True, null=True)
    foto = models.ImageField("Foto", upload_to='fotos_barbeiro/', blank=True, null=True)

    # Comissão do barbeiro
    comissao = models.DecimalField("Comissão (%)", max_digits=5, decimal_places=2, default=0.0)

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["username"]

    def __str__(self):
        return f"{self.username} ({self.get_tipo_display()})"


# ------------------ SERVIÇOS ------------------
class Servico(models.Model):
    barbearia = models.ForeignKey(
        Barbearia,
        on_delete=models.CASCADE,
        related_name="servicos",
        verbose_name="Barbearia"
    )
    barbeiro = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="servicos",
        verbose_name="Barbeiro"
    )
    nome = models.CharField("Nome do Serviço", max_length=100)
    preco = models.DecimalField("Preço (R$)", max_digits=8, decimal_places=2)
    duracao = models.DurationField("Duração", help_text="Informe no formato HH:MM:SS")

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} - {self.barbeiro.username} ({self.barbearia.nome})"


# ------------------ AGENDAMENTO ------------------
class Agendamento(models.Model):
    STATUS_CHOICES = (
        ("ativo", "Ativo"),
        ("cancelado", "Cancelado"),
    )

    barbearia = models.ForeignKey(
        Barbearia,
        on_delete=models.CASCADE,
        related_name="agendamentos",
        verbose_name="Barbearia"
    )
    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="agendamentos_cliente",
        verbose_name="Cliente"
    )
    barbeiro = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="agendamentos_barbeiro",
        verbose_name="Barbeiro"
    )
    servico = models.ForeignKey(
        Servico,
        on_delete=models.SET_NULL,
        null=True,
        related_name="agendamentos",
        verbose_name="Serviço"
    )
    data = models.DateTimeField("Data e Hora")
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="ativo")
    mensagem_cancelamento = models.TextField("Mensagem de Cancelamento", blank=True, null=True)

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ["-data"]

    def __str__(self):
        servico_nome = self.servico.nome if self.servico else "Serviço"
        return f"{servico_nome} - {self.cliente.username} com {self.barbeiro.username} ({self.barbearia.nome}) em {self.data.strftime('%d/%m/%Y %H:%M')}"

    @property
    def horario_fim(self):
        if self.servico and self.servico.duracao:
            return self.data + self.servico.duracao
        return self.data + timedelta(minutes=30)


# ------------------ DISPONIBILIDADE ------------------
class Disponibilidade(models.Model):
    barbeiro = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="disponibilidades",
        verbose_name="Barbeiro"
    )
    dia = models.DateField("Dia")
    hora_inicio = models.TimeField("Início")
    hora_fim = models.TimeField("Fim")

    class Meta:
        verbose_name = "Disponibilidade"
        verbose_name_plural = "Disponibilidades"
        ordering = ["dia", "hora_inicio"]

    def __str__(self):
        return f"{self.barbeiro.username} - {self.dia.strftime('%d/%m/%Y')} {self.hora_inicio.strftime('%H:%M')} às {self.hora_fim.strftime('%H:%M')}"


# ------------------ NOTIFICAÇÃO ------------------
class Notificacao(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="notificacoes",
        verbose_name="Usuário"
    )
    mensagem = models.TextField("Mensagem")
    lida = models.BooleanField("Lida", default=False)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.usuario.username} - {self.mensagem[:30]}..."
