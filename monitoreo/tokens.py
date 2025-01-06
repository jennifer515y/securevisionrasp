from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.timezone import now
import six

class EmpleadoTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, empleado, timestamp):
        return f"{empleado.pk}{timestamp}{empleado.Activo}"

empleado_token_generator = EmpleadoTokenGenerator()
