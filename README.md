# RuleForge MCP Server

**Servidor MCP (Model Context Protocol) para generación automática de reglas Cursor**

RuleForge MCP es una integración nativa con Cursor que permite analizar proyectos de forma inteligente y generar reglas personalizadas automáticamente. Detecta tecnologías, versiones, frameworks y crea configuraciones `.cursor/rules` optimizadas para tu stack tecnológico.

## 🚀 Características Principales

### **🔍 Análisis Inteligente**
- **Detección Automática:** Identifica Spring Boot, Angular, Vue, Python, Java Legacy, GitLab CI
- **Detección de Versiones:** Reconoce versiones específicas y adapta las reglas
- **Sin Configuración Manual:** No necesitas especificar la ruta del proyecto, usa el proyecto actual automáticamente

### **⚡ Integración Nativa con Cursor**
- **Acceso Directo:** Usa los tools de RuleForge desde el panel de MCP en Cursor
- **Generación Instantánea:** Crea archivos `.cursor/rules/rules.mdc` directamente
- **4 Tools Disponibles:** Análisis granular o generación completa según necesidad

### **🛡️ Seguridad y Clean Code**
- **Detección de Vulnerabilidades:** CVEs, configuraciones inseguras, secretos hardcodeados
- **Análisis de Calidad:** Code smells, anti-patrones, violaciones SOLID
- **Reglas Específicas:** Adaptadas por tecnología y versión detectada

## 📦 Instalación

### Requisitos Previos

- **Python 3.8 o superior** (detectado automáticamente)
- **Node.js 14 o superior** (para el wrapper)
- **Cursor IDE** instalado
- **pip** para gestión de paquetes Python

### Paso 1: Instalar el paquete Python

```bash
pip install -e .
```

### Paso 2: Configurar en Cursor

Añade el servidor MCP a tu configuración de Cursor.

**Ubicación del archivo de configuración:**
- Presiona `Ctrl+Shift+P` (Windows/Linux) o `Cmd+Shift+P` (Mac)
- Busca "Preferences: Open User Settings (JSON)"
- O edita directamente: `~/.cursor/mcp.json` (Linux/Mac) o `C:\Users\TuUsuario\.cursor\mcp.json` (Windows)

**Configuración para mcp.json:**

```json
{
  "mcpServers": {
    "ruleforge": {
      "command": "node",
      "args": ["path/to/ruleforge-public/wrapper.js"]
    }
  }
}
```

## 🎯 Uso

### Desde Cursor

1. Abre el panel de MCP (esquina inferior derecha)
2. Busca "RuleForge" 
3. Selecciona uno de los 4 tools disponibles:
   - **Análisis Rápido:** Detecta tecnologías principales
   - **Análisis Completo:** Análisis exhaustivo del proyecto
   - **Generar Reglas:** Crea el archivo `.cursor/rules/rules.mdc`
   - **Crear/Actualizar Versión:** Crea una nueva versión con template

### Desde Terminal

```bash
# Análisis rápido
python -m mcp_tools analyze_project --quick

# Análisis completo
python -m mcp_tools analyze_project --verbose

# Generar reglas
python -m mcp_tools generate_rules

# Generar reglas por tipo de proyecto
python -m mcp_tools generate_rules --project_type springboot
```

## 🛠️ Tecnologías Soportadas

- **Spring Boot** (Java)
- **Angular** (TypeScript)
- **Vue.js** (JavaScript)
- **Python** (Django, Flask, FastAPI)
- **Java Legacy** (Spring oldstyle)
- **GitLab CI** (DevOps)

## 📋 Reglas Generadas

Las reglas generadas incluyen:

- ✅ Detección automática de tecnologías y versiones
- ✅ Patrones de seguridad específicos del stack
- ✅ Convenciones de código y clean code
- ✅ Mejores prácticas por framework
- ✅ Configuraciones de linting
- ✅ Reglas de testing

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Luis Miguel Martín**

## 🙏 Agradecimientos

- Cursor IDE por el soporte a MCP
- Comunidad de desarrolladores que contribuyen con feedback

## 📞 Soporte

Si encuentras problemas o tienes sugerencias, por favor:
- Abre un issue en este repositorio
- Contáctame a través de GitHub

---

**¿Te gustaría contribuir?** ¡Simplemente abre un issue o PR!

**Última actualización:** Febrero 2026
