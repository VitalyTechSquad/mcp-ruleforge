# Changelog - RuleForge MCP

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [1.1.0] - 2026-02-12

### ✨ Nuevas Características

#### **Detección Automática de Python en Wrapper**
- El wrapper Node.js ahora detecta automáticamente la instalación de Python
- Búsqueda inteligente en múltiples ubicaciones:
  - Variables de entorno `PYTHON_PATH` y `RULEFORGE_PYTHON`
  - Comandos genéricos del PATH (`python3`, `python`)
  - Windows: py launcher (`py -3`, `py`)
  - Rutas comunes de instalación en Windows (Python.org, Anaconda, Miniconda)
  - Rutas comunes en Linux/Mac (`/usr/bin`, `/usr/local/bin`, Homebrew, pyenv)
- Validación de versión mínima Python 3.8+
- Mensajes de error claros con instrucciones de solución

#### **Mejoras en el Wrapper**
- Logging mejorado con información detallada de búsqueda de Python
- Soporte para múltiples versiones de Python instaladas
- Compatibilidad mejorada con Anaconda/Miniconda
- Soporte para pyenv en Linux/Mac

### 🔧 Cambios

#### **Configuración Simplificada**
- Ya no es necesario configurar manualmente la ruta de Python
- El wrapper encuentra automáticamente el intérprete correcto
- Posibilidad de override manual mediante variables de entorno

#### **Documentación**
- Actualizado README con nueva información de detección automática
- Nuevas instrucciones de troubleshooting para problemas de Python

### 🐛 Correcciones

- **wrapper.js:** Eliminada ruta de Python hardcodeada
- **Compatibilidad Windows:** Mejorada detección en diferentes configuraciones
- **Logs:** Información más detallada para diagnóstico de problemas

### 📦 Dependencias

Sin cambios en dependencias respecto a la versión 1.0.0.

---

## [1.0.0] - 2025-10-08

### 🎉 Lanzamiento Inicial

Primera versión estable del servidor MCP de RuleForge con integración completa en Cursor.

### ✨ Características Principales

#### **Integración con Cursor**
- Servidor MCP funcional con 4 tools disponibles
- Comunicación via protocolo MCP usando stdio
- Wrapper Node.js para compatibilidad Windows
- Configuración simplificada en `mcp.json`
- Detección automática del proyecto actual

#### **Tools Implementados**
- `generate_rules` - Generación completa de reglas (all-in-one)
- `analyze_project` - Análisis detallado de proyecto
- `detect_technology` - Detección rápida de tecnologías
- `list_supported_technologies` - Lista de tecnologías soportadas

#### **Análisis Inteligente**
- Detección automática de 6 tipos de proyectos:
  - Spring Boot (1.x, 2.x, 3.x)
  - Angular (14+)
  - Vue.js (2.x, 3.x)
  - Python (Django, Flask, FastAPI)
  - Java Legacy Spring (1.x - 4.x)
  - GitLab CI/CD

#### **Adaptación de Reglas**
- Adaptación por versión detectada
- Reglas específicas por framework
- Detección de características avanzadas:
  - Spring Security, Data JPA, Actuator
  - Angular Standalone, Signals, Control Flow
  - Python Poetry, Pipenv, Docker
  - Hibernate, Struts, Log4j legacy

#### **Seguridad y Calidad**
- Detección de vulnerabilidades conocidas (CVEs)
- Análisis de configuraciones inseguras
- Detección de secrets hardcodeados
- Reglas de Clean Code específicas por lenguaje
- Priorización de seguridad (crítica, alta, media, baja)

### 🔧 Implementación Técnica

#### **Arquitectura**
- Servidor MCP basado en Python 3.8+
- Wrapper Node.js para compatibilidad multiplataforma
- Sistema de logging estructurado
- Comunicación asíncrona (async/await)

#### **Estructura del Proyecto**
```
mcp0-ruleforge/
├── server.py                # Servidor MCP principal
├── wrapper.js               # Wrapper Node.js
├── mcp_tools.py             # Implementación de tools
├── core/                    # Lógica de análisis
│   ├── project_analyzer.py  # Detección de tecnologías
│   ├── rule_generator.py    # Generación de reglas
│   └── utils.py             # Utilidades
└── templates/               # Plantillas por tecnología
```

