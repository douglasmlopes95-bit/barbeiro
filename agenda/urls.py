# agenda/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "agenda"  # Namespace para usar no {% url %} e redirect

urlpatterns = [
    # ------------------ PÁGINA INICIAL ------------------
    path("", views.home, name="home"),
    path("barbearia/<int:barbearia_id>/", views.barbearia_detail, name="barbearia_detail"),

    # ------------------ REGISTRO DE USUÁRIOS ------------------
    path("registro/cliente/", views.registro_cliente, name="registro_cliente"),
    path("registro/barbeiro/", views.registro_barbeiro, name="registro_barbeiro"),
    path("barbearia/criar/", views.criar_barbearia, name="criar_barbearia"),

    # ------------------ LOGIN / LOGOUT ------------------
    path("login/", views.login_cliente, name="login_cliente"),
    path("logout/", LogoutView.as_view(next_page="agenda:home"), name="logout"),

    # ------------------ ÁREAS ESPECÍFICAS ------------------
    path("agenda/", views.agenda_cliente, name="agenda_cliente"),
    path("dashboard/barbeiro/", views.dashboard_barbeiro, name="dashboard_barbeiro"),
    path("dashboard/admin/", views.dashboard_admin, name="dashboard_admin"),
    path("dashboard/super_admin/", views.dashboard_superadmin, name="dashboard_super_admin"),  # Corrigido

    # ------------------ DISPONIBILIDADE DO BARBEIRO ------------------
    path("disponibilidade/", views.gerenciar_disponibilidade, name="gerenciar_disponibilidade"),
    path("disponibilidade/remover/<int:id>/", views.remover_disponibilidade, name="remover_disponibilidade"),

    # ------------------ CRUD DE SERVIÇOS ------------------
    path("servicos/adicionar/", views.adicionar_servico, name="adicionar_servico"),
    path("servicos/editar/<int:id>/", views.editar_servico, name="editar_servico"),
    path("servicos/remover/<int:id>/", views.remover_servico, name="remover_servico"),

    # ------------------ BARBEIROS (ADMIN) ------------------
    path("barbeiro/adicionar/", views.adicionar_barbeiro, name="adicionar_barbeiro"),
    path("barbeiro/adicionar/<int:barbearia_id>/", views.adicionar_barbeiro, name="adicionar_barbeiro_barbearia"),
    path("barbeiro/remover/<int:id>/", views.remover_barbeiro, name="remover_barbeiro"),

    # ------------------ AGENDAMENTOS ------------------
    path("agendamento/cancelar/<int:id>/", views.cancelar_agendamento, name="cancelar_agendamento"),

    # ------------------ NOTIFICAÇÕES ------------------
    path("notificacoes/", views.lista_notificacoes, name="lista_notificacoes"),
    path("notificacoes/lida/<int:id>/", views.marcar_notificacao_lida, name="marcar_notificacao_lida"),

    # ------------------ API ------------------
    path("api/horarios_disponiveis/", views.horarios_disponiveis, name="horarios_disponiveis"),
]
