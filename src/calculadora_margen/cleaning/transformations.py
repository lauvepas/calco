from typing import Any, Callable
import re

class Transformation:
    """
    Clase base para definir transformaciones.
    Permite encapsular la lógica de transformación y sus parámetros.
    """
    def __call__(self, value: Any) -> Any:
        """
        Método que ejecuta la transformación.
        Debe ser implementado por las clases hijas.
        """
        raise NotImplementedError("Las subclases deben implementar este método")

    @property
    def description(self) -> str:
        """Descripción de lo que hace la transformación"""
        return self.__class__.__doc__ or "No hay descripción disponible"


class UppercaseTransformation(Transformation):
    """Convierte el texto a mayúsculas"""
    def __call__(self, value: Any) -> str:
        return str(value).upper()


class StripAndNormalizeTransformation(Transformation):
    """
    Normaliza texto eliminando espacios extra y caracteres especiales.
    Opcionalmente puede convertir a mayúsculas/minúsculas.
    """
    def __init__(self, to_upper: bool = False, to_lower: bool = False):
        self.to_upper = to_upper
        self.to_lower = to_lower

    def __call__(self, value: Any) -> str:
        # Convertir a string y eliminar espacios
        text = str(value).strip()
        # Normalizar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        if self.to_upper:
            text = text.upper()
        elif self.to_lower:
            text = text.lower()
            
        return text


class NumericNormalizer(Transformation):
    """
    Normaliza valores numéricos aplicando redondeo y/o rangos.
    """
    def __init__(self, decimals: int = 2, min_value: float = None, max_value: float = None):
        self.decimals = decimals
        self.min_value = min_value
        self.max_value = max_value

    def __call__(self, value: Any) -> float:
        try:
            num = float(value)
            # Aplicar redondeo
            num = round(num, self.decimals)
            # Aplicar límites si están definidos
            if self.min_value is not None:
                num = max(num, self.min_value)
            if self.max_value is not None:
                num = min(num, self.max_value)
            return num
        except (ValueError, TypeError):
            return value


# Diccionario de transformaciones predefinidas comunes
common_transformations = {
    'to_upper': UppercaseTransformation(),
    'normalize_text': StripAndNormalizeTransformation(),
    'normalize_text_upper': StripAndNormalizeTransformation(to_upper=True),
    'normalize_text_lower': StripAndNormalizeTransformation(to_lower=True),
    'round_2_decimals': NumericNormalizer(decimals=2),
} 