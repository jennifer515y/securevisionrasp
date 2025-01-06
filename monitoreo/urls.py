from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import actualizar_ubicacion

urlpatterns = [
    path('', views.index, name='index'),
    path('iniciar-sesion/', views.Iniciar, name='Iniciar'),#Página de Iniciar
    path('cerrar_sesion/', views.CerrarSesion, name='CerrarSesion'),
    path('registro-empresa/', views.RegistroEmpresa, name='RegistroEmpresa'),#Página de RegistroEmpresa
    path('registro-empleado/', views.RegistroEmpleado, name='RegistroEmpleado'),#Página de RegistroEmpleado
    path('registro-exitoso/', views.RegistroExitoso, name='RegistroExitoso'),#Página de RegistroExitoso
    path('bienvenido/empleado/', views.BienvenidoEmpleado, name='BienvenidoEmpleado'),#Página de BienvenidoEmpleado
    path('bienvenido/empresa/', views.BienvenidoEmpresa, name='BienvenidoEmpresa'),#Página de BienvenidoEmpresa
    path('perfilEmpleado/', views.PerfilEmpleado, name='PerfilEmpleado'),#Página de perfil
    path('perfilEmpresa/', views.PerfilEmpresa, name='PerfilEmpresa'),#Página de perfilempresa
    path('Lista/empleados/', views.ListaEmpleados, name='ListaEmpleados'),
    path('empleado/<int:empleado_id>/', views.DetalleEmpleado, name='DetalleEmpleado'),
    path('soporte_usuarios/', views.SoporteUsuarios, name='SoporteUsuarios'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='monitoreo/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='monitoreo/reset_password_confirm.html'), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(template_name='monitoreo/password_reset_complete.html'), name='password_reset_complete'),
    path('monitoreo/<int:empleado_id>/', views.monitoreo, name='monitoreo'),
    path('video_feed/<int:empleado_id>/', views.video_feed, name='video_feed'),
    path('detener_alarma', views.detener_alarma, name='detener_alarma'),
    path('detener_monitoreo/', views.detener_monitoreo, name='detener_monitoreo'),
    path('estado_alerta/<int:empleado_id>/', views.estado_alerta, name='estado_alerta'),
    path('empleado/<int:empleado_id>/cambiar_alarma/', views.cambiar_alarma, name='cambiar_alarma'),
    path('actualizar-ubicacion/', views.actualizar_ubicacion, name='actualizar_ubicacion'),
]