"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from  Login.views import LoginAPIView, LogoutAPIView
from django.conf import settings
from django.conf.urls.static import static
from integrations.almacenamiento_proxy import almacenamiento_proxy
from integrations.turnos_proxy import turnos_proxy_get, turnos_proxy_post, turnos_proxy_get_medico_fecha, turnos_proxy_reservar, turnos_proxy_get_turnos_paciente, turnos_proxy_cancelar
from integrations.almacenamiento_reserva_proxy import almacenamiento_reserva_proxy
from integrations.gametos_donacion_proxy import gametos_donacion_proxy

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('Paciente.urls')),
    path('api/', include('Ovocito.urls')),
    path('api/', include('Medicos.urls')),
    path('api/', include('Puncion.urls')),
    path('api/', include('Embrion.urls')),
    path('api/', include('PrimerConsulta.urls')),
    path('api/', include('Fertilizacion.urls')),
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/logout/', LogoutAPIView.as_view(), name='logout'),
    #path('api/', include('Turnos.urls')),
    path('api/almacenamiento/', almacenamiento_proxy),
    #path('api/turnos/', turnos_proxy),
    #path('turnos/consultar/', turnos_proxy_get, name='turnos_get_proxy'),
    path('api/turnos/consultar_medico_fecha/', turnos_proxy_get_medico_fecha, name='turnos_proxy_get_medico_fecha'),
    path('api/turnos/grilla/', turnos_proxy_post, name='turnos_post_proxy'),
    path('api/reservar_turno/', turnos_proxy_reservar, name='turnos_proxy_reservar'),
    path('api/donacion/', gametos_donacion_proxy),
    path('api/tanques/registrar/', almacenamiento_reserva_proxy),
    path('api/turnos/mis_turnos/', turnos_proxy_get_turnos_paciente, name='turnos_proxy_get_turnos_paciente'),
    path('api/turnos/cancelar_turno/', turnos_proxy_cancelar, name='turnos_proxy_cancelar'),
    path('api/monitoreo/', include('Monitoreo.urls')),
    path('api/segunda_consulta/', include('SegundaConsulta.urls')),
    path('api/chatbot/', include('Chatbot.urls')),
    path('api/tratamiento/', include('Tratamiento.urls')),
    path('api/transferencia/', include('Transferencia.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
