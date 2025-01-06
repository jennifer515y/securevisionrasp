from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from .models import Empleado, Empresa, Profile
from .models import Usuario
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db import IntegrityError
import cv2
import mediapipe as mp
import time
import pygame
from scipy.spatial import distance as dist
import threading
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.http import StreamingHttpResponse, JsonResponse
from .utils import gen_frames
from .forms import EmpleadoForm
from .forms import EmpresaForm
from django.contrib.auth import logout
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from monitoreo.models import Empleado
from . import models
from .models import Empleado, Alerta  # Ajusta según tus modelos
from django.db.models import Count
from monitoreo.models import Empleado
from django.shortcuts import render, get_object_or_404
from django.http import Http404
import json


            
# Define la vista para index
def index(request):
    return render(request, 'monitoreo/index.html')

#Define la vista para Iniciar
@csrf_protect
def Iniciar(request):
    if request.method == 'POST':
        print(request.POST) 
        correo = request.POST['correo']
        contrasena = request.POST['contrasena']

        #print(f"Correo recibido: {correo}")  # Depuración
        #print(f"Contraseña recibida: {contrasena}")  # Depuración


        usuario = authenticate(request, username=correo, password=contrasena)
        #print(f"Usuario encontrado: {usuario}")  # Depuración
            
        if usuario is not None:
            login(request, usuario)  # Inicia sesión al usuario

            # Verificar el tipo de usuario usando el perfil
            if usuario.profile.is_empresa:
                return redirect('BienvenidoEmpresa')  # Redirigir a la página de bienvenida para empresa
            elif usuario.profile.is_empleado:
                # Buscar el empleado por el correo del usuario autenticado
                empleado = Empleado.objects.get(CorreoEmpleado=request.user.email)
                empleado.Activo = True  # Marcar como activo
                empleado.save()  # Guardar cambios en la base de datos
                return redirect('BienvenidoEmpleado')  # Redirigir a la página de bienvenida para empleado
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return redirect('Iniciar')  # Volver al login si la autenticación falla

    return render(request, 'monitoreo/Iniciar.html')

#Soporte para usuarios
def SoporteUsuarios(request):
    return render(request, 'monitoreo/SoporteUsuarios.html')

#Cerrar sesión
def CerrarSesion(request):
    # Verificar si el usuario es un empleado
    if hasattr(request.user, 'profile') and request.user.profile.is_empleado:
        try:
            # Buscar el empleado por el correo del usuario autenticado
            empleado = Empleado.objects.get(CorreoEmpleado=request.user.email)
            empleado.Activo = False  # Marcar como inactivo
            empleado.save()  # Guardar cambios en la base de datos
        except Empleado.DoesNotExist:
            print("Empleado no encontrado, no se pudo marcar como inactivo.") 
    # Cerrar la sesión
    logout(request)
    
    # Redirigir al usuario a la página de inicio de sesión
    return redirect('Iniciar')  

#Define la vista para Registro_Empresa
@csrf_protect
def RegistroEmpresa(request):
    if request.method == "POST":
        nombre = request.POST.get('nombreEmpresa')
        titulo = request.POST.get('TituloEmpresa')
        rfc = request.POST.get('RFCEmpresa')
        numero = request.POST.get('NumeroEmpresa')
        correo = request.POST.get('CorreoEmpresa')
        contrasena = request.POST.get('ContrasenaEmpresa')

        try:
            # Intentar crear la empresa
            Empresa.objects.create(
                nombreEmpresa=nombre,
                RFCEmpresa=rfc,
                NumeroEmpresa=numero,
                CorreoEmpresa=correo,
                ContrasenaEmpresa=contrasena,
                TituloEmpresa = titulo,
            )
            print("Registro exitoso, redirigiendo...")
            
        # Crear el perfil de usuario asociado a la empresa
            user = User.objects.create_user(username=correo, password=contrasena, email=correo)
            user.first_name = titulo  # Usar el nombre de la empresa como nombre del usuario
            user.save()

            # Crear el perfil del usuario y marcarlo como empresa
            profile = Profile(user=user, is_empresa=True)
            profile.save()

            print("Perfil de empresa creado con éxito")
            return redirect('RegistroExitoso')  # Cambia esto al nombre de tu vista de éxito para empresas

        except IntegrityError:
            # Si hay un problema de unicidad (correo o RFC repetido)
            print("Error: RFC o correo ya registrado")
            return render(request, 'monitoreo/RegistroEmpresa.html', {
                'error': 'El RFC o correo ya está registrado.'
            })

        except Exception as e:
            # Manejo general de errores (debugging)
            print(f"Error inesperado: {str(e)}")
            return render(request, 'monitoreo/RegistroEmpresa.html', {
                'error': f'Error inesperado: {str(e)}'
            })

    print("Renderizando formulario vacío para registro de empresa")
    return render(request, 'monitoreo/RegistroEmpresa.html')

