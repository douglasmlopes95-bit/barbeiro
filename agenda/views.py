from datetime import datetime, timedelta, date
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from .forms import RegistroClienteForm, RegistroBarbeiroForm, ServicoForm, BarbeariaForm
from .models import Agendamento, Usuario, Servico, Disponibilidade, Notificacao, Barbearia

# ------------------ HOME ------------------
def home(request):
    """Página inicial com lista de barbearias"""
    barbearias = Barbearia.objects.all()
    return render(request, "home.html", {"barbearias": barbearias})

def barbearia_detail(request, barbearia_id):
    """Detalhes da barbearia: barbeiros, serviços e horários disponíveis"""
    barbearia = get_object_or_404(Barbearia, id=barbearia_id)
    barbeiros = Usuario.objects.filter(barbearia=barbearia, tipo="barbeiro")
    servicos = Servico.objects.filter(barbearia=barbearia)

    hoje = date.today()
    disponibilidades = Disponibilidade.objects.filter(
        barbeiro__in=barbeiros, dia__gte=hoje
    ).order_by("dia", "hora_inicio")

    horarios_por_barbeiro = {b.id: disponibilidades.filter(barbeiro=b) for b in barbeiros}

    return render(
        request,
        "barbearia_detail.html",
        {
            "barbearia": barbearia,
            "barbeiros": barbeiros,
            "servicos": servicos,
            "disponibilidades": disponibilidades,
            "horarios_por_barbeiro": horarios_por_barbeiro,
        },
    )

# ------------------ CRIAR BARBEARIA ------------------
@login_required
def criar_barbearia(request):
    if request.method == "POST":
        form = BarbeariaForm(request.POST, request.FILES)
        if form.is_valid():
            barbearia = form.save()
            request.user.barbearia = barbearia
            request.user.save()
            return redirect("agenda:home")
    else:
        form = BarbeariaForm()
    return render(request, "criar_barbearia.html", {"form": form})

# ------------------ REGISTRO ------------------
def registro_cliente(request):
    if request.method == "POST":
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            if Usuario.objects.filter(username=username).exists():
                return render(
                    request,
                    "registro.html",
                    {"form": form, "tipo": "cliente", "error": "Este nome de usuário já está em uso."},
                )
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.tipo = "cliente"
            user.telefone = form.cleaned_data["telefone"]
            user.save()
            login(request, user)
            return redirect("agenda:agenda_cliente")
    else:
        form = RegistroClienteForm()
    return render(request, "registro.html", {"form": form, "tipo": "cliente"})

def registro_barbeiro(request):
    if request.method == "POST":
        form = RegistroBarbeiroForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data["username"]
            if Usuario.objects.filter(username=username).exists():
                return render(
                    request,
                    "registro.html",
                    {"form": form, "tipo": "barbeiro", "error": "Este nome de usuário já está em uso."},
                )
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.tipo = "barbeiro"
            if request.user.tipo == "admin_barbearia":
                user.barbearia = request.user.barbearia
            user.save()
            login(request, user)
            return redirect("agenda:dashboard_barbeiro")
    else:
        form = RegistroBarbeiroForm()
    return render(request, "registro.html", {"form": form, "tipo": "barbeiro"})

# ------------------ LOGIN ------------------
def login_cliente(request):
    if request.method == "POST":
        username = request.POST.get("username")
        senha = request.POST.get("password")
        user = authenticate(request, username=username, password=senha)
        if user:
            login(request, user)
            if user.tipo == "cliente":
                return redirect("agenda:agenda_cliente")
            elif user.tipo == "barbeiro":
                return redirect("agenda:dashboard_barbeiro")
            elif user.tipo == "admin_barbearia":
                return redirect("agenda:dashboard_admin")
            return redirect("/admin/")
        return render(request, "login.html", {"error": "Usuário ou senha incorretos."})
    return render(request, "login.html")

