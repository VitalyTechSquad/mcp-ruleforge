"""
MCP Tools para RuleForge
========================

Implementación de las herramientas (tools) del servidor MCP.
Cada tool proporciona funcionalidad específica para análisis y generación de reglas.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from core.project_analyzer import analyze_project
from core.rule_generator import generate_rules
from core.utils import load_mdc_file, save_mdc_file


def get_project_path_from_context(provided_path: Optional[str] = None) -> str:
    """
    Detecta el project_path desde el contexto o usa el proporcionado.
    
    Args:
        provided_path: Ruta proporcionada por el usuario (opcional)
        
    Returns:
        Ruta absoluta del proyecto
    """
    if provided_path:
        return os.path.abspath(provided_path)
    
    # Opción 1: Variable de entorno proporcionada por Cursor
    cursor_workspace = os.environ.get('CURSOR_WORKSPACE', None)
    if cursor_workspace:
        return cursor_workspace
    
    # Opción 2: Directorio actual de trabajo
    return os.getcwd()


async def analyze_project_tool(
    project_path: Optional[str] = None,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Tool 1: Analiza un proyecto para detectar tecnología y versión.
    
    Args:
        project_path: Ruta al proyecto (opcional, usa CWD si no se proporciona)
        verbose: Si True, muestra información detallada del análisis
        
    Returns:
        Dict con project_type, detected_tech y información adicional
    """
    try:
        path = get_project_path_from_context(project_path)
        
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": f"La ruta '{path}' no existe o no es un directorio",
                "project_path": path
            }
        
        # Analizar proyecto
        project_type, detected_tech = analyze_project(path, verbose)
        
        if not project_type:
            return {
                "success": False,
                "error": "No se pudo detectar el tipo de proyecto automáticamente",
                "project_path": path,
                "suggestion": "Intenta especificar el tipo manualmente o verifica que el proyecto tenga archivos de configuración reconocibles"
            }
        
        return {
            "success": True,
            "project_path": path,
            "project_type": project_type,
            "detected_technologies": detected_tech,
            "message": f"✅ Proyecto detectado: {project_type}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error durante el análisis: {str(e)}",
            "project_path": path if 'path' in locals() else None
        }


