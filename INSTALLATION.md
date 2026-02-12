# Guía de Instalación Rápida - RuleForge MCP

## 📋 Requisitos Previos

- **Python 3.8+** instalado
- **Node.js 14+** instalado
- **Cursor IDE** instalado
- **pip** para instalar paquetes Python

---

## 🚀 Instalación en 3 Pasos

### Paso 1: Instalar el paquete Python

```bash
cd ruleforge
pip install -e mcp0-ruleforge/
```

### Paso 2: Configurar en Cursor

Edita el archivo de configuración MCP de Cursor:

**Ubicación:**
- Windows: `C:\Users\TuUsuario\.cursor\mcp.json`
- Linux/Mac: `~/.cursor/mcp.json`

O abre desde Cursor:
- Presiona `Ctrl+Shift+P` (Windows/Linux) o `Cmd+Shift+P` (Mac)
- Busca "Preferences: Open User Settings (JSON)"

**Configuración para Windows:**

```json
{
  "mcpServers": {
    "ruleforge": {
      "command": "cmd",
      "args": [
        "/c",
        "node",
        "C:\\ruta\\completa\\a\\ruleforge\\mcp0-ruleforge\\wrapper.js"
      ]
    }
  }
}
```

> **⚠️ IMPORTANTE:** Reemplaza `C:\\ruta\\completa\\a\\ruleforge\\mcp0-ruleforge\\wrapper.js` con la ruta real de tu instalación. Usa dobles barras invertidas `\\`.

**Ejemplo real:**
```json
{
  "mcpServers": {
    "ruleforge": {
      "command": "cmd",
      "args": [
        "/c",
        "node",
        "C:\\Users\\Juan\\Projects\\ruleforge\\mcp0-ruleforge\\wrapper.js"
      ]
    }
  }
}
```

**Configuración para Linux/Mac:**

```json
{
  "mcpServers": {
    "ruleforge": {
      "command": "node",
      "args": [
        "/home/usuario/ruleforge/mcp0-ruleforge/wrapper.js"
      ]
    }
  }
}
```

### Paso 3: Reiniciar Cursor y Verificar

1. **Cierra Cursor completamente** (todas las ventanas)
2. **Espera 5-10 segundos**
3. **Abre Cursor**
4. **Ve al panel de "Tools & MCP"**
5. Deberías ver:
   - ✅ **"ruleforge"** con punto verde
   - ✅ **"4 tools"** disponibles

---

## ✅ Verificación de Instalación

### Opción A: Desde el panel de MCP

1. Abre el panel "Tools & MCP" en Cursor
2. Haz clic en "ruleforge"
3. Deberías ver 4 tools listados:
   - `generate_rules`
   - `analyze_project`
   - `detect_technology`
   - `list_supported_technologies`

### Opción B: Verificar logs

Si aparece el punto verde ✅, el servidor está funcionando correctamente.

Si hay problemas, verifica los logs:

```bash
# Windows (PowerShell)
Get-ChildItem C:\ruta\a\ruleforge\mcp0-ruleforge\logs

# Linux/Mac
ls /ruta/a/ruleforge/mcp0-ruleforge/logs/
```

Deberías ver archivos:
- `wrapper_*.log` - Log del wrapper Node.js
- `server_*.log` - Log del servidor Python

---

## 🎯 Primer Uso

Una vez instalado, puedes generar reglas para cualquier proyecto:

1. Abre tu proyecto en Cursor
2. Ve al panel de "Tools & MCP"
3. Selecciona "ruleforge"
4. Ejecuta el tool `generate_rules` con los parámetros deseados

**Ejemplo de parámetros:**
```json
{
  "project_path": "/mi/proyecto",
  "project_type": "python",
  "verbose": true
}
```

El archivo `.cursor/rules/rules.mdc` se creará automáticamente en tu proyecto.

---

## ❌ Solución de Problemas

### Problema 1: Punto rojo ❌ en "ruleforge"

**Causa:** Cursor no puede ejecutar el servidor.

**Soluciones:**

1. **Verifica la ruta del wrapper:**
   - Asegúrate de que la ruta en `mcp.json` es correcta y absoluta
   - En Windows, usa dobles barras: `C:\\Users\\...`

2. **Verifica Node.js:**
   ```bash
   node --version
   ```
   Debe mostrar v14 o superior

3. **Verifica Python:**
   ```bash
   python --version
   ```
   Debe mostrar 3.8 o superior

4. **Reinicia Cursor:**
   - Cierra TODAS las ventanas
   - Espera 10 segundos
   - Vuelve a abrir

### Problema 2: "No tools, prompts, or resources"

**Causa:** El servidor se ejecuta pero no carga las tools.

**Soluciones:**

1. **Verifica los logs:**
   ```bash
   # Ve a la carpeta de logs
   cd ruleforge/mcp0-ruleforge/logs
   
   # Lee el último log del servidor
   # Windows
   type server_*.log | Select-Object -Last 50
   
   # Linux/Mac
   tail -50 server_*.log
   ```

2. **Reinstala el paquete:**
   ```bash
   pip uninstall ruleforge-mcp
   pip install -e mcp0-ruleforge/
   ```

3. **Verifica que el módulo MCP está instalado:**
   ```bash
   pip show mcp
   ```

### Problema 3: "Module 'mcp' not found"

**Solución:**
```bash
pip install mcp>=0.9.0
```

### Problema 4: Error de encoding en Windows

**Solución:** Ya está resuelto en la versión actual. Si persiste, verifica que estás usando la última versión:
```bash
cd ruleforge
git pull origin main
pip install -e mcp0-ruleforge/ --force-reinstall
```

---

## 🔧 Comandos Útiles

### Reinstalar completamente

```bash
# 1. Desinstalar
pip uninstall ruleforge-mcp

# 2. Limpiar cache
pip cache purge

# 3. Reinstalar
cd ruleforge
pip install -e mcp0-ruleforge/

# 4. Reiniciar Cursor
```

### Ver logs en tiempo real (debug)

**Windows (PowerShell):**
```powershell
Get-Content C:\ruta\a\ruleforge\mcp0-ruleforge\logs\server_*.log -Wait -Tail 50
```

**Linux/Mac:**
```bash
tail -f /ruta/a/ruleforge/mcp0-ruleforge/logs/server_*.log
```

### Ejecutar el servidor manualmente (para debug)

```bash
cd mcp0-ruleforge
node wrapper.js
```

Presiona `Ctrl+C` para detener.

---

## 📞 Soporte

Si los problemas persisten:

1. **Revisa el README completo:** `README.md`
2. **Abre un issue:** https://github.com/VitalyTechSquad/mcp-ruleforge/issues
3. **Contacto:** lm.martin@preving.com

---

**¡Disfruta generando reglas Cursor automáticamente!** 🚀
