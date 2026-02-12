#!/usr/bin/env python3
"""
RuleForge MCP Server
====================

Servidor MCP (Model Context Protocol) para integración con Cursor.
Proporciona herramientas para análisis automático de proyectos y generación de reglas.

Autor: Luis Miguel Martín
Versión: 1.1.0
"""

import asyncio
import json
import sys
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Importar los tools implementados
from mcp_tools import (
    analyze_project_tool,
    generate_rules_tool,
    detect_technology_tool,
    list_supported_technologies_tool,
)

# Configurar logging básico para debug (opcional)
import logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler(f"logs/server_{os.getpid()}.log", encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)


def create_app():
    """Crea y configura el servidor MCP."""
    app = Server("ruleforge-mcp")
    logger.info("Servidor RuleForge MCP iniciado")

    @app.list_tools()
    async def handle_list_tools():
        """Lista todos los tools disponibles."""
        return [
            Tool(
                name="generate_rules",
                description=(
                    "Genera reglas Cursor completas automáticamente (ALL-IN-ONE). "
                    "Analiza el proyecto actual, detecta tecnologías y versiones, "
                    "y crea el archivo .cursor/rules/rules.mdc con reglas personalizadas. "
                    "Este es el tool principal recomendado para uso general."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Ruta al proyecto (opcional, usa el directorio actual si no se especifica)"
                        },
                        "output_filename": {
                            "type": "string",
                            "description": "Nombre del archivo de salida sin extensión (default: 'rules')",
                            "default": "rules"
                        },
                        "custom_rules_path": {
                            "type": "string",
                            "description": "Ruta a archivo .mdc con reglas personalizadas adicionales (opcional)"
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Mostrar información detallada del proceso (default: false)",
                            "default": False
                        },
                        "project_type": {
                            "type": "string",
                            "description": "Tipo de proyecto manual: springboot, angular, vue, python, java_legacy_spring, gitlab_ci (opcional)",
                            "enum": ["springboot", "angular", "vue", "python", "java_legacy_spring", "gitlab_ci"]
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="analyze_project",
                description=(
                    "Analiza un proyecto para detectar su tecnología, versión y características. "
                    "Útil para inspeccionar qué detectará RuleForge antes de generar reglas. "
                    "No crea archivos, solo retorna información."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Ruta al proyecto (opcional, usa el directorio actual si no se especifica)"
                        },
                        "verbose": {
                            "type": "boolean",
                            "description": "Mostrar información detallada del análisis (default: false)",
                            "default": False
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="detect_technology",
                description=(
                    "Detecta rápidamente las tecnologías principales del proyecto sin análisis profundo. "
                    "Retorna información básica de versión y frameworks detectados. "
                    "Más rápido que analyze_project pero con menos detalles."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_path": {
                            "type": "string",
                            "description": "Ruta al proyecto (opcional, usa el directorio actual si no se especifica)"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="list_supported_technologies",
                description=(
                    "Lista todas las tecnologías soportadas por RuleForge MCP. "
                    "Muestra qué tipos de proyectos puede analizar y qué características "
                    "detecta para cada tecnología."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
        ]

    @app.call_tool()
    async def handle_call_tool(name: str, arguments: Any):
        """Maneja las llamadas a los tools."""
        logger.info(f"Tool llamado: {name}")
        
        try:
            # Asegurar que arguments sea un dict
            if not isinstance(arguments, dict):
                arguments = {}
            
            # Ejecutar el tool correspondiente
            if name == "generate_rules":
                result = await generate_rules_tool(
                    project_path=arguments.get("project_path"),
                    output_filename=arguments.get("output_filename", "rules"),
                    custom_rules_path=arguments.get("custom_rules_path"),
                    verbose=arguments.get("verbose", False),
                    project_type=arguments.get("project_type")
                )
                
            elif name == "analyze_project":
                result = await analyze_project_tool(
                    project_path=arguments.get("project_path"),
                    verbose=arguments.get("verbose", False)
                )
                
            elif name == "detect_technology":
                result = await detect_technology_tool(
                    project_path=arguments.get("project_path")
                )
                
            elif name == "list_supported_technologies":
                result = await list_supported_technologies_tool()
                
            else:
                result = {
                    "success": False,
                    "error": f"Tool desconocido: {name}",
                    "available_tools": ["generate_rules", "analyze_project", "detect_technology", "list_supported_technologies"]
                }
            
            logger.info(f"Tool {name} ejecutado: success={result.get('success')}")
            
            # Formatear resultado
            formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
            
            # Añadir emoji según el resultado
            if result.get("success"):
                prefix = "✅ **Éxito**\n\n"
            else:
                prefix = "❌ **Error**\n\n"
            
            return [
                TextContent(
                    type="text",
                    text=prefix + formatted_result
                )
            ]
            
        except Exception as e:
            logger.error(f"Error en tool {name}: {e}")
            error_result = {
                "success": False,
                "error": f"Error inesperado: {str(e)}",
                "tool": name,
                "arguments": arguments
            }
            
            return [
                TextContent(
                    type="text",
                    text="❌ **Error crítico**\n\n" + json.dumps(error_result, indent=2, ensure_ascii=False)
                )
            ]

    return app


async def main():
    """Punto de entrada principal del servidor MCP."""
    app = create_app()
    
    # Ejecutar el servidor usando stdio para comunicación con Cursor
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servidor detenido por usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error fatal en el servidor: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