# ------------------ CLIENTE ------------------
@login_required
def agenda_cliente(request):
    if request.user.tipo != "cliente":
        return redirect("agenda:home")

    barbearia_id = request.GET.get("barbearia")
    if barbearia_id:
        barbearia = get_object_or_404(Barbearia, id=barbearia_id)
        barbeiros = Usuario.objects.filter(barbearia=barbearia, tipo="barbeiro")
        servicos = Servico.objects.filter(barbearia=barbearia)
    else:
        barbearia = None
        barbeiros = Usuario.objects.filter(tipo="barbeiro")
        servicos = Servico.objects.all()

    agendamentos = Agendamento.objects.filter(cliente=request.user).order_by("data")

    if request.method == "POST":
        barbeiro_id = request.POST.get("barbeiro")
        servico_id = request.POST.get("servico")
        data = request.POST.get("data")
        hora = request.POST.get("hora")

        if not all([barbeiro_id, servico_id, data, hora]):
            return render(
                request,
                "agenda_cliente.html",
                {
                    "agendamentos": agendamentos,
                    "barbeiros": barbeiros,
                    "servicos": servicos,
                    "barbearia": barbearia,
                    "error": "Preencha todos os campos."
                },
            )

        barbeiro = get_object_or_404(Usuario, id=barbeiro_id)
        servico = get_object_or_404(Servico, id=servico_id)
        data_hora = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")

        disponivel = Disponibilidade.objects.filter(
            barbeiro=barbeiro,
            dia=data_hora.date(),
            hora_inicio__lte=data_hora.time(),
            hora_fim__gte=(datetime.combine(data_hora.date(), data_hora.time()) + servico.duracao).time(),
        ).exists()

        conflito = Agendamento.objects.filter(
            barbeiro=barbeiro,
            status="ativo",
            data__lt=data_hora + servico.duracao,
            data__gte=data_hora,
        ).exists()

        if disponivel and not conflito:
            Agendamento.objects.create(
                cliente=request.user,
                barbeiro=barbeiro,
                barbearia=barbeiro.barbearia,
                servico=servico,
                data=data_hora,
                status="ativo",
            )
            return redirect("agenda:agenda_cliente")
        else:
            msg = "Horário não disponível." if not disponivel else "Esse horário já foi reservado."
            return render(
                request,
                "agenda_cliente.html",
                {
                    "agendamentos": agendamentos,
                    "barbeiros": barbeiros,
                    "servicos": servicos,
                    "barbearia": barbearia,
                    "error": msg
                },
            )

    return render(
        request,
        "agenda_cliente.html",
        {
            "agendamentos": agendamentos,
            "barbeiros": barbeiros,
            "servicos": servicos,
            "barbearia": barbearia,
        },
    )

# ------------------ BARBEIRO ------------------
@login_required
def dashboard_barbeiro(request):
    if request.user.tipo != "barbeiro":
        return redirect("agenda:home")

    agendamentos = Agendamento.objects.filter(barbeiro=request.user).order_by("data")
    total_agendamentos = agendamentos.filter(status="ativo").count()
    total_clientes = agendamentos.filter(status="ativo").values("cliente").distinct().count()
    ticket_medio = agendamentos.filter(status="ativo").aggregate(avg=Avg("servico__preco"))["avg"] or 0

    stats = []
    for i in range(7):
        dia = now().date() - timedelta(days=i)
        dia_agendamentos = agendamentos.filter(data__date=dia, status="ativo")
        stats.append({
            "data": dia.strftime("%d/%m"),
            "total": dia_agendamentos.count(),
            "faturamento": dia_agendamentos.aggregate(total=Sum("servico__preco"))["total"] or 0
        })
    stats.reverse()

    servicos = Servico.objects.filter(barbeiro=request.user)
    form = ServicoForm()

    if request.method == "POST":
        form = ServicoForm(request.POST)
        if form.is_valid():
            novo_servico = form.save(commit=False)
            novo_servico.barbeiro = request.user
            novo_servico.barbearia = request.user.barbearia
            novo_servico.save()
            return redirect("agenda:dashboard_barbeiro")

    return render(
        request,
        "dashboard_barbeiro.html",
        {
            "agendamentos": agendamentos,
            "total_agendamentos": total_agendamentos,
            "total_clientes": total_clientes,
            "ticket_medio": ticket_medio,
            "stats": stats,
            "servicos": servicos,
            "form": form
        },
    )

# ------------------ SERVIÇOS ------------------
@login_required
def adicionar_servico(request):
    if request.user.tipo != "barbeiro":
        return redirect("agenda:home")
    form = ServicoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        novo_servico = form.save(commit=False)
        novo_servico.barbeiro = request.user
        novo_servico.barbearia = request.user.barbearia
        novo_servico.save()
        return redirect("agenda:dashboard_barbeiro")
    return render(request, "form_servico.html", {"form": form, "titulo": "Adicionar Serviço"})

@login_required
def editar_servico(request, id):
    if request.user.tipo != "barbeiro":
        return redirect("agenda:home")
    servico = get_object_or_404(Servico, id=id, barbeiro=request.user)
    form = ServicoForm(request.POST or None, instance=servico)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("agenda:dashboard_barbeiro")
    return render(request, "form_servico.html", {"form": form, "titulo": "Editar Serviço"})

