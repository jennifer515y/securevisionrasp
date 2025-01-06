from django.db import models
from django.contrib.auth.models import User

class Empresa(models.Model):
    nombreEmpresa = models.CharField(max_length=255)  # Cambié el nombre duplicado
    RFCEmpresa = models.CharField(max_length=13, unique=True)
    NumeroEmpresa = models.CharField(max_length=15)
    CorreoEmpresa = models.EmailField(unique=True)
    ContrasenaEmpresa = models.CharField(max_length=128)
    TituloEmpresa = models.CharField(max_length=100) 

    def __str__(self):  
        return f"{self.TituloEmpresa} - {self.CorreoEmpresa}"


class Empleado(models.Model):
    id = models.AutoField(primary_key=True) 
    NombreEmpleado = models.CharField(max_length=255)
    EmpresaEmpleado = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    UsuarioEmpleado = models.CharField(max_length=100, unique=True, db_index=True)
    ContrasenaEmpleado = models.CharField(max_length=128)
    CorreoEmpleado = models.EmailField(unique=True, db_index=True)
    NumeroEmpleado = models.CharField(max_length=15)
    Activo = models.BooleanField(default=False)
    Latitud = models.FloatField(null=True, blank=True)
    Longitud = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.NombreEmpleado} - {self.CorreoEmpleado}"


class Usuario(models.Model):
    TIPOS_USUARIO = [
        ('empresa', 'Empresa'),
        ('empleado', 'Empleado'),
    ]

    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena = models.CharField(max_length=100)
    tipo_usuario = models.CharField(max_length=10, choices=TIPOS_USUARIO)

    def __str__(self):
        return f"{self.nombre} ({self.tipo_usuario})"

    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_empresa = models.BooleanField(default=False)  # Si es empresa
    is_empleado = models.BooleanField(default=False)  # Si es empleado
    empresa = models.CharField(max_length=255, blank=True, null=True)  # Empresa donde trabaja el empleado (si es empleado)

    def __str__(self):
        return self.user.username
    

class Alerta(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    activa = models.BooleanField(default=False)  # Campo que indica si la alerta está activa

    def __str__(self):
        return f"Alerta de {self.empleado.NombreEmpleado} en {self.fecha}"

