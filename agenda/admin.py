from django.contrib import admin
from .models import Usuario, Agendamento, Servico, Disponibilidade, Barbearia

# ------------------------------
# Barbearia
# ------------------------------
@admin.register(Barbearia)
class BarbeariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco', 'telefone', 'criado_em')
    search_fields = ('nome', 'endereco', 'telefone')
    ordering = ('nome',)


# ------------------------------
# Usuário
# ------------------------------
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'tipo', 'barbearia')  # Mostra a barbearia
    list_filter = ('tipo', 'barbearia')                        # Filtros por tipo e barbearia
    search_fields = ('username', 'email', 'barbearia__nome')   # Busca por usuário e barbearia
    ordering = ('username',)


# ------------------------------
# Serviços
# ------------------------------
@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'barbeiro', 'barbearia', 'preco', 'duracao')  # Exibe a barbearia
    list_filter = ('barbeiro', 'barbearia')                               # Filtros por barbeiro e barbearia
    search_fields = ('nome', 'barbeiro__username', 'barbearia__nome')     # Busca por serviço, barbeiro e barbearia
    ordering = ('nome',)


# ------------------------------
# Agendamentos
# ------------------------------
@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'barbeiro', 'barbearia', 'servico', 'data', 'status')
    list_filter = ('barbeiro', 'barbearia', 'status', 'data')
    search_fields = ('cliente__username', 'barbeiro__username', 'servico__nome', 'barbearia__nome')
    ordering = ('-data',)


# ------------------------------
# Disponibilidade
# ------------------------------
@admin.register(Disponibilidade)
class DisponibilidadeAdmin(admin.ModelAdmin):
    list_display = ('barbeiro', 'barbeiro_barbearia', 'dia', 'hora_inicio', 'hora_fim')
    list_filter = ('barbeiro', 'barbeiro__barbearia', 'dia')
    search_fields = ('barbeiro__username', 'barbeiro__barbearia__nome')
    ordering = ('-dia',)

    def barbeiro_barbearia(self, obj):
        return obj.barbeiro.barbearia
    barbeiro_barbearia.short_description = 'Barbearia'