@login_required
def remover_servico(request, id):
    if request.user.tipo != "barbeiro":
        return redirect("agenda:home")
    servico = get_object_or_404(Servico, id=id, barbeiro=request.user)
    if request.method == "POST":
        servico.delete()
        return redirect("agenda:dashboard_barbeiro")
    return render(request, "remover_servico.html", {"servico": servico})

# ------------------ DISPONIBILIDADE ------------------
@login_required
def gerenciar_disponibilidade(request):
    if request.user.tipo != "barbeiro":
        return redirect("agenda:home")

    if request.method == "POST":
        dia = request.POST.get("dia")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fim = request.POST.get("hora_fim")
        if all([dia, hora_inicio, hora_fim]):
            Disponibilidade.objects.create(barbeiro=request.user, dia=dia, hora_inicio=hora_inicio, hora_fim=hora_fim)
        return redirect("agenda:gerenciar_disponibilidade")

    disponibilidades = Disponibilidade.objects.filter(barbeiro=request.user).order_by("dia", "hora_inicio")
    return render(request, "disponibilidade_barbeiro.html", {"disponibilidades": disponibilidades})

@login_required
def remover_disponibilidade(request, id):
    if request.user.tipo != "barbeiro":
        return redirect("agenda:home")
    disponibilidade = get_object_or_404(Disponibilidade, id=id, barbeiro=request.user)
    disponibilidade.delete()
    return redirect("agenda:gerenciar_disponibilidade")

# ------------------ CANCELAR AGENDAMENTO ------------------
@login_required
def cancelar_agendamento(request, id):
    agendamento = get_object_or_404(Agendamento, id=id)
    if request.user not in [agendamento.cliente, agendamento.barbeiro]:
        return HttpResponseForbidden("Você não tem permissão para cancelar este agendamento.")

    if request.method == "POST":
        destinatario = agendamento.barbeiro if request.user == agendamento.cliente else agendamento.cliente
        agendamento.status = "cancelado"
        agendamento.mensagem_cancelamento = f"O agendamento de {agendamento.data.strftime('%d/%m %H:%M')} foi cancelado por {request.user.username}."
        agendamento.save()
        Notificacao.objects.create(usuario=destinatario, mensagem=agendamento.mensagem_cancelamento)
        return redirect("agenda:agenda_cliente" if request.user.tipo == "cliente" else "agenda:dashboard_barbeiro")

    return render(request, "cancelar_agendamento.html", {"agendamento": agendamento})

# ------------------ API: HORÁRIOS DISPONÍVEIS ------------------
@login_required
def horarios_disponiveis(request):
    barbeiro_id = request.GET.get("barbeiro")
    dia_str = request.GET.get("dia")
    servico_id = request.GET.get("servico")
    if not barbeiro_id or not dia_str or not servico_id:
        return JsonResponse({"horarios": []})

    barbeiro = get_object_or_404(Usuario, id=barbeiro_id)
    servico = get_object_or_404(Servico, id=servico_id)
    duracao = servico.duracao
    dia = datetime.strptime(dia_str, "%Y-%m-%d").date()

    disponibilidades = Disponibilidade.objects.filter(barbeiro=barbeiro, dia=dia)
    horarios_livres = []

    for d in disponibilidades:
        hora_atual = datetime.combine(d.dia, d.hora_inicio)
        hora_fim = datetime.combine(d.dia, d.hora_fim) - duracao
        while hora_atual <= hora_fim:
            conflito = Agendamento.objects.filter(
                barbeiro=barbeiro,
                status="ativo",
                data__lt=hora_atual + duracao,
                data__gte=hora_atual,
            ).exists()
            if not conflito:
                horarios_livres.append(hora_atual.strftime("%H:%M"))
            hora_atual += timedelta(minutes=30)

    return JsonResponse({"horarios": horarios_livres})

# ------------------ NOTIFICAÇÕES ------------------
@login_required
def lista_notificacoes(request):
    notificacoes = Notificacao.objects.filter(usuario=request.user, lida=False)
    data = [{"id": n.id, "mensagem": n.mensagem} for n in notificacoes]
    return JsonResponse({"notificacoes": data})

@login_required
def marcar_notificacao_lida(request, id):
    notif = get_object_or_404(Notificacao, id=id, usuario=request.user)
    notif.lida = True
    notif.save()
    return JsonResponse({"status": "ok"})

