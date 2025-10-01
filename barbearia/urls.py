# project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Painel administrativo do Django
    path("admin/", admin.site.urls),

    # URLs do app principal "agenda"
    path("", include(("agenda.urls", "agenda"), namespace="agenda")),

    # URLs para autenticação de usuários (descomente se for usar login/logout padrão do Django)
    # path("accounts/", include("django.contrib.auth.urls")),
]

# Servir arquivos de mídia (como logos) durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
