# Guía de Inicio Rápido

## 5 Minutos para Empezar

### 1. Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tuusuario/ruleforge-mcp.git
cd ruleforge-mcp

# Instalar dependencias
pip install -e .
```

### 2. Configurar en Cursor

**Abre `~/.cursor/mcp.json` (o en Windows: `C:\Users\TuUsuario\.cursor\mcp.json`)**

Añade esta sección:

```json
{
  "mcpServers": {
    "ruleforge": {
      "command": "node",
      "args": ["/ruta/absoluta/a/ruleforge-mcp/wrapper.js"]
    }
  }
}
```

Reinicia Cursor.

### 3. Usar RuleForge

Abre el panel de MCP en Cursor (parte inferior derecha) y busca "RuleForge". Verás 4 herramientas:

1. **detect_technology** - Detecta tecnologías de tu proyecto (rápido)
2. **analyze_project** - Análisis detallado (puede tomar unos segundos)
3. **generate_rules** - Genera el archivo de reglas personalizado
4. **create_version_with_template** - Crea versiones del proyecto (avanzado)

### 4. Generar Tus Primeras Reglas

1. Abre tu proyecto en Cursor
2. Ve al panel MCP (esquina inferior derecha)
3. Haz clic en "generate_rules"
4. Las reglas se crearán en `.cursor/rules/rules.mdc`
5. ¡Disfruta de tus reglas personalizadas!

## Casos de Uso

### Proyecto Spring Boot

```bash
# RuleForge automáticamente detectará Spring Boot
# y generará reglas para vulnerabilidades de seguridad,
# patrones de código, buenas prácticas de Java, etc.
```

### Proyecto Vue.js

```bash
# Detecta Vue 3, genera reglas para:
# - Composables best practices
# - Patrones de componentes
# - Performance
# - TypeScript
```

### Proyecto Python + Django

```bash
# Detecta Django, genera reglas para:
# - Security (CSRF, SQL injection, XSS)
# - ORM best practices
# - Configuration safety
# - Validación de entrada
```

## Próximos Pasos

- Lee el [README completo](README.md)
- Explora el [ROADMAP](ROADMAP.md)
- Contribuye con [CONTRIBUTING.md](CONTRIBUTING.md)

¿Problemas? [Abre un issue](https://github.com/tuusuario/ruleforge-mcp/issues)

---

**¡Que disfrutes usando RuleForge!** 🚀