# ------------------ DASHBOARD ADMIN ------------------
@login_required
def dashboard_admin(request):
    if request.user.tipo not in ["admin_barbearia", "superadmin"]:
        return redirect("agenda:home")

    barbearia = request.user.barbearia
    if not barbearia:
        return redirect("agenda:home")

    agendamentos = Agendamento.objects.filter(barbearia=barbearia).order_by("data")
    barbeiros = Usuario.objects.filter(barbearia=barbearia, tipo="barbeiro")
    servicos = Servico.objects.filter(barbearia=barbearia)
    disponibilidades = Disponibilidade.objects.filter(barbeiro__in=barbeiros).order_by("dia", "hora_inicio")

    clientes_ids = set(ag.cliente.id for ag in agendamentos)
    total_clientes = len(clientes_ids)

    form_servico = ServicoForm()

    if request.method == "POST":
        if "add_servico" in request.POST:
            form_servico = ServicoForm(request.POST)
            if form_servico.is_valid():
                novo_servico = form_servico.save(commit=False)
                if barbeiros.exists():
                    novo_servico.barbeiro = barbeiros.first()
                novo_servico.barbearia = barbearia
                novo_servico.save()
                return redirect("agenda:dashboard_admin")
        elif "update_logo" in request.POST:
            logo = request.FILES.get("logo")
            if logo:
                barbearia.logo = logo
                barbearia.save()
            return redirect("agenda:dashboard_admin")

    return render(
        request,
        "dashboard_admin.html",
        {
            "barbearia": barbearia,
            "agendamentos": agendamentos,
            "barbeiros": barbeiros,
            "servicos": servicos,
            "disponibilidades": disponibilidades,
            "form_servico": form_servico,
            "total_clientes": total_clientes
        },
    )

# ------------------ ADICIONAR BARBEIRO (ADMIN) ------------------
@login_required
def adicionar_barbeiro(request, barbearia_id=None):
    if request.user.tipo not in ["admin_barbearia", "superadmin"]:
        return redirect("agenda:home")

    barbearia = get_object_or_404(Barbearia, id=barbearia_id) if barbearia_id else request.user.barbearia

    if request.method == "POST":
        form = RegistroBarbeiroForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.tipo = "barbeiro"
            user.barbearia = barbearia
            user.save()
            return redirect("agenda:dashboard_admin")
    else:
        form = RegistroBarbeiroForm()

    return render(request, "adicionar_barbeiro.html", {"form": form, "barbearia": barbearia})

# ------------------ REMOVER BARBEIRO (ADMIN) ------------------
@login_required
def remover_barbeiro(request, id):
    if request.user.tipo not in ["admin_barbearia", "superadmin"]:
        return redirect("agenda:home")

    barbeiro = get_object_or_404(Usuario, id=id, tipo="barbeiro", barbearia=request.user.barbearia)
    if request.method == "POST":
        barbeiro.delete()
        return redirect("agenda:dashboard_admin")

    return render(request, "remover_barbeiro.html", {"barbeiro": barbeiro})

# ------------------ DASHBOARD SUPERADMIN ------------------
@login_required
def dashboard_superadmin(request):
    if request.user.tipo != "superadmin":
        return redirect("agenda:home")

    barbearias = Barbearia.objects.all()
    agendamentos = Agendamento.objects.all().order_by("data")
    clientes = Usuario.objects.filter(tipo="cliente")
    barbeiros = Usuario.objects.filter(tipo="barbeiro")

    filtro = request.GET.get("filtro", "total")
    hoje = now().date()
    if filtro == "dia":
        agendamentos = agendamentos.filter(data__date=hoje)
    elif filtro == "mes":
        agendamentos = agendamentos.filter(data__month=hoje.month, data__year=hoje.year)

    faturamento_barbearias = []
    for b in barbearias:
        total = agendamentos.filter(barbearia=b).aggregate(total=Sum("servico__preco"))["total"] or 0
        faturamento_barbearias.append({"barbearia": b, "total": total})
    top5 = sorted(faturamento_barbearias, key=lambda x: x["total"], reverse=True)[:5]

    grafico_faturamento = []
    grafico_clientes = []
    for b in barbearias:
        total = agendamentos.filter(barbearia=b).aggregate(total=Sum("servico__preco"))["total"] or 0
        qtd_clientes = agendamentos.filter(barbearia=b).values("cliente").distinct().count()
        grafico_faturamento.append({"barbearia": b.nome, "total": total})
        grafico_clientes.append({"barbearia": b.nome, "clientes": qtd_clientes})

    return render(
        request,
        "dashboard_superadmin.html",
        {
            "barbearias": barbearias,
            "agendamentos": agendamentos,
            "clientes": clientes,
            "barbeiros": barbeiros,
            "top5": top5,
            "grafico_faturamento": grafico_faturamento,
            "grafico_clientes": grafico_clientes,
            "filtro": filtro
        },
    )
