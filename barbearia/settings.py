from pathlib import Path

# -----------------------
# Caminho base do projeto
# -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------
# Segurança
# -----------------------
SECRET_KEY = 'troque-essa-chave-por-uma-secreta-muito-forte'  # Substitua por uma chave real
DEBUG = False
ALLOWED_HOSTS = ['barbeiro-3wft.onrender.com']  # URL do seu serviço no Render

# -----------------------
# Aplicativos instalados
# -----------------------
INSTALLED_APPS = [
    # Apps padrão do Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # App do sistema de agendamento
    'agenda',
]

# -----------------------
# Middleware
# -----------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -----------------------
# Configuração de URLs
# -----------------------
ROOT_URLCONF = 'barbearia.urls'

# -----------------------
# Templates
# -----------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', 
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# -----------------------
# WSGI
# -----------------------
WSGI_APPLICATION = 'barbearia.wsgi.application'

# -----------------------
# Banco de dados
# -----------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -----------------------
# Validação de senhas
# -----------------------
AUTH_PASSWORD_VALIDATORS = [
    # Ative em produção para maior segurança
    # {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    # {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    # {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    # {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------
# Internacionalização
# -----------------------
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# -----------------------
# Arquivos estáticos
# -----------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # Coleta para produção

# -----------------------
# Arquivos de mídia
# -----------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -----------------------
# Tipo padrão para campos AutoField
# -----------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------
# Usuário customizado
# -----------------------
AUTH_USER_MODEL = "agenda.Usuario"

# -----------------------
# URLs de login/logout
# -----------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/agenda/'
LOGOUT_REDIRECT_URL = '/'

# -----------------------
# Email backend (desenvolvimento)
# -----------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