#### **Configuración**
- `pyproject.toml` - Configuración del paquete Python
- `package.json` - Configuración del wrapper Node.js
- `MANIFEST.in` - Inclusión de templates y documentación
- `.gitignore` - Archivos ignorados (logs, cache)

### 📚 Documentación

#### **Archivos de Documentación**
- `README.md` - Documentación completa del MCP
- `INSTALLATION.md` - Guía de instalación rápida
- `CHANGELOG.md` - Este archivo
- Docstrings completos en todos los módulos

#### **Guías Incluidas**
- Instalación paso a paso (Windows, Linux, Mac)
- Configuración de Cursor
- Uso de todos los tools
- Ejemplos prácticos por tecnología
- Troubleshooting completo

### 🐛 Correcciones

#### **Problemas Resueltos**
- **pyproject.toml:** Corregida configuración de package-data con nombres inválidos
- **Encoding Windows:** Forzado UTF-8 para salida de consola (soporte emojis)
- **Ejecución en Cursor:** Implementado wrapper Node.js para compatibilidad
- **Import paths:** Configurados correctamente los módulos Python
- **Logs:** Sistema de logging funcional en carpeta `logs/`

### 🔄 Migraciones

#### **Cambios de Arquitectura**
- De ejecución directa Python a wrapper Node.js
- De `python -m mcp0-ruleforge` a `node wrapper.js`
- Sistema de logs mejorado con timestamps

### 📦 Dependencias

#### **Dependencias Principales**
- `mcp>=0.9.0` - Protocolo MCP para integración Cursor
- Python 3.8+
- Node.js 14+

#### **Dependencias de Desarrollo**
- `pytest>=7.0.0` - Testing
- `pytest-asyncio>=0.21.0` - Tests asíncronos
- `black>=23.0.0` - Formateo de código
- `mypy>=1.0.0` - Type checking

### 🚀 Instalación

```bash
# Instalación del paquete
pip install -e mcp0-ruleforge/

# Configuración en Cursor (mcp.json)
{
  "mcpServers": {
    "ruleforge": {
      "command": "cmd",
      "args": ["/c", "node", "C:\\ruta\\a\\mcp0-ruleforge\\wrapper.js"]
    }
  }
}
```

### 📊 Estadísticas

- **Lines of Code:** ~3,500 líneas
- **Archivos Python:** 8 módulos principales
- **Templates:** 6 plantillas de tecnologías
- **Tools:** 4 herramientas disponibles
- **Tecnologías Soportadas:** 6 tipos principales
- **Tiempo de Desarrollo:** ~4 semanas

### 🙏 Agradecimientos

- Equipo de Cursor por el protocolo MCP
- Comunidad de desarrolladores por feedback

### 📝 Notas de Versión

Esta es la primera versión estable después de múltiples iteraciones de desarrollo y testing. 
El MCP ha sido probado en proyectos reales de Spring Boot, Angular y Python con resultados exitosos.

**Plataformas Probadas:**
- ✅ Windows 10/11
- ✅ Linux Ubuntu 22.04
- ✅ macOS Sonoma

**IDEs Compatibles:**
- ✅ Cursor 1.7.38+

---

## [Unreleased] - Próximas Versiones

### 🔮 En Planificación

Ver [ROADMAP.md](ROADMAP.md) para el plan de evolución completo.

#### **Versión 1.2.0** (Próxima)
- Preview de reglas antes de generar
- Actualización/merge de reglas existentes
- Templates personalizados por usuario
- Análisis de proyectos multi-tecnología
- Configuración personalizable del wrapper

#### **Versión 2.0.0**
- Modo interactivo/selectivo
- Diff de reglas
- Telemetría opcional
- Auto-actualización

---

## Leyenda de Cambios

- `✨` **Added** - Nueva funcionalidad
- `🔧` **Changed** - Cambios en funcionalidad existente
- `🐛` **Fixed** - Corrección de bugs
- `🗑️` **Deprecated** - Funcionalidad que será removida
- `🔥` **Removed** - Funcionalidad removida
- `🔒` **Security** - Correcciones de seguridad
- `📚` **Documentation** - Cambios en documentación
- `⚡` **Performance** - Mejoras de rendimiento

---

**Mantenedor:** Luis Miguel Martín (lm.martin@preving.com)  
**Repositorio:** https://github.com/VitalyTechSquad/mcp-ruleforge  
**Licencia:** MIT