#Define la vista RegistroEmpleado
@csrf_protect
def RegistroEmpleado(request):
    if request.method == "POST":
        nombre = request.POST.get('NombreEmpleado')
        empresa_nombre = request.POST.get('EmpresaEmpleado')
        usuario = request.POST.get('UsuarioEmpleado')
        contrasena = request.POST.get('ContrasenaEmpleado')
        correo = request.POST.get('CorreoEmpleado')
        numero = request.POST.get('NumeroEmpleado')
        

        try:
            empresa = Empresa.objects.get(TituloEmpresa=empresa_nombre)

            # Crear el empleado
            Empleado.objects.create(
                NombreEmpleado=nombre,
                EmpresaEmpleado=empresa,
                UsuarioEmpleado=usuario,
                ContrasenaEmpleado=contrasena,
                CorreoEmpleado=correo,
                NumeroEmpleado=numero,
            )
            print("Registro exitoso, redirigiendo...")
            
            # Crear el perfil de usuario asociado al empleado
            user = User.objects.create_user(username=correo, password=contrasena, email=correo)
            user.first_name = nombre  # Usar el nombre del empleado como nombre del usuario
            user.save()

            # Crear el perfil del usuario y marcarlo como empleado
            profile = Profile(user=user, is_empleado=True, empresa=empresa.TituloEmpresa)
            profile.save()

            print("Perfil de empleado creado con éxito")
            # Redirigir al HTML de éxito
            return redirect('RegistroExitoso')
              
        
        except Empresa.DoesNotExist:
            # Si la empresa no existe, mostrar error en el formulario
            print("Error: Empresa no existe")
            return render(request, 'monitoreo/RegistroEmpleado.html', {
                'error': 'La empresa especificada no existe.'
            })
        
        except IntegrityError:
            # Si hay un problema de unicidad (correo o usuario repetido)
            print("Error: Correo o usuario ya registrado")
            return render(request, 'monitoreo/RegistroEmpleado.html', {
                'error': 'El correo o usuario ya está registrado.'
            })

        except Exception as e:
            # Manejo general de errores (debugging)
            print(f"Error inesperado: {str(e)}")
            return render(request, 'monitoreo/RegistroEmpleado.html', {
                'error': f'Error inesperado: {str(e)}'
            })
    print("Renderizando formulario vacío")
    return render(request, 'monitoreo/RegistroEmpleado.html')

#Función para regresar al index
def regresar_a_index(request):
    return redirect('index')

def RegistroExitoso(request):
    return render(request, 'monitoreo/RegistroExitoso.html')


#Define vista para BienvenidoEmpleado
@login_required
def BienvenidoEmpleado(request):
    if request.user.is_authenticated:
        # Verificar el correo electrónico del usuario autenticado
        print(f"Correo del usuario autenticado: {request.user.email}")

        try:
            # Buscar el empleado por el correo electrónico
            empleado = Empleado.objects.get(CorreoEmpleado=request.user.email)
            print(f"Empleado encontrado: {empleado}")
            empleado_id = empleado.id
        except Empleado.DoesNotExist:
            print("Empleado no encontrado.")
            empleado_id = None
    else:
        print("Usuario no autenticado.")
        empleado_id = None

    # Verificar qué valor se está pasando
    print(f"Empleado ID: {empleado_id}")

    return render(request, 'monitoreo/BienvenidoEmpleado.html', {'empleado_id': empleado_id})



#Define vista para BienvenidoEmpresa
@login_required
def BienvenidoEmpresa(request):
    return render(request, 'monitoreo/BienvenidoEmpresa.html')

#Vista PerfilEmpleado
@login_required
def PerfilEmpleado(request):
    # Obtenemos el perfil del empleado que está logueado
    empleado = Empleado.objects.get(CorreoEmpleado=request.user)

    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('PerfilEmpleado')  # Redirige después de guardar
    else:
        form = EmpleadoForm(instance=empleado)

    return render(request, 'monitoreo/PerfilEmpleado.html', {'form': form, 'empleado': empleado})

