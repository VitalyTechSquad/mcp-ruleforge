# Estructura del Proyecto

```
ruleforge-mcp/
├── core/                           # Lógica principal de análisis
│   ├── __init__.py
│   ├── project_analyzer.py         # Análisis de proyectos
│   └── rule_generator.py           # Generación de reglas
├── templates/                      # Templates de reglas por tecnología
│   ├── python.mdc
│   ├── spring_boot.mdc
│   ├── angular.mdc
│   ├── vue.mdc
│   ├── java_legacy.mdc
│   └── gitlab_ci.mdc
├── server.py                       # Servidor MCP principal
├── mcp_tools.py                    # Definición de tools MCP
├── wrapper.js                      # Wrapper Node.js
├── requirements.txt                # Dependencias Python
├── pyproject.toml                  # Configuración del paquete
├── package.json                    # Configuración Node.js
├── test_mcp.py                     # Tests
├── README.md                       # Documentación principal
├── QUICKSTART.md                   # Guía de inicio rápido
├── CONTRIBUTING.md                 # Guía para contribuir
├── LICENSE                         # Licencia MIT
└── .gitignore                      # Archivos ignorados

```

## Componentes Clave

### `core/project_analyzer.py`
- Escanea el proyecto y detecta tecnologías
- Identifica archivos clave de configuración
- Analiza vulnerabilidades y patrones de código

### `core/rule_generator.py`
- Genera reglas basadas en tecnología detectada
- Adapta reglas según versiones
- Combina templates de seguridad y clean code

### `templates/`
- Contiene las reglas base para cada tecnología
- Se personalizan según el análisis del proyecto
- Pueden ser actualizadas fácilmente

### `mcp_tools.py`
- Define los 4 tools de MCP disponibles
- Interfaz entre Cursor y la lógica de análisis
- Manejo de parámetros y errores

### `wrapper.js`
- Inicia el servidor Python desde Node.js
- Maneja la comunicación MCP
- Detecta automáticamente la instalación de Python

## Flujo de Ejecución

1. Usuario abre Cursor → Panel MCP
2. Usuario selecciona un tool → wrapper.js recibe la solicitud
3. wrapper.js → server.py (Python)
4. server.py → mcp_tools.py → core/
5. Análisis → Generación de reglas
6. Resultado → Cursor IDE

## Adición de Nuevas Tecnologías

1. Crear nuevo archivo en `templates/` (ej: `nodejs.mdc`)
2. Actualizar detección en `core/project_analyzer.py`
3. Añadir test en `test_mcp.py`
4. Documentar en `ROADMAP.md`

---

**¿Preguntas sobre la estructura?** [Abre un issue](https://github.com/tuusuario/ruleforge-mcp/issues)
