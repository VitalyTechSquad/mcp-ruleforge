"""
Test de validación para RuleForge MCP Server
============================================

Script de prueba para verificar que el servidor MCP y los tools
funcionan correctamente.

Uso:
    python test_mcp.py
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Añadir el directorio actual al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

from mcp_tools import (
    analyze_project_tool,
    generate_rules_tool,
    detect_technology_tool,
    list_supported_technologies_tool,
    get_project_path_from_context
)


async def test_get_project_path():
    """Test: Obtener ruta del proyecto"""
    print("\n" + "="*60)
    print("TEST 1: get_project_path_from_context")
    print("="*60)
    
    # Test sin parámetros (debe usar CWD)
    path = get_project_path_from_context()
    print(f"[OK] Ruta detectada: {path}")
    assert os.path.isdir(path), "La ruta debe ser un directorio valido"
    
    # Test con parámetro
    parent_path = get_project_path_from_context("..")
    print(f"[OK] Ruta con parametro: {parent_path}")
    
    print("[PASS] TEST PASADO\n")


async def test_list_supported_technologies():
    """Test: Listar tecnologías soportadas"""
    print("\n" + "="*60)
    print("TEST 2: list_supported_technologies_tool")
    print("="*60)
    
    result = await list_supported_technologies_tool()
    
    assert result["success"] == True, "Debe retornar success=True"
    assert "supported_technologies" in result, "Debe contener 'supported_technologies'"
    assert result["total_technologies"] == 6, "Debe soportar 6 tecnologias"
    
    print("[OK] Tecnologias soportadas:")
    for tech_id, tech_info in result["supported_technologies"].items():
        print(f"  - {tech_id}: {tech_info['name']}")
    
    print("[PASS] TEST PASADO\n")


async def test_detect_technology():
    """Test: Detectar tecnología del proyecto"""
    print("\n" + "="*60)
    print("TEST 3: detect_technology_tool")
    print("="*60)
    
    # Test en el directorio del proyecto RuleForge
    # Navegamos al directorio padre que contiene el proyecto RuleForge
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    result = await detect_technology_tool(project_path=parent_dir)
    
    print(f"[OK] Proyecto analizado: {parent_dir}")
    print(f"[OK] Resultado: {json.dumps(result, indent=2, ensure_ascii=True)}")
    
    # La validacion depende del proyecto, puede no detectar nada o detectar Python
    if result["success"]:
        print(f"[OK] Tecnologia detectada: {result.get('technology', {}).get('project_type', 'N/A')}")
    else:
        print("[INFO] No se detecto tecnologia (esperado si no hay proyecto reconocible)")
    
    print("[PASS] TEST PASADO\n")


async def test_analyze_project():
    """Test: Análisis completo de proyecto"""
    print("\n" + "="*60)
    print("TEST 4: analyze_project_tool")
    print("="*60)
    
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    result = await analyze_project_tool(project_path=parent_dir, verbose=False)
    
    print(f"[OK] Analisis completo ejecutado")
    print(f"[OK] Resultado: {json.dumps(result, indent=2, ensure_ascii=True)}")
    
    assert "success" in result, "Debe contener campo 'success'"
    
    if result["success"]:
        print(f"[OK] Tipo detectado: {result.get('project_type', 'N/A')}")
    else:
        print("[INFO] No se detecto proyecto (esperado en algunos casos)")
    
    print("[PASS] TEST PASADO\n")


async def test_generate_rules_validation():
    """Test: Validación de parámetros de generación (sin crear archivo)"""
    print("\n" + "="*60)
    print("TEST 5: generate_rules_tool (validación)")
    print("="*60)
    
    # Test con directorio inexistente
    result = await generate_rules_tool(
        project_path="/ruta/inexistente/test",
        verbose=False
    )
    
    print(f"[OK] Test con ruta inexistente:")
    print(f"  - Success: {result['success']}")
    print(f"  - Error esperado: {result.get('error', 'N/A')}")
    
    assert result["success"] == False, "Debe fallar con ruta inexistente"
    assert "error" in result, "Debe contener mensaje de error"
    
    print("[PASS] TEST PASADO\n")


async def test_structure_validation():
    """Test: Validar estructura de archivos del MCP"""
    print("\n" + "="*60)
    print("TEST 6: Validación de estructura de archivos")
    print("="*60)
    
    base_dir = Path(__file__).parent
    
    required_files = [
        "__init__.py",
        "__main__.py",
        "server.py",
        "mcp_tools.py",
        "pyproject.toml",
        "requirements.txt",
        "README.md",
        "core/__init__.py",
        "core/project_analyzer.py",
        "core/rule_generator.py",
        "core/utils.py",
    ]
    
    required_templates = [
        "templates/angular.mdc",
        "templates/gitlab_ci.mdc",
        "templates/java_legacy_spring.mdc",
        "templates/python.mdc",
        "templates/spring_boot.mdc",
        "templates/vue.mdc",
    ]
    
    all_required = required_files + required_templates
    
    for file_path in all_required:
        full_path = base_dir / file_path
        assert full_path.exists(), f"Archivo requerido no encontrado: {file_path}"
        print(f"  [OK] {file_path}")
    
    print(f"\n[OK] Todos los archivos requeridos ({len(all_required)}) estan presentes")
    print("[PASS] TEST PASADO\n")


async def test_imports():
    """Test: Validar que todos los imports funcionen"""
    print("\n" + "="*60)
    print("TEST 7: Validación de imports")
    print("="*60)
    
    try:
        from core import project_analyzer
        print("  [OK] core.project_analyzer")
        
        from core import rule_generator
        print("  [OK] core.rule_generator")
        
        from core import utils
        print("  [OK] core.utils")
        
        import mcp_tools
        print("  [OK] mcp_tools")
        
        # Verificar que las funciones criticas existan
        assert hasattr(project_analyzer, 'analyze_project'), "analyze_project debe existir"
        assert hasattr(rule_generator, 'generate_rules'), "generate_rules debe existir"
        assert hasattr(utils, 'save_mdc_file'), "save_mdc_file debe existir"
        
        print("\n[OK] Todos los imports son validos")
        print("[PASS] TEST PASADO\n")
        
    except ImportError as e:
        print(f"\n[ERROR] Error de import: {e}")
        raise


async def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print("[TEST] INICIANDO SUITE DE TESTS DE RULEFORGE MCP")
    print("="*70)
    
    tests = [
        ("Validacion de estructura", test_structure_validation),
        ("Validacion de imports", test_imports),
        ("Get project path", test_get_project_path),
        ("List supported technologies", test_list_supported_technologies),
        ("Detect technology", test_detect_technology),
        ("Analyze project", test_analyze_project),
        ("Generate rules validation", test_generate_rules_validation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"\n[FAIL] TEST FALLIDO: {test_name}")
            print(f"   Error: {str(e)}")
            failed += 1
    
    # Resumen
    print("\n" + "="*70)
    print("[RESUMEN] RESUMEN DE TESTS")
    print("="*70)
    print(f"[OK] Tests pasados: {passed}/{len(tests)}")
    print(f"[FAIL] Tests fallidos: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n[SUCCESS] TODOS LOS TESTS PASARON CORRECTAMENTE!")
        print("[OK] El MCP esta listo para ser usado")
    else:
        print("\n[WARNING] Algunos tests fallaron. Revisa los errores arriba.")
    
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    print("\n[TEST] RuleForge MCP - Suite de Tests de Validacion\n")
    
    # Ejecutar tests
    success = asyncio.run(run_all_tests())
    
    # Exit code
    sys.exit(0 if success else 1)
