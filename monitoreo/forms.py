from django import forms
from .models import Empleado, Empresa

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['NombreEmpleado', 'CorreoEmpleado', 'NumeroEmpleado', 'UsuarioEmpleado']

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombreEmpresa', 'RFCEmpresa', 'NumeroEmpresa']
