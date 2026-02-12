# Contribuyendo a RuleForge

¡Gracias por tu interés en contribuir a RuleForge! Las contribuciones son lo que hace que la comunidad de código abierto sea un lugar tan especial.

## Código de Conducta

Este proyecto y todos los que participan en él están sujetos a nuestro [Código de Conducta](CODE_OF_CONDUCT.md). Al participar, se espera que cumplas con este código.

## Cómo Contribuir

### Reportar Bugs

Antes de crear un reporte de bug, por favor revisa la lista de issues ya que podrías descubrir que no necesitas crear uno. Cuando creas un reporte de bug, incluye:

- **Resumen claro y descriptivo**
- **Descripción exacta de los pasos para reproducir** el problema
- **Ejemplos específicos** para demostrar los pasos
- **Comportamiento observado y qué esperabas**
- **Screenshots y logs** si es posible
- **Tu entorno**: OS, versión de Python, versión de Cursor, etc.

### Sugerir Mejoras

Las sugerencias de mejoras se rastrean como issues. Al crear una sugerencia de mejora, incluye:

- **Resumen claro y descriptivo**
- **Descripción paso a paso** de la mejora sugerida
- **Ejemplos específicos** de cómo funcionaría
- **Por qué crees que sería útil**

### Pull Requests

- Rellena el template del PR cuando lo crees
- Sigue las guías de estilo Python (PEP 8)
- Incluye comentarios apropiados
- Termina todos los archivos con una nueva línea
- Evita cambios de plataforma en el código que envíes
- Limita los cambios a su alcance lógico

## Guías de Estilo

### Estilo de Código Python

- Sigue [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Usa `black` para formateo automático: `black .`
- Usa type hints donde sea posible
- Máximo 100 caracteres por línea
- Nombra variables de forma descriptiva

### Mensajes de Commit

- Usa imperativo, presente: "Agrega feature" no "Agregué feature"
- Limita la primera línea a 72 caracteres
- Referencia issues y pull requests generosamente después de la primera línea

### Docstrings

- Sigue el estilo Google o NumPy para docstrings
- Incluye ejemplos cuando sea apropiado

## Configuración de Desarrollo

1. Fork el repositorio
2. Clona tu fork: `git clone https://github.com/tuusuario/ruleforge-mcp.git`
3. Crea un entorno virtual: `python -m venv venv`
4. Activa el entorno: 
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
5. Instala las dependencias: `pip install -e ".[dev]"`
6. Realiza tus cambios
7. Ejecuta los tests: `pytest test_mcp.py`
8. Formatea el código: `black .`

## Testing

- Escribe tests para cualquier nueva funcionalidad
- Asegúrate de que todos los tests pasen: `pytest test_mcp.py`
- Incluye tests unitarios y de integración cuando sea posible

## Linting

- Ejecuta `black .` antes de hacer commit
- Verifica el código con `black . --check`

## Proceso de Revisión

1. Tu PR será revisado por los mantenedores
2. Se puede solicitar cambios o mejoras
3. Una vez aprobado, será mergeado

¡Gracias por contribuir! 🎉