#Define la vista PerfilEmpresa
@login_required
def PerfilEmpresa(request):
    # Obtenemos el perfil del empleado que está logueado
    empresa = Empresa.objects.get(CorreoEmpresa=request.user)

    # Si se recibe una solicitud POST, significa que se quiere editar
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()  # Guardar los cambios
            return redirect('PerfilEmpresa')  # Redirigir al perfil después de guardar
    else:
        # Si es una solicitud GET, simplemente mostrar el formulario con los datos actuales
        form = EmpresaForm(instance=empresa)

    return render(request, 'monitoreo/PerfilEmpresa.html', {'form': form})

#Vista de empleados activos e inactivos
@login_required
def ListaEmpleados(request):
    if request.user.profile.is_empresa:
        try:
            empresa = Empresa.objects.get(CorreoEmpresa=request.user.email)

            # Obtén los empleados activos e inactivos
            empleados_activos = Empleado.objects.filter(EmpresaEmpleado=empresa, Activo=True)
            empleados_inactivos = Empleado.objects.filter(EmpresaEmpleado=empresa, Activo=False)

            # Agregar el estado de la alerta a cada empleado
            for empleado in empleados_activos:
                # Verifica si tiene alertas activas
                tiene_alerta = Alerta.objects.filter(empleado=empleado, activa=True).exists()
                empleado.tiene_alerta = tiene_alerta

            return render(request, 'monitoreo/ListaEmpleados.html', {
                'empleados_activos': empleados_activos,
                'empleados_inactivos': empleados_inactivos,
            })

        except (Empresa.DoesNotExist, Empleado.DoesNotExist):
            messages.error(request, 'No se encontraron empleados o empresa.')
            return redirect('BienvenidoEmpresa')

    else:
        messages.error(request, 'Acceso denegado.')
        return redirect('Iniciar')
    
#Alertas de somnolencia
def estado_alerta(request, empleado_id):
    try:
        # Verificar si hay alguna alerta registrada y activa para el empleado
        alerta_activa = Alerta.objects.filter(empleado__id=empleado_id, activa=True).exists()
        return JsonResponse({'alerta_activada': alerta_activa})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
#Cambiar a alarma atendida
def cambiar_alarma(request, empleado_id):
    try:
        # Buscar la alerta activa del empleado
        alerta = Alerta.objects.filter(empleado_id=empleado_id, activa=True).first()

        if alerta:
            if request.method == 'POST':
                # Cambiar el estado de la alarma a False (sin alarma)
                alerta.activa = False
                alerta.save()
                
                # Redirigir a la misma página de detalles del empleado
                return redirect('DetalleEmpleado', empleado_id=empleado_id)
            else:
                # Si la solicitud no es POST, simplemente redirigimos a detalles
                return redirect('DetalleEmpleado', empleado_id=empleado_id)

        else:
            raise Http404("No hay alerta activa para este empleado")

    except Alerta.DoesNotExist:
        raise Http404("Empleado o alerta no encontrada")
    
#Vista para la localización del empleado
@csrf_exempt
def actualizar_ubicacion(request):
    if request.method == 'POST':
        try:
            # Obtener los datos del cuerpo de la solicitud
            data = json.loads(request.body)
            empleado_id = data.get('empleado_id')
            latitud = data.get('latitud')
            longitud = data.get('longitud')

            # Imprimir para depuración
            #print(f"Empleado ID: {empleado_id}")
            #print(f"Latitud: {latitud}")
            #print(f"Longitud: {longitud}")

            # Validar que los datos no estén vacíos
            if not empleado_id or latitud is None or longitud is None:
                return JsonResponse({'success': False, 'message': 'Datos incompletos.'})

            # Verificar si el empleado existe en la base de datos
            try:
                empleado = Empleado.objects.get(id=empleado_id)
                empleado.Latitud = latitud
                empleado.Longitud = longitud
                empleado.save()

                return JsonResponse({'success': True, 'message': 'Ubicación actualizada correctamente.'})
            except Empleado.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Empleado no encontrado.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

#Define la vista para DetalleEmpleado
@login_required
def DetalleEmpleado(request, empleado_id):
    # Verificar si el usuario autenticado es una empresa
    if request.user.profile.is_empresa:
        try:
            # Obtener la empresa asociada
            empresa = Empresa.objects.get(CorreoEmpresa=request.user.email)

            # Obtener el empleado específico de esa empresa
            empleado = Empleado.objects.get(id=empleado_id, EmpresaEmpleado=empresa)

            # Verificar si tiene coordenadas
            if empleado.Latitud is None or empleado.Longitud is None:
                messages.warning(request, 'Este empleado no tiene ubicación registrada.')

            return render(request, 'monitoreo/DetalleEmpleado.html', {'empleado': empleado})
        except (Empresa.DoesNotExist, Empleado.DoesNotExist):
            messages.error(request, 'Empleado no encontrado.')
            return redirect('ListaEmpleados')
    else:
        messages.error(request, 'Acceso denegado.')
        return redirect('Iniciar')
    
