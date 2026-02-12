import os
import sys
import subprocess
import xml.etree.ElementTree as ET # For pom.xml parsing
import re # For version parsing
import json # For Python package detection
from .utils import load_json_file # For package.json, angular.json etc.

# Heuristics for project type detection
# Each function returns a tuple: (project_type_string_or_None, detected_details_dict)

def check_java_legacy(project_path, verbose=False):
    """Checks for indicators of a legacy Java Spring + JSP project."""
    # Indicators: WEB-INF directory, web.xml, Spring XML configs, JSP files.
    web_inf_path = os.path.join(project_path, "src", "main", "webapp", "WEB-INF")
    if not os.path.isdir(web_inf_path):
        web_inf_path = os.path.join(project_path, "WebContent", "WEB-INF") # Common in older Eclipse projects
        if not os.path.isdir(web_inf_path):
            return None, {}

    if verbose:
        print(f"Found WEB-INF directory at: {web_inf_path}")

    has_web_xml = os.path.exists(os.path.join(web_inf_path, "web.xml"))
    # Look for Spring XML files (e.g., applicationContext.xml, *-servlet.xml)
    spring_xml_present = False
    jsp_files_found = 0
    details = {"web_inf_path": web_inf_path}
    
    for root, _, files in os.walk(project_path):
        if "target" in root or "build" in root or ".git" in root or "node_modules" in root:
            continue
        for file in files:
            if file.endswith(".jsp") or file.endswith(".jspf") or file.endswith(".jspx"):
                jsp_files_found += 1
                if verbose: print(f"Found JSP file: {os.path.join(root, file)}")
                if jsp_files_found <= 3:  # Only log first few to avoid spam
                    details[f"jsp_file_{jsp_files_found}"] = os.path.join(root, file)
            if (("applicationContext.xml" in file or "spring-servlet.xml" in file or file.endswith("-context.xml")) 
                and file.endswith(".xml")):
                if verbose: print(f"Found Spring XML config: {os.path.join(root, file)}")
                spring_xml_present = True
                details["spring_xml_config"] = os.path.join(root, file)
                break
        if spring_xml_present:
            break
    
    details["jsp_files_count"] = jsp_files_found
    details["spring_xml_found"] = spring_xml_present
    
    if (has_web_xml or spring_xml_present):
        # Enhanced pom.xml parsing for Spring Framework version detection
        pom_path = os.path.join(project_path, "pom.xml")
        if os.path.exists(pom_path):
            details["is_maven"] = True
            if verbose: print("Maven project (pom.xml found).")
            
            try:
                tree = ET.parse(pom_path)
                root = tree.getroot()
                ns = {"m": "http://maven.apache.org/POM/4.0.0"}
                
                # Look for Spring Framework version in properties
                properties = root.find("m:properties", ns)
                if properties is not None:
                    # Common Spring version property names
                    spring_version_props = [
                        "spring.version", "spring-framework.version", "springframework.version",
                        "spring.framework.version", "org.springframework.version"
                    ]
                    
                    for prop_name in spring_version_props:
                        # Handle both with and without namespace prefixes
                        spring_version_elem = properties.find(f"m:{prop_name}", ns)
                        if spring_version_elem is None:
                            # Try without namespace for older POMs
                            spring_version_elem = properties.find(prop_name)
                        
                        if spring_version_elem is not None:
                            details["spring_framework_version"] = spring_version_elem.text
                            if verbose: print(f"Spring Framework version found in properties: {spring_version_elem.text}")
                            break
                
                # Look for Spring dependencies to determine version if not in properties
                dependencies = root.find("m:dependencies", ns)
                if dependencies is not None:
                    spring_version_from_deps = None
                    uses_spring_security = False
                    uses_spring_webmvc = False
                    uses_spring_orm = False
                    uses_hibernate = False
                    uses_struts = False
                    
                    for dep in dependencies.findall("m:dependency", ns):
                        groupId = dep.find("m:groupId", ns)
                        artifactId = dep.find("m:artifactId", ns)
                        version = dep.find("m:version", ns)
                        
                        if groupId is not None and artifactId is not None:
                            group_text = groupId.text
                            artifact_text = artifactId.text
                            version_text = version.text if version is not None else None
                            
                            # Spring Framework core dependencies
                            if group_text == "org.springframework":
                                if not spring_version_from_deps and version_text:
                                    spring_version_from_deps = version_text
                                    details["spring_framework_version"] = version_text
                                    if verbose: print(f"Spring Framework version found in dependency: {version_text}")
                                
                                # Specific Spring modules detection
                                if "spring-security" in artifact_text:
                                    uses_spring_security = True
                                elif "spring-webmvc" in artifact_text:
                                    uses_spring_webmvc = True
                                elif "spring-orm" in artifact_text:
                                    uses_spring_orm = True
                            
                            # Hibernate detection (common in legacy projects)
                            elif group_text == "org.hibernate" and "hibernate" in artifact_text:
                                uses_hibernate = True
                                if version_text:
                                    details["hibernate_version"] = version_text
                                    if verbose: print(f"Hibernate version detected: {version_text}")
                            
                            # Struts detection (high security risk)
                            elif group_text == "org.apache.struts" or "struts" in artifact_text:
                                uses_struts = True
                                if version_text:
                                    details["struts_version"] = version_text
                                    details["struts_security_risk"] = True
                                    if verbose: print(f"Struts version detected: {version_text} - HIGH SECURITY RISK")
                            
                            # Legacy logging frameworks
                            elif group_text == "log4j" and "log4j" in artifact_text:
                                details["uses_log4j"] = True
                                details["log4j_version"] = version_text
                                if version_text and version_text.startswith("1."):
                                    details["log4j_security_risk"] = True
                                    if verbose: print(f"Log4j 1.x detected: {version_text} - SECURITY RISK")
                            
                            # Database drivers
                            elif group_text == "mysql" and "mysql-connector" in artifact_text:
                                details["database_mysql"] = True
                            elif group_text == "oracle" and "ojdbc" in artifact_text:
                                details["database_oracle"] = True
                            elif group_text == "com.microsoft.sqlserver" and "mssql-jdbc" in artifact_text:
                                details["database_sqlserver"] = True
                    
                    # Set technology flags
                    details["uses_spring_security"] = uses_spring_security
                    details["uses_spring_webmvc"] = uses_spring_webmvc
                    details["uses_spring_orm"] = uses_spring_orm
                    details["uses_hibernate"] = uses_hibernate
                    details["uses_struts"] = uses_struts
                
                # Analyze Spring Framework version for security assessment
                spring_version = details.get("spring_framework_version")
                if spring_version:
                    version_match = re.search(r'(\d+)\.(\d+)', spring_version)
                    if version_match:
                        major_version = int(version_match.group(1))
                        minor_version = int(version_match.group(2))
                        details["spring_major_version"] = major_version
                        details["spring_minor_version"] = minor_version
                        
                        # Security risk assessment based on version
                        if major_version == 1 or (major_version == 2 and minor_version < 5):
                            details["security_priority"] = "critical"
                            details["is_very_legacy"] = True
                            if verbose: print(f"Spring Framework {major_version}.{minor_version} - CRITICAL security risk (very legacy)")
                        elif major_version == 2 or (major_version == 3 and minor_version < 2):
                            details["security_priority"] = "high"
                            details["is_legacy"] = True
                            if verbose: print(f"Spring Framework {major_version}.{minor_version} - HIGH security risk (legacy)")
                        elif major_version == 3:
                            details["security_priority"] = "medium"
                            details["is_old"] = True
                            if verbose: print(f"Spring Framework {major_version}.{minor_version} - MEDIUM security risk (old)")
                        else:
                            details["security_priority"] = "low"
                            if verbose: print(f"Spring Framework {major_version}.{minor_version} - Lower security risk")
                
            except ET.ParseError:
                if verbose: print(f"Error parsing pom.xml at {pom_path}")
            except Exception as e:
                if verbose: print(f"An unexpected error occurred parsing pom.xml: {e}")
        
        # Check for Gradle build files (less common in legacy projects but possible)
        gradle_path = os.path.join(project_path, "build.gradle")
        if os.path.exists(gradle_path):
            details["is_gradle"] = True
            if verbose: print("Gradle project (build.gradle found).")
            
            try:
                with open(gradle_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple regex to find Spring version in Gradle files
                    spring_version_match = re.search(r'springframework[\'"]:\s*[\'"]([0-9.]+)', content)
                    if spring_version_match:
                        details["spring_framework_version"] = spring_version_match.group(1)
                        if verbose: print(f"Spring Framework version found in build.gradle: {spring_version_match.group(1)}")
            except Exception as e:
                if verbose: print(f"Error reading build.gradle: {e}")
        
        # Check web.xml for servlet version (indicates how legacy the project is)
        if has_web_xml:
            try:
                web_xml_path = os.path.join(web_inf_path, "web.xml")
                tree = ET.parse(web_xml_path)
                root = tree.getroot()
                
                # Check web-app version attribute
                version_attr = root.get("version")
                if version_attr:
                    details["servlet_version"] = version_attr
                    servlet_version = float(version_attr)
                    if servlet_version < 2.5:
                        details["servlet_very_legacy"] = True
                        if verbose: print(f"Servlet API {version_attr} - VERY LEGACY")
                    elif servlet_version < 3.0:
                        details["servlet_legacy"] = True
                        if verbose: print(f"Servlet API {version_attr} - LEGACY")
                    
            except Exception as e:
                if verbose: print(f"Error parsing web.xml: {e}")
        
        return "java_legacy_spring", details
    return None, {}

def check_spring_boot(project_path, verbose=False):
    """Checks for indicators of a Spring Boot project."""
    pom_path = os.path.join(project_path, "pom.xml")
    gradle_path = os.path.join(project_path, "build.gradle")
    application_props_main = os.path.join(project_path, "src", "main", "resources", "application.properties")
    application_yml_main = os.path.join(project_path, "src", "main", "resources", "application.yml")
    application_yaml_main = os.path.join(project_path, "src", "main", "resources", "application.yaml")
    details = {}

    if os.path.exists(pom_path):
        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            
            parent = root.find("m:parent", ns)
            if parent is not None:
                artifactId = parent.find("m:artifactId", ns)
                if artifactId is not None and artifactId.text == "spring-boot-starter-parent":
                    version_tag = parent.find("m:version", ns)
                    if version_tag is not None:
                        details["spring_boot_version"] = version_tag.text
                        
                        # Parse version to detect major version
                        import re
                        version_match = re.search(r'(\d+)', version_tag.text)
                        if version_match:
                            major_version = int(version_match.group(1))
                            details["spring_boot_major_version"] = major_version
                            
                            if major_version == 1:
                                details["is_legacy"] = True
                                details["security_priority"] = "high"
                                if verbose: print(f"Spring Boot {major_version} detected - LEGACY version with security concerns.")
                            elif major_version == 2:
                                details["is_modern"] = True
                                details["security_priority"] = "medium"
                                if verbose: print(f"Spring Boot {major_version} detected - Modern stable version.")
                            elif major_version >= 3:
                                details["is_latest"] = True
                                details["requires_java17"] = True
                                details["security_priority"] = "low"
                                if verbose: print(f"Spring Boot {major_version} detected - Latest version with Java 17+ requirement.")
                    
                    if verbose: print(f"Spring Boot parent found in pom.xml. Version: {details.get('spring_boot_version', 'N/A')}")
                    
                    # Check for specific Spring dependencies
                    dependencies = root.find("m:dependencies", ns)
                    if dependencies is not None:
                        for dep in dependencies.findall("m:dependency", ns):
                            groupId = dep.find("m:groupId", ns)
                            artifactId = dep.find("m:artifactId", ns)
                            
                            if groupId is not None and artifactId is not None:
                                group_text = groupId.text
                                artifact_text = artifactId.text
                                
                                # Spring Security detection
                                if group_text == "org.springframework.boot" and artifact_text == "spring-boot-starter-security":
                                    details["uses_spring_security"] = True
                                    if verbose: print("Spring Security detected.")
                                
                                # Spring Data JPA detection
                                elif group_text == "org.springframework.boot" and artifact_text == "spring-boot-starter-data-jpa":
                                    details["uses_spring_data_jpa"] = True
                                    if verbose: print("Spring Data JPA detected.")
                                
                                # Spring Boot Actuator detection
                                elif group_text == "org.springframework.boot" and artifact_text == "spring-boot-starter-actuator":
                                    details["uses_actuator"] = True
                                    if verbose: print("Spring Boot Actuator detected - SECURITY RISK if not secured.")
                                
                                # Spring WebFlux (Reactive) detection
                                elif group_text == "org.springframework.boot" and artifact_text == "spring-boot-starter-webflux":
                                    details["uses_webflux"] = True
                                    if verbose: print("Spring WebFlux (Reactive) detected.")
                                
                                # Spring Cloud detection
                                elif group_text and "org.springframework.cloud" in group_text:
                                    details["uses_spring_cloud"] = True
                                    if verbose: print("Spring Cloud dependency detected.")
                                
                                # Database drivers detection for security analysis
                                elif group_text == "mysql" and "mysql-connector" in artifact_text:
                                    details["database_mysql"] = True
                                elif group_text == "org.postgresql" and "postgresql" in artifact_text:
                                    details["database_postgresql"] = True
                                elif group_text == "com.h2database" and "h2" in artifact_text:
                                    details["database_h2"] = True
                                    details["h2_console_risk"] = True
                                    if verbose: print("H2 Database detected - SECURITY RISK if H2 console enabled in production.")
                    
                    return "springboot", details
            
            # Check dependencies for spring-boot artifacts
            dependencies = root.find("m:dependencies", ns)
            if dependencies is not None:
                for dep in dependencies.findall("m:dependency", ns):
                    groupId = dep.find("m:groupId", ns)
                    artifactId = dep.find("m:artifactId", ns)
                    if groupId is not None and groupId.text == "org.springframework.boot" and \
                       artifactId is not None and "spring-boot-starter" in artifactId.text:
                        if verbose: print(f"Spring Boot starter dependency found in pom.xml: {artifactId.text}")
                        # Try to get version from properties if not in parent
                        if "spring_boot_version" not in details:
                            properties = root.find("m:properties", ns)
                            if properties is not None:
                                spring_boot_version_prop = properties.find("m:spring-boot.version", ns) # Common property name
                                if spring_boot_version_prop is not None:
                                     details["spring_boot_version"] = spring_boot_version_prop.text
                        return "springboot", details

        except ET.ParseError:
            if verbose: print(f"Error parsing pom.xml at {pom_path}")
        except Exception as e:
            if verbose: print(f"An unexpected error occurred parsing pom.xml: {e}")

    if os.path.exists(gradle_path):
        try:
            with open(gradle_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "org.springframework.boot" in content or "spring-boot-gradle-plugin" in content:
                    if verbose: print("Spring Boot Gradle plugin detected.")
                    # Could try to extract version from gradle if needed
                    return "springboot", details
        except Exception as e:
            if verbose: print(f"Error reading or parsing build.gradle: {e}")

    if (os.path.exists(application_props_main) or 
        os.path.exists(application_yml_main) or 
        os.path.exists(application_yaml_main)):
        if verbose: print("Found Spring Boot application.(properties/yml/yaml)")
        # This is a weaker indicator alone, but can confirm if pom/gradle check wasn't definitive
        # or if those files are missing but it's still a Boot app (e.g. non-standard structure)
        return "springboot", details # Return if found, even if pom/gradle check was inconclusive

    # Check for @SpringBootApplication (more advanced, requires file parsing)
    # For now, rely on build files and application config files.

    return None, {}

def check_angular(project_path, verbose=False):
    """Checks for indicators of an Angular project."""
    angular_json_path = os.path.join(project_path, "angular.json")
    package_json_path = os.path.join(project_path, "package.json") 
    details = {}

    if os.path.exists(angular_json_path):
        if verbose: print("Found angular.json.")
        data = load_json_file(angular_json_path)
        if data and isinstance(data.get("projects"), dict):
            # Try to get project name and version if possible
            # Angular CLI stores projects under the "projects" key
            # The actual app name might be one of the keys in `data["projects"]`
            # This is a strong indicator.
            details["angular_cli_version"] = data.get("$schema", "").split("/")[-1].replace(".json","") # Heuristic
            
            # Detect Angular CLI version from schema
            schema = data.get("$schema", "")
            if "15" in schema or "16" in schema or "17" in schema or "18" in schema:
                details["angular_cli_modern"] = True

    if os.path.exists(package_json_path):
        data = load_json_file(package_json_path)
        if data:
            dependencies = data.get("dependencies", {})
            dev_dependencies = data.get("devDependencies", {})
            if "@angular/core" in dependencies or "@angular/core" in dev_dependencies:
                if verbose: print("Found @angular/core in package.json.")
                angular_version = dependencies.get("@angular/core") or dev_dependencies.get("@angular/core")
                details["angular_core_version"] = angular_version
                
                # Parse version to detect major version
                import re
                version_match = re.search(r'(\d+)', angular_version)
                if version_match:
                    major_version = int(version_match.group(1))
                    details["angular_major_version"] = major_version
                    
                    if major_version >= 14:
                        details["supports_standalone"] = True
                        if verbose: print(f"Angular {major_version} supports standalone components.")
                    
                    if major_version >= 16:
                        details["supports_signals"] = True
                        if verbose: print(f"Angular {major_version} supports signals.")
                    
                    if major_version >= 17:
                        details["new_control_flow"] = True
                        if verbose: print(f"Angular {major_version} has new control flow syntax.")
                
                # Check for specific Angular features in dependencies
                if "@angular/material" in dependencies or "@angular/material" in dev_dependencies:
                    details["uses_angular_material"] = True
                
                if "@ngrx/store" in dependencies or "@ngrx/store" in dev_dependencies:
                    details["uses_ngrx"] = True
                
                if "@angular/pwa" in dependencies or "@angular/pwa" in dev_dependencies:
                    details["is_pwa"] = True
                
                # Check for SSR
                if "@nguniversal/express-engine" in dependencies or "@angular/ssr" in dependencies:
                    details["has_ssr"] = True
                
                return "angular", details
    
    return None, {}

def check_vue(project_path, verbose=False):
    """Checks for indicators of a Vue.js project."""
    package_json_path = os.path.join(project_path, "package.json")
    vue_config_js_path = os.path.join(project_path, "vue.config.js")
    vite_config_js_path = os.path.join(project_path, "vite.config.js") # Vue 3 with Vite
    nuxt_config_js_path = os.path.join(project_path, "nuxt.config.js") # Nuxt.js (Vue framework)
    details = {}

    if os.path.exists(package_json_path):
        data = load_json_file(package_json_path)
        if data:
            dependencies = data.get("dependencies", {})
            dev_dependencies = data.get("devDependencies", {})
            if "vue" in dependencies or "vue" in dev_dependencies:
                if verbose: print("Found 'vue' in package.json.")
                details["vue_version"] = dependencies.get("vue") or dev_dependencies.get("vue")
                if "nuxt" in dependencies or "nuxt" in dev_dependencies:
                    details["is_nuxt"] = True
                    if verbose: print("Nuxt detected.")
                return "vue", details
    
    if os.path.exists(vue_config_js_path) or os.path.exists(vite_config_js_path) or os.path.exists(nuxt_config_js_path):
        if verbose: print("Found vue.config.js, vite.config.js, or nuxt.config.js.")
        # This is a good secondary indicator if package.json wasn't conclusive or is missing vue dep for some reason
        return "vue", details
    
    # Check for .vue files (more intensive)
    for root, _, files in os.walk(project_path):
        if "node_modules" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".vue"):
                if verbose: print(f"Found .vue file: {os.path.join(root, file)}")
                return "vue", details
    return None, {}

def check_gitlab_ci(project_path, verbose=False):
    """Checks for a GitLab CI file."""
    gitlab_ci_yml_path = os.path.join(project_path, ".gitlab-ci.yml")
    if os.path.exists(gitlab_ci_yml_path):
        if verbose: print("Found .gitlab-ci.yml.")
        return "gitlab_ci", {}
    return None, {}


def detect_python_version(project_path, verbose=False):
    """
    Detecta la versión de Python y su ruta de instalación.
    
    Estrategia de detección (en orden de prioridad):
    1. Entorno virtual del proyecto (.venv/, venv/, env/)
    2. Archivos de configuración (pyproject.toml, Pipfile, .python-version)
    3. Intérprete del sistema (python/python3)
    
    Args:
        project_path: Ruta al proyecto
        verbose: Si True, muestra información detallada
        
    Returns:
        Dict con información de versión de Python
    """
    details = {}
    
    # Determinar el sufijo del ejecutable según el sistema operativo
    is_windows = sys.platform == 'win32'
    python_exe = 'python.exe' if is_windows else 'python'
    bin_dir = 'Scripts' if is_windows else 'bin'
    
    # 1. Buscar entorno virtual local
    venv_paths = ['.venv', 'venv', 'env', '.env']
    for venv_name in venv_paths:
        venv_dir = os.path.join(project_path, venv_name)
        venv_python = os.path.join(venv_dir, bin_dir, python_exe)
        
        # En Windows también puede ser solo 'python' sin .exe
        if not os.path.exists(venv_python) and is_windows:
            venv_python = os.path.join(venv_dir, bin_dir, 'python')
        
        if os.path.exists(venv_python):
            if verbose:
                print(f"Entorno virtual encontrado: {venv_dir}")
            
            try:
                # Ejecutar python --version para obtener la versión
                result = subprocess.run(
                    [venv_python, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=False
                )
                
                if result.returncode == 0:
                    version_output = result.stdout.strip() or result.stderr.strip()
                    # Parsear "Python 3.11.5" -> "3.11.5"
                    version_match = re.search(r'Python\s+(\d+\.\d+\.?\d*)', version_output)
                    if version_match:
                        full_version = version_match.group(1)
                        details["python_version"] = full_version
                        details["python_path"] = os.path.abspath(venv_python)
                        details["python_source"] = "venv"
                        details["is_venv"] = True
                        details["venv_path"] = os.path.abspath(venv_dir)
                        
                        # Parsear versión major y minor
                        version_parts = full_version.split('.')
                        if len(version_parts) >= 1:
                            details["python_major_version"] = int(version_parts[0])
                        if len(version_parts) >= 2:
                            details["python_minor_version"] = int(version_parts[1])
                        
                        if verbose:
                            print(f"Python {full_version} detectado en venv: {venv_python}")
                        
                        return details
                        
            except subprocess.TimeoutExpired:
                if verbose:
                    print(f"Timeout al ejecutar Python en venv: {venv_python}")
            except Exception as e:
                if verbose:
                    print(f"Error al detectar versión de Python en venv: {e}")
    
    # 2. Parsear archivos de configuración del proyecto
    
    # 2.1 Archivo .python-version (pyenv)
    python_version_file = os.path.join(project_path, ".python-version")
    if os.path.exists(python_version_file):
        try:
            with open(python_version_file, 'r', encoding='utf-8') as f:
                version_content = f.read().strip()
                # Puede ser "3.11.5" o "3.11" o incluso "pypy3.9-7.3.9"
                version_match = re.search(r'^(\d+\.\d+\.?\d*)', version_content)
                if version_match:
                    full_version = version_match.group(1)
                    details["python_version"] = full_version
                    details["python_source"] = "pyenv"
                    details["is_venv"] = False
                    
                    version_parts = full_version.split('.')
                    if len(version_parts) >= 1:
                        details["python_major_version"] = int(version_parts[0])
                    if len(version_parts) >= 2:
                        details["python_minor_version"] = int(version_parts[1])
                    
                    if verbose:
                        print(f"Python {full_version} detectado en .python-version")
                    
                    return details
                    
        except Exception as e:
            if verbose:
                print(f"Error leyendo .python-version: {e}")
    
    # 2.2 pyproject.toml - campo requires-python
    pyproject_path = os.path.join(project_path, "pyproject.toml")
    if os.path.exists(pyproject_path):
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Buscar requires-python = ">=3.8" o python = "^3.9"
                requires_match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
                if not requires_match:
                    # Poetry usa python = "^3.9" en [tool.poetry.dependencies]
                    requires_match = re.search(r'\[tool\.poetry\.dependencies\][^\[]*python\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
                
                if requires_match:
                    version_spec = requires_match.group(1)
                    # Extraer versión de especificadores como ">=3.8", "^3.9", "~3.10"
                    version_match = re.search(r'(\d+\.\d+\.?\d*)', version_spec)
                    if version_match:
                        full_version = version_match.group(1)
                        details["python_version_required"] = version_spec
                        details["python_version"] = full_version
                        details["python_source"] = "pyproject"
                        details["is_venv"] = False
                        
                        version_parts = full_version.split('.')
                        if len(version_parts) >= 1:
                            details["python_major_version"] = int(version_parts[0])
                        if len(version_parts) >= 2:
                            details["python_minor_version"] = int(version_parts[1])
                        
                        if verbose:
                            print(f"Python {full_version} requerido en pyproject.toml ({version_spec})")
                        
                        return details
                        
        except Exception as e:
            if verbose:
                print(f"Error leyendo pyproject.toml: {e}")
    
    # 2.3 Pipfile - sección [requires] con python_version
    pipfile_path = os.path.join(project_path, "Pipfile")
    if os.path.exists(pipfile_path):
        try:
            with open(pipfile_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Buscar python_version = "3.9" en sección [requires]
                requires_section = re.search(r'\[requires\][^\[]*python_version\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
                if requires_section:
                    full_version = requires_section.group(1)
                    details["python_version"] = full_version
                    details["python_source"] = "pipfile"
                    details["is_venv"] = False
                    
                    version_parts = full_version.split('.')
                    if len(version_parts) >= 1:
                        details["python_major_version"] = int(version_parts[0])
                    if len(version_parts) >= 2:
                        details["python_minor_version"] = int(version_parts[1])
                    
                    if verbose:
                        print(f"Python {full_version} requerido en Pipfile")
                    
                    return details
                    
        except Exception as e:
            if verbose:
                print(f"Error leyendo Pipfile: {e}")
    
    # 2.4 setup.py - campo python_requires
    setup_py_path = os.path.join(project_path, "setup.py")
    if os.path.exists(setup_py_path):
        try:
            with open(setup_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Buscar python_requires='>=3.7'
                requires_match = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', content)
                if requires_match:
                    version_spec = requires_match.group(1)
                    version_match = re.search(r'(\d+\.\d+\.?\d*)', version_spec)
                    if version_match:
                        full_version = version_match.group(1)
                        details["python_version_required"] = version_spec
                        details["python_version"] = full_version
                        details["python_source"] = "setup.py"
                        details["is_venv"] = False
                        
                        version_parts = full_version.split('.')
                        if len(version_parts) >= 1:
                            details["python_major_version"] = int(version_parts[0])
                        if len(version_parts) >= 2:
                            details["python_minor_version"] = int(version_parts[1])
                        
                        if verbose:
                            print(f"Python {full_version} requerido en setup.py ({version_spec})")
                        
                        return details
                        
        except Exception as e:
            if verbose:
                print(f"Error leyendo setup.py: {e}")
    
    # 3. Fallback: Intérprete del sistema
    python_commands = ['python3', 'python'] if not is_windows else ['python', 'python3']
    
    for python_cmd in python_commands:
        try:
            # Obtener versión
            result = subprocess.run(
                [python_cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=False
            )
            
            if result.returncode == 0:
                version_output = result.stdout.strip() or result.stderr.strip()
                version_match = re.search(r'Python\s+(\d+\.\d+\.?\d*)', version_output)
                
                if version_match:
                    full_version = version_match.group(1)
                    
                    # Obtener ruta del ejecutable
                    which_cmd = 'where' if is_windows else 'which'
                    path_result = subprocess.run(
                        [which_cmd, python_cmd],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        shell=False
                    )
                    
                    python_path = None
                    if path_result.returncode == 0:
                        # En Windows, 'where' puede devolver múltiples líneas
                        python_path = path_result.stdout.strip().split('\n')[0].strip()
                    
                    details["python_version"] = full_version
                    details["python_path"] = python_path if python_path else python_cmd
                    details["python_source"] = "system"
                    details["is_venv"] = False
                    
                    version_parts = full_version.split('.')
                    if len(version_parts) >= 1:
                        details["python_major_version"] = int(version_parts[0])
                    if len(version_parts) >= 2:
                        details["python_minor_version"] = int(version_parts[1])
                    
                    if verbose:
                        print(f"Python {full_version} detectado en sistema: {details['python_path']}")
                    
                    return details
                    
        except subprocess.TimeoutExpired:
            if verbose:
                print(f"Timeout al ejecutar {python_cmd}")
        except FileNotFoundError:
            if verbose:
                print(f"Comando {python_cmd} no encontrado")
        except Exception as e:
            if verbose:
                print(f"Error al detectar Python del sistema con {python_cmd}: {e}")
    
    if verbose:
        print("No se pudo detectar la versión de Python")
    
    return details


def check_python(project_path, verbose=False):
    """Checks for indicators of a Python project."""
    details = {}
    
    # Check for common Python files and directories
    indicators = [
        "requirements.txt", "setup.py", "pyproject.toml", 
        "Pipfile", "poetry.lock", "manage.py", "app.py", "main.py"
    ]
    
    found_indicators = []
    for indicator in indicators:
        if os.path.exists(os.path.join(project_path, indicator)):
            found_indicators.append(indicator)
    
    if not found_indicators:
        # Check for .py files in root or common directories
        python_files_found = 0
        for root, dirs, files in os.walk(project_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in ['venv', '.venv', 'env', '__pycache__', '.git', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files_found += 1
                    if python_files_found >= 3:  # If we find 3+ Python files, likely a Python project
                        break
            if python_files_found >= 3:
                break
        
        if python_files_found < 3:
            return None, {}
    
    if verbose and found_indicators:
        print(f"Python project indicators found: {', '.join(found_indicators)}")
    
    details["python_indicators"] = found_indicators
    
    # Detect Python frameworks and libraries
    frameworks_detected = []
    
    # Check for Django
    if "manage.py" in found_indicators:
        frameworks_detected.append("Django")
        details["is_django"] = True
        if verbose: print("Django project detected (manage.py found)")
        
        # Look for Django settings
        for root, dirs, files in os.walk(project_path):
            if 'settings.py' in files:
                details["django_settings_path"] = os.path.join(root, 'settings.py')
                if verbose: print(f"Django settings found at: {os.path.join(root, 'settings.py')}")
                
                # Try to read settings for version detection
                try:
                    with open(os.path.join(root, 'settings.py'), 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'DEBUG = True' in content:
                            details["debug_enabled"] = True
                            if verbose: print("WARNING: DEBUG=True found in settings")
                        
                        # Check for database configuration
                        if 'sqlite3' in content:
                            details["database_sqlite"] = True
                        elif 'postgresql' in content or 'psycopg' in content:
                            details["database_postgresql"] = True
                        elif 'mysql' in content:
                            details["database_mysql"] = True
                        
                        # Check for SECRET_KEY
                        if re.search(r"SECRET_KEY\s*=\s*['\"][\w\-]+['\"]", content):
                            details["hardcoded_secret_key"] = True
                            if verbose: print("WARNING: Hardcoded SECRET_KEY detected")
                            
                except Exception as e:
                    if verbose: print(f"Error reading settings.py: {e}")
                break
    
    # Check for Flask
    if "app.py" in found_indicators:
        # Additional check to confirm it's Flask
        try:
            with open(os.path.join(project_path, "app.py"), 'r', encoding='utf-8') as f:
                content = f.read()
                if 'from flask import' in content or 'import flask' in content:
                    frameworks_detected.append("Flask")
                    details["is_flask"] = True
                    if verbose: print("Flask project detected")
                    
                    # Check for debug mode
                    if 'debug=True' in content or 'app.debug = True' in content:
                        details["debug_enabled"] = True
                        if verbose: print("WARNING: Flask debug mode enabled")
        except Exception as e:
            if verbose: print(f"Error reading app.py: {e}")
    
    # Check for FastAPI
    if "main.py" in found_indicators:
        try:
            with open(os.path.join(project_path, "main.py"), 'r', encoding='utf-8') as f:
                content = f.read()
                if 'from fastapi import' in content or 'import fastapi' in content:
                    frameworks_detected.append("FastAPI")
                    details["is_fastapi"] = True
                    if verbose: print("FastAPI project detected")
        except Exception as e:
            if verbose: print(f"Error reading main.py: {e}")
    
    # Parse requirements.txt for dependencies and versions
    if "requirements.txt" in found_indicators:
        try:
            with open(os.path.join(project_path, "requirements.txt"), 'r', encoding='utf-8') as f:
                content = f.read()
                requirements = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        requirements.append(line)
                
                details["requirements"] = requirements
                if verbose: print(f"Found {len(requirements)} requirements")
                
                # Check for specific risky dependencies
                risky_packages = []
                for req in requirements:
                    req_lower = req.lower()
                    if 'django==' in req_lower:
                        version_match = re.search(r'django==([0-9.]+)', req_lower)
                        if version_match:
                            details["django_version"] = version_match.group(1)
                    elif 'flask==' in req_lower:
                        version_match = re.search(r'flask==([0-9.]+)', req_lower)
                        if version_match:
                            details["flask_version"] = version_match.group(1)
                    elif 'fastapi==' in req_lower:
                        version_match = re.search(r'fastapi==([0-9.]+)', req_lower)
                        if version_match:
                            details["fastapi_version"] = version_match.group(1)
                    elif any(risky in req_lower for risky in ['pycrypto', 'md5', 'pickle']):
                        risky_packages.append(req)
                
                if risky_packages:
                    details["risky_packages"] = risky_packages
                    if verbose: print(f"WARNING: Risky packages detected: {risky_packages}")
                        
        except Exception as e:
            if verbose: print(f"Error reading requirements.txt: {e}")
    
    # Parse pyproject.toml for Poetry projects
    if "pyproject.toml" in found_indicators:
        try:
            with open(os.path.join(project_path, "pyproject.toml"), 'r', encoding='utf-8') as f:
                content = f.read()
                details["is_poetry"] = True
                if verbose: print("Poetry project detected (pyproject.toml found)")
                
                # Simple regex to extract dependencies (basic implementation)
                django_match = re.search(r'django\s*=\s*"([^"]+)"', content, re.IGNORECASE)
                if django_match:
                    details["django_version"] = django_match.group(1)
                    if "Django" not in frameworks_detected:
                        frameworks_detected.append("Django")
                        details["is_django"] = True
                        
        except Exception as e:
            if verbose: print(f"Error reading pyproject.toml: {e}")
    
    # Parse Pipfile for Pipenv projects  
    if "Pipfile" in found_indicators:
        try:
            with open(os.path.join(project_path, "Pipfile"), 'r', encoding='utf-8') as f:
                content = f.read()
                details["is_pipenv"] = True
                if verbose: print("Pipenv project detected (Pipfile found)")
                
                # Check for Django in Pipfile
                if 'django' in content.lower():
                    if "Django" not in frameworks_detected:
                        frameworks_detected.append("Django")
                        details["is_django"] = True
                        
        except Exception as e:
            if verbose: print(f"Error reading Pipfile: {e}")
    
    # Check for common Python web server configurations
    wsgi_files = ["wsgi.py", "asgi.py"]
    for wsgi_file in wsgi_files:
        if os.path.exists(os.path.join(project_path, wsgi_file)):
            details[f"has_{wsgi_file.split('.')[0]}"] = True
            if verbose: print(f"WSGI/ASGI configuration found: {wsgi_file}")
    
    # Check for testing frameworks
    test_files = ["pytest.ini", "tox.ini", "conftest.py"]
    for test_file in test_files:
        if os.path.exists(os.path.join(project_path, test_file)):
            details[f"has_{test_file.split('.')[0]}"] = True
            if verbose: print(f"Testing configuration found: {test_file}")
    
    # Check for Docker
    if os.path.exists(os.path.join(project_path, "Dockerfile")):
        details["has_docker"] = True
        if verbose: print("Docker configuration found")
    
    details["frameworks_detected"] = frameworks_detected
    if verbose and frameworks_detected:
        print(f"Python frameworks detected: {', '.join(frameworks_detected)}")
    
    # Detectar versión de Python y ruta
    python_version_info = detect_python_version(project_path, verbose)
    if python_version_info:
        details.update(python_version_info)
        if verbose and python_version_info.get("python_version"):
            source = python_version_info.get("python_source", "unknown")
            version = python_version_info.get("python_version")
            path = python_version_info.get("python_path", "N/A")
            print(f"Python version detected: {version} (source: {source}, path: {path})")
    
    # Determine security priority based on findings
    security_priority = "low"
    if details.get("debug_enabled"):
        security_priority = "high"
    elif details.get("hardcoded_secret_key") or details.get("risky_packages"):
        security_priority = "medium"
    
    details["security_priority"] = security_priority
    
    return "python", details

# List of checker functions. Order can matter if a project might match multiple types.
# More specific checks should ideally come before more generic ones if there's overlap potential.
PROJECT_CHECKERS = [
    check_spring_boot,      # More specific Java (uses pom.xml, specific starters)
    check_java_legacy,      # General Java Web App with Spring indications
    check_angular,          # Uses angular.json or @angular/core
    check_vue,              # Uses vue in package.json or .vue files
    check_python,           # Checks for Python project indicators
    check_gitlab_ci,        # Just checks for the .gitlab-ci.yml file (could be part of any project)
]

def analyze_project(project_path, verbose=False):
    """Analyzes the project at the given path to determine its type and technologies."""
    if not os.path.isdir(project_path):
        if verbose: print(f"Error: Project path {project_path} is not a directory.")
        return None, {}

    if verbose:
        print(f"Starting project analysis for: {project_path}")

    # For GitLab CI, it can coexist with other project types. 
    # We should run its check independently and potentially merge results or offer multiple rule sets.
    # For now, if gitlab-ci.yml is found, it will be one of the types. 
    # The main loop will find the *first* matching primary project type.
    
    detected_project_type = None
    detected_technologies = {}

    for checker_func in PROJECT_CHECKERS:
        try:
            project_type, tech_details = checker_func(project_path, verbose)
            if project_type:
                if verbose: 
                    print(f"Checker '{checker_func.__name__}' identified project type: {project_type} with details: {tech_details}")
                # First primary type found wins for now. 
                # GitLab CI is special, if we want it to be additive, logic needs adjustment.
                # Current setup: if check_gitlab_ci is before others and finds it, it might return 'gitlab_ci' as the primary type.
                # Order in PROJECT_CHECKERS matters.
                detected_project_type = project_type
                detected_technologies.update(tech_details) # Merge details, though only first type is returned
                break # Stop at first match
        except Exception as e:
            if verbose:
                print(f"Error during project analysis with {checker_func.__name__}: {e}")
    
    # Special handling for gitlab_ci: it can be a standalone type or complementary.
    # If another type was detected, we still check for gitlab_ci and add its rules if requested via --type
    # or if we decide to support generating multiple rule files or a merged one.
    # For now, the main CLI loop handles --type. If not specified, only the first detected type is used.
    # The current PROJECT_CHECKERS order might make gitlab_ci a primary type if its file is found and it's checked early.
    # Consider making gitlab_ci detection separate if it's always additive.

    if detected_project_type:
        if verbose: print(f"Analysis complete. Final detected type: {detected_project_type}, Tech: {detected_technologies}")
        return detected_project_type, detected_technologies
    else:
        if verbose: print("Analysis complete. No specific project type conclusively identified.")
        return None, {} 