async def generate_rules_tool(
    project_path: Optional[str] = None,
    output_filename: str = "rules",
    custom_rules_path: Optional[str] = None,
    verbose: bool = False,
    project_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tool 2: Genera reglas Cursor completas (all-in-one).
    
    Este es el tool principal que realiza todo el proceso:
    1. Detecta el proyecto si no se especifica project_type
    2. Analiza las tecnologías
    3. Genera las reglas adaptadas
    4. Escribe el archivo .cursor/rules/rules.mdc
    
    Args:
        project_path: Ruta al proyecto (opcional)
        output_filename: Nombre del archivo de salida sin extensión (default: "rules")
        custom_rules_path: Ruta a archivo .mdc con reglas personalizadas (opcional)
        verbose: Si True, muestra información detallada
        project_type: Tipo de proyecto manual (opcional, sobrescribe detección automática)
        
    Returns:
        Dict con información del resultado
    """
    try:
        path = get_project_path_from_context(project_path)
        
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": f"La ruta '{path}' no existe o no es un directorio",
                "project_path": path
            }
        
        # Paso 1: Analizar proyecto (si no se especificó tipo manual)
        detected_type = project_type
        detected_tech = {}
        
        if not detected_type:
            if verbose:
                print(f"🔍 Analizando proyecto en: {path}")
            detected_type, detected_tech = analyze_project(path, verbose)
            
            if not detected_type:
                return {
                    "success": False,
                    "error": "No se pudo detectar el tipo de proyecto",
                    "project_path": path,
                    "suggestion": "Especifica el tipo de proyecto manualmente con el parámetro 'project_type'"
                }
        else:
            if verbose:
                print(f"📋 Usando tipo de proyecto especificado: {detected_type}")
        
        # Paso 2: Cargar reglas personalizadas (si existen)
        custom_rules = None
        if custom_rules_path:
            if os.path.exists(custom_rules_path):
                custom_rules_data = load_mdc_file(custom_rules_path)
                if custom_rules_data:
                    custom_rules = custom_rules_data.get("content", "")
                    if verbose:
                        print(f"📄 Reglas personalizadas cargadas desde: {custom_rules_path}")
            else:
                return {
                    "success": False,
                    "error": f"Archivo de reglas personalizadas no encontrado: {custom_rules_path}",
                    "project_path": path
                }
        
        # Paso 3: Generar reglas
        if verbose:
            print(f"⚙️  Generando reglas para proyecto tipo: {detected_type}")
        
        final_rules = generate_rules(
            project_type=detected_type,
            detected_tech=detected_tech,
            custom_rules_data=custom_rules,
            verbose=verbose
        )
        
        if not final_rules:
            return {
                "success": False,
                "error": f"No se pudieron generar reglas para el tipo '{detected_type}'",
                "project_path": path,
                "project_type": detected_type
            }
        
        # Paso 4: Preparar directorio de salida
        output_dir = os.path.join(path, ".cursor", "rules")
        os.makedirs(output_dir, exist_ok=True)
        
        # Asegurar extensión .mdc
        if not output_filename.endswith(".mdc"):
            output_filename += ".mdc"
        
        output_path = os.path.join(output_dir, output_filename)
        
        # Paso 5: Guardar archivo
        if verbose:
            print(f"💾 Guardando reglas en: {output_path}")
        
        if save_mdc_file(output_path, final_rules):
            # Preparar resumen de tecnologías detectadas
            tech_summary = []
            if detected_tech:
                if detected_tech.get("spring_boot_version"):
                    tech_summary.append(f"Spring Boot {detected_tech['spring_boot_version']}")
                if detected_tech.get("angular_major_version"):
                    tech_summary.append(f"Angular {detected_tech['angular_major_version']}")
                if detected_tech.get("frameworks_detected"):
                    tech_summary.extend(detected_tech["frameworks_detected"])
                if detected_tech.get("spring_framework_version"):
                    tech_summary.append(f"Spring Framework {detected_tech['spring_framework_version']}")
            
            return {
                "success": True,
                "project_path": path,
                "project_type": detected_type,
                "output_file": output_path,
                "technologies_detected": tech_summary if tech_summary else ["Análisis básico completado"],
                "message": f"✅ Reglas generadas exitosamente en: {output_path}",
                "details": {
                    "file_size": os.path.getsize(output_path),
                    "relative_path": os.path.relpath(output_path, path)
                }
            }
        else:
            return {
                "success": False,
                "error": f"No se pudo escribir el archivo en: {output_path}",
                "project_path": path,
                "project_type": detected_type
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error durante la generación de reglas: {str(e)}",
            "project_path": path if 'path' in locals() else None,
            "traceback": str(e)
        }


async def detect_technology_tool(
    project_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tool 3: Detecta tecnologías sin generar reglas (granular).
    
    Útil para obtener información rápida del proyecto sin crear archivos.
    
    Args:
        project_path: Ruta al proyecto (opcional)
        
    Returns:
        Dict con información de tecnologías detectadas
    """
    try:
        path = get_project_path_from_context(project_path)
        
        if not os.path.isdir(path):
            return {
                "success": False,
                "error": f"La ruta '{path}' no existe o no es un directorio"
            }
        
        # Analizar sin verbose para salida limpia
        project_type, detected_tech = analyze_project(path, verbose=False)
        
        if not project_type:
            return {
                "success": False,
                "error": "No se detectaron tecnologías reconocidas",
                "project_path": path
            }
        
        # Formatear información de manera legible
        tech_info = {
            "project_type": project_type,
            "details": {}
        }
        
        # Mapear información relevante según tipo de proyecto
        if project_type == "springboot":
            if detected_tech.get("spring_boot_version"):
                tech_info["details"]["version"] = detected_tech["spring_boot_version"]
            if detected_tech.get("uses_spring_security"):
                tech_info["details"]["spring_security"] = True
            if detected_tech.get("uses_spring_data_jpa"):
                tech_info["details"]["spring_data_jpa"] = True
            if detected_tech.get("uses_actuator"):
                tech_info["details"]["actuator"] = True
                
        elif project_type == "angular":
            if detected_tech.get("angular_major_version"):
                tech_info["details"]["version"] = detected_tech["angular_major_version"]
            if detected_tech.get("supports_standalone"):
                tech_info["details"]["standalone_components"] = True
            if detected_tech.get("supports_signals"):
                tech_info["details"]["signals_api"] = True
                
        elif project_type == "python":
            # Información de versión de Python
            if detected_tech.get("python_version"):
                tech_info["details"]["python_version"] = detected_tech["python_version"]
            if detected_tech.get("python_path"):
                tech_info["details"]["python_path"] = detected_tech["python_path"]
            if detected_tech.get("python_source"):
                tech_info["details"]["python_source"] = detected_tech["python_source"]
            if detected_tech.get("is_venv"):
                tech_info["details"]["is_venv"] = detected_tech["is_venv"]
            if detected_tech.get("venv_path"):
                tech_info["details"]["venv_path"] = detected_tech["venv_path"]
            
            # Frameworks detectados
            if detected_tech.get("frameworks_detected"):
                tech_info["details"]["frameworks"] = detected_tech["frameworks_detected"]
            if detected_tech.get("is_django"):
                tech_info["details"]["django"] = True
            if detected_tech.get("is_flask"):
                tech_info["details"]["flask"] = True
            if detected_tech.get("is_fastapi"):
                tech_info["details"]["fastapi"] = True
                
        elif project_type == "java_legacy_spring":
            if detected_tech.get("spring_framework_version"):
                tech_info["details"]["spring_version"] = detected_tech["spring_framework_version"]
            if detected_tech.get("security_priority"):
                tech_info["details"]["security_priority"] = detected_tech["security_priority"]
            if detected_tech.get("jsp_files_count"):
                tech_info["details"]["jsp_files"] = detected_tech["jsp_files_count"]
        
        return {
            "success": True,
            "project_path": path,
            "technology": tech_info,
            "raw_details": detected_tech  # Para información completa
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error detectando tecnologías: {str(e)}",
            "project_path": path if 'path' in locals() else None
        }


async def list_supported_technologies_tool() -> Dict[str, Any]:
    """
    Tool 4: Lista todas las tecnologías soportadas por RuleForge MCP.
    
    Returns:
        Dict con lista de tecnologías y sus características
    """
    return {
        "success": True,
        "supported_technologies": {
            "springboot": {
                "name": "Spring Boot",
                "description": "Proyectos Spring Boot modernos (versiones 1.x, 2.x, 3.x)",
                "detection_files": ["pom.xml", "build.gradle", "application.properties"],
                "features": [
                    "Detección de versión completa",
                    "Análisis de Spring Security",
                    "Detección de Spring Data JPA",
                    "Alertas de Spring Actuator",
                    "Reglas de seguridad específicas por versión"
                ]
            },
            "angular": {
                "name": "Angular",
                "description": "Aplicaciones Angular (versiones 14+)",
                "detection_files": ["angular.json", "package.json"],
                "features": [
                    "Detección de versión major",
                    "Soporte para Standalone Components",
                    "Detección de Signals API (v16+)",
                    "Nueva sintaxis de control flow (v17+)",
                    "Análisis de NgRx y Angular Material"
                ]
            },
            "vue": {
                "name": "Vue.js",
                "description": "Aplicaciones Vue.js (2.x y 3.x)",
                "detection_files": ["package.json", "vue.config.js", "vite.config.js"],
                "features": [
                    "Detección de versión",
                    "Soporte para Nuxt.js",
                    "Reglas de seguridad XSS",
                    "Composition API patterns"
                ]
            },
            "python": {
                "name": "Python",
                "description": "Proyectos Python con frameworks web",
                "detection_files": ["requirements.txt", "pyproject.toml", "manage.py", ".python-version", "Pipfile"],
                "features": [
                    "Detección automática de versión de Python",
                    "Detección de ruta del intérprete",
                    "Soporte para entornos virtuales (venv, .venv, env)",
                    "Detección de pyenv (.python-version)",
                    "Detección de Django",
                    "Detección de Flask",
                    "Detección de FastAPI",
                    "Análisis de dependencias",
                    "Reglas PEP 8"
                ]
            },
            "java_legacy_spring": {
                "name": "Java Legacy Spring",
                "description": "Proyectos Java Legacy con Spring Framework y JSP",
                "detection_files": ["web.xml", "applicationContext.xml", "*.jsp"],
                "features": [
                    "Detección de Spring Framework legacy",
                    "Análisis de vulnerabilidades críticas",
                    "Detección de Log4Shell",
                    "Análisis de Struts",
                    "Priorización de seguridad"
                ]
            },
            "gitlab_ci": {
                "name": "GitLab CI/CD",
                "description": "Pipelines GitLab CI/CD",
                "detection_files": [".gitlab-ci.yml"],
                "features": [
                    "Análisis de pipelines",
                    "DevSecOps best practices",
                    "Detección de secrets",
                    "Configuración Docker"
                ]
            }
        },
        "total_technologies": 6
    }