#Recuperar contraseña
class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'monitoreo/password_reset_email.html'
    subject_template_name = 'monitoreo/password_reset_subject.txt'

    def form_valid(self, form):
        return super().form_valid(form)
    
#Guardar nueva contraseña en la BD
def reset_password_confirm(request, uidb64, token):
    try:
        # Decodificar el UID del empleado desde la URL
        uid = urlsafe_base64_decode(uidb64).decode()
        empleado = Empleado.objects.get(pk=uid)  # Cambia esto según el modelo del usuario
    except (TypeError, ValueError, OverflowError, Empleado.DoesNotExist):
        empleado = None

    # Verificar si el token es válido
    if empleado is not None and default_token_generator.check_token(empleado, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Validar contraseñas
            if new_password and confirm_password:
                if new_password == confirm_password:
                    # Guardar la nueva contraseña en el modelo
                    empleado.ContrasenaEmpleado = make_password(new_password)
                    empleado.save()
                    messages.success(request, "Contraseña actualizada exitosamente.")
                    return redirect('Iniciar')  # Redirige al login después de actualizar
                else:
                    messages.error(request, "Las contraseñas no coinciden.")
            else:
                messages.error(request, "Por favor, completa ambos campos.")
        
        # Si hay un error o es GET, renderiza nuevamente la página
        return render(request, 'monitoreo/reset_password_confirm.html', {
            'uidb64': uidb64,
            'token': token
        })
    else:
        messages.error(request, "El enlace para restablecer la contraseña no es válido o ha expirado.")
        return redirect('index')

def get_user_from_uidb64_and_token(uidb64, token):
    try:
        # Decodificar el UID
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        
        # Validar el token
        token_generator = PasswordResetTokenGenerator()
        if token_generator.check_token(user, token):
            return user
    except (User.DoesNotExist, ValueError, TypeError):
        return None


def send_reset_email(user):
    token_generator = PasswordResetTokenGenerator()
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    reset_link = f"http://tusitio.com/reset-password/{uidb64}/{token}/"
    # Código para enviar el correo con reset_link


# Define la vista para monitoreo
@login_required
def monitoreo(request, empleado_id):
    # Verificar si el usuario está autenticado
    if request.user.is_authenticated:
        # Verificar el correo electrónico del usuario autenticado
        print(f"Correo del usuario autenticado: {request.user.email}")

        try:
            # Buscar el empleado por el correo electrónico del usuario autenticado
            empleado = Empleado.objects.get(CorreoEmpleado=request.user.email)
            print(f"Empleado encontrado: {empleado}")
            empleado_id = empleado.id
        except Empleado.DoesNotExist:
            # Si el empleado no se encuentra, manejar el error
            print("Empleado no encontrado.")
            empleado_id = None
    else:
        # Si el usuario no está autenticado, asignar empleado_id a None
        print("Usuario no autenticado.")
        empleado_id = None

    # Verificar qué valor se está pasando para el empleado_id
    print(f"Empleado ID: {empleado_id}")

    # Verificar si el empleado_id es válido antes de continuar
    if empleado_id is None:
        return render(request, 'error.html', {'mensaje': 'Empleado no encontrado o no autenticado'})

    # Continuar con el resto del código, pasando empleado_id a la plantilla
    return render(request, 'monitoreo/monitoreo.html', {'empleado_id': empleado_id})

def video_feed(request, empleado_id):
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        print(f"Empleado encontrado: {empleado.NombreEmpleado}")
    except Empleado.DoesNotExist:
        print("Empleado no encontrado")
        raise Http404("Empleado no encontrado")

    print(f"Generando flujo de video para empleado ID: {empleado_id}")
    return StreamingHttpResponse(gen_frames(empleado_id), content_type='multipart/x-mixed-replace; boundary=frame')


@csrf_exempt
def detener_alarma(request):
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        return JsonResponse({"status": "ok", "message": "Alarma detenida."})
    return JsonResponse({"status": "error", "message": "No hay alarma activa."})


@csrf_exempt
def detener_monitoreo(request):
    # Liberar la cámara globalmente (si se usa un objeto compartido)
    cv2.VideoCapture(1).release()
    print("Monitoreo detenido y cámara liberada")
    return JsonResponse({"status": "ok", "message": "Monitoreo detenido"})