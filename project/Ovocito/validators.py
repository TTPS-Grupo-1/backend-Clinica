from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


# Reusable, importable validator for Ovocito.identificador
identificador_regex = r'^[A-Za-z0-9_-]+$'
identificador_message = 'El identificador solo puede contener letras, números, guiones y guiones bajos.'

# RegexValidator instance at module level (serializable by migrations)
validar_identificador = RegexValidator(regex=identificador_regex, message=identificador_message)


def validar_identificador_personalizado(value: str) -> None:
    """Función-validator alternativa con la misma lógica.

    Está definida a nivel de módulo para que sea importable y serializable
    si se prefiere usar una función en lugar de la clase RegexValidator.
    """
    if not validar_identificador.regex.match(value):
        raise ValidationError(identificador_message)
