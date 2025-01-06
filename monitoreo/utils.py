import cv2
import mediapipe as mp
import time
import pygame
from scipy.spatial import distance as dist
import threading
from monitoreo.models import Alerta, Empleado 
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib.auth.models import User

# Variables globales
contador_bips = 0
contador_alertas = 0
tiempo_inicial_cerrados = None
tiempo_ultimo_bip = None

# Inicializa pygame para el sonido
pygame.mixer.init()

# Constantes
EAR_UMBRAL = 0.25
TIEMPO_PARPADO_UMBRAL = 2.0
OJO_IZQUIERDO_INDICES = [33, 160, 158, 133, 153, 144]
OJO_DERECHO_INDICES = [362, 385, 387, 263, 373, 380]

def registrar_alerta(empleado_id):
    print(f"ID recibido: {empleado_id}")  
    try:
        empleado = Empleado.objects.get(id=empleado_id)
        alerta = Alerta.objects.create(empleado=empleado, fecha=now(), activa=True)
        print(f"Alerta registrada para el empleado {empleado.NombreEmpleado}")
        return JsonResponse({'alerta_activada': True, 'empleado_id': empleado_id})
    except Empleado.DoesNotExist:
        print(f"El empleado con ID {empleado_id} no existe")
        return JsonResponse({'alerta_activada': False, 'empleado_id': empleado_id})


def calcular_ear(landmarks, ojo_indices):
    A = dist.euclidean(landmarks[ojo_indices[1]], landmarks[ojo_indices[5]])
    B = dist.euclidean(landmarks[ojo_indices[2]], landmarks[ojo_indices[4]])
    C = dist.euclidean(landmarks[ojo_indices[0]], landmarks[ojo_indices[3]])
    ear = (A + B) / (2.0 * C)
    return ear

def reproducir_bip():
    pygame.mixer.music.load('monitoreo/static/sounds/bip.mp3')
    pygame.mixer.music.play()

def reproducir_alarma(empleado_id):
    pygame.mixer.music.load('monitoreo/static/sounds/sonido2.mp3')
    pygame.mixer.music.play()
    registrar_alerta(empleado_id)

def obtener_usuarios_activos(request):
    empleados_activos_ids = Empleado.objects.filter(empleado__is_active=True).values_list('id', flat=True)
    return JsonResponse({'success': True, 'empleados_activos_ids': list(empleados_activos_ids)})

def gen_frames(empleado_id):
    global contador_bips, contador_alertas, tiempo_inicial_cerrados, tiempo_ultimo_bip

    try:
        empleado = Empleado.objects.get(id=empleado_id)
    except Empleado.DoesNotExist:
        print(f"Empleado con ID {empleado_id} no encontrado")
        return  

    cap = cv2.VideoCapture(1)  # Inicializa la cámara aquí
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        return

    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:
        while True:
            success, frame = cap.read()
            if not success:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultado = face_mesh.process(rgb_frame)

            if resultado.multi_face_landmarks:
                for face_landmarks in resultado.multi_face_landmarks:
                    height, width, _ = frame.shape
                    landmarks = [(int(pt.x * width), int(pt.y * height)) for pt in face_landmarks.landmark]

                    ear_izquierdo = calcular_ear(landmarks, OJO_IZQUIERDO_INDICES)
                    ear_derecho = calcular_ear(landmarks, OJO_DERECHO_INDICES)
                    ear_promedio = (ear_izquierdo + ear_derecho) / 2.0

                    if ear_promedio < EAR_UMBRAL:
                        if tiempo_inicial_cerrados is None:
                            tiempo_inicial_cerrados = time.time()

                        tiempo_cerrados = time.time() - tiempo_inicial_cerrados

                        if tiempo_cerrados >= TIEMPO_PARPADO_UMBRAL:
                            if tiempo_ultimo_bip is None or (time.time() - tiempo_ultimo_bip) >= 1:
                                if not pygame.mixer.music.get_busy():
                                    threading.Thread(target=reproducir_bip).start()
                                    contador_bips += 1
                                    tiempo_ultimo_bip = time.time()
                                if contador_bips == 3:
                                    threading.Thread(target=reproducir_alarma, args=(empleado.id,)).start()
                                    contador_alertas += 1
                                    contador_bips = 0
                    else:
                        tiempo_inicial_cerrados = None
                        tiempo_ultimo_bip = None

            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()  # Libera la cámara al finalizar