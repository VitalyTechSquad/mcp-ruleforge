import os
import re
from .utils import load_mdc_file

# Define the path to the templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")

PROJECT_TYPES_TEMPLATES = {
    "java_legacy_spring": "java_legacy_spring.mdc",
    "springboot": "spring_boot.mdc",
    "angular": "angular.mdc",
    "vue": "vue.mdc",
    "python": "python.mdc",
    "gitlab_ci": "gitlab_ci.mdc",
}

class RuleSet:
    """Base class for a set of rules."""
    def __init__(self, project_type, detected_tech=None, custom_rules_data=None, verbose=False):
        self.project_type = project_type
        self.detected_tech = detected_tech if detected_tech else {}
        self.custom_rules_data = custom_rules_data if custom_rules_data else {}
        self.verbose = verbose
        self.rules = "" # Rules will be a raw string

    def _load_base_template(self):
        """Loads the base template content for the project type."""
        template_filename = PROJECT_TYPES_TEMPLATES.get(self.project_type)
        if not template_filename:
            if self.verbose:
                print(f"Warning: No template found for project type '{self.project_type}'.")
            return {"frontmatter": None, "content": ""}
        
        template_path = os.path.join(TEMPLATES_DIR, template_filename)
        base_rules_data = load_mdc_file(template_path)
        if not base_rules_data:
            if self.verbose:
                print(f"Warning: Could not load template file: {template_path}")
            return {"frontmatter": None, "content": ""}
        if self.verbose:
            print(f"Successfully loaded base template: {template_path}")
        return base_rules_data

    def _adapt_rules_for_angular(self, content):
        """Adapts Angular rules based on detected version and features."""
        adaptations = []
        
        major_version = self.detected_tech.get("angular_major_version")
        if major_version:
            adaptations.append(f"\n# Detectado: Angular {major_version}")
            
            # Add version-specific symbols and find patterns
            if self.detected_tech.get("supports_standalone"):
                adaptations.append("""
# Símbolos específicos para Angular 14+
symbols:
  - label: "bootstrapApplication"
    description: "Función para bootstrap de standalone applications (Angular 14+)."
  - label: "@Component (standalone: true)"
    description: "Componentes standalone que no requieren NgModule."
""")
            
            if self.detected_tech.get("supports_signals"):
                adaptations.append("""
# Símbolos específicos para Angular 16+
symbols:
  - label: "signal()"
    description: "API de signals para gestión de estado reactivo (Angular 16+)."
  - label: "computed()"
    description: "Valores computados basados en signals (Angular 16+)."
  - label: "effect()"
    description: "Efectos secundarios basados en signals (Angular 16+)."
""")
            
            if self.detected_tech.get("new_control_flow"):
                adaptations.append("""
# Símbolos específicos para Angular 17+
symbols:
  - label: "@if"
    description: "Nueva sintaxis de control de flujo para condicionales (Angular 17+)."
  - label: "@for"
    description: "Nueva sintaxis de control de flujo para bucles (Angular 17+)."
  - label: "@switch"
    description: "Nueva sintaxis de control de flujo para switch statements (Angular 17+)."
""")
        
        # Add feature-specific adaptations
        if self.detected_tech.get("uses_angular_material"):
            adaptations.append("""
# Ficheros específicos para Angular Material
find:
  - label: "angular-material.module.ts"
    description: "Configuración de módulos de Angular Material."
""")
        
        if self.detected_tech.get("uses_ngrx"):
            adaptations.append("""
# Símbolos específicos para NgRx
symbols:
  - label: "@Injectable() Store"
    description: "Servicio de store de NgRx para gestión de estado."
  - label: "createAction"
    description: "Función para crear acciones de NgRx."
  - label: "createReducer"
    description: "Función para crear reducers de NgRx."
""")
        
        if self.detected_tech.get("is_pwa"):
            adaptations.append("""
# Ficheros específicos para PWA
find:
  - label: "manifest.json"
    description: "Manifiesto de la aplicación PWA."
  - label: "ngsw-config.json"
    description: "Configuración del Service Worker de Angular."
""")
        
        if self.detected_tech.get("has_ssr"):
            adaptations.append("""
# Ficheros específicos para SSR
find:
  - label: "app.server.ts"
    description: "Configuración del servidor para SSR."
  - label: "main.server.ts"
    description: "Punto de entrada del servidor para SSR."
""")
        
        # Add adaptations to the content
        if adaptations:
            content += "\n" + "\n".join(adaptations)
        
        return content

    def _adapt_rules_for_spring_boot(self, content):
        """Adapts Spring Boot rules based on detected version and features."""
        adaptations = []
        
        # Add version detection header at the top
        major_version = self.detected_tech.get("spring_boot_major_version")
        full_version = self.detected_tech.get("spring_boot_version")
        
        if full_version:
            adaptations.append(f"""
# =============================================================================
# DETECCIÓN AUTOMÁTICA: Spring Boot {full_version}
# =============================================================================""")
            
            if major_version == 1:
                adaptations.append("""
# ⚠️  ADVERTENCIA: Versión LEGACY detectada
# Esta versión tiene vulnerabilidades conocidas y soporte limitado
# Se recomienda encarecidamente actualizar a una versión moderna""")
            elif major_version == 2:
                adaptations.append("""
# ✅ Versión ESTABLE detectada
# Spring Boot 2.x es una versión madura con soporte de seguridad activo""")
            elif major_version >= 3:
                adaptations.append("""
# 🚀 Versión MODERNA detectada  
# Spring Boot 3.x incluye las últimas características de seguridad
# Requiere Java 17+ y Spring Framework 6+""")
        elif major_version:
            adaptations.append(f"""
# =============================================================================
# DETECCIÓN AUTOMÁTICA: Spring Boot {major_version}.x
# =============================================================================""")
        
        # Add detected features summary
        detected_features = []
        if self.detected_tech.get("uses_spring_security"):
            detected_features.append("Spring Security")
        if self.detected_tech.get("uses_spring_data_jpa"):
            detected_features.append("Spring Data JPA")
        if self.detected_tech.get("uses_actuator"):
            detected_features.append("Spring Boot Actuator")
        if self.detected_tech.get("uses_webflux"):
            detected_features.append("Spring WebFlux")
        if self.detected_tech.get("uses_spring_cloud"):
            detected_features.append("Spring Cloud")
        if self.detected_tech.get("database_h2"):
            detected_features.append("H2 Database")
        if self.detected_tech.get("database_mysql"):
            detected_features.append("MySQL")
        if self.detected_tech.get("database_postgresql"):
            detected_features.append("PostgreSQL")
        
        if detected_features:
            adaptations.append(f"""
# 📦 CARACTERÍSTICAS DETECTADAS: {', '.join(detected_features)}
# Las reglas han sido adaptadas automáticamente para estas tecnologías
""")
        
        # Security priority indicator
        security_priority = self.detected_tech.get("security_priority")
        if security_priority:
            priority_text = {
                "high": "🔴 ALTA - Requiere revisión inmediata de seguridad",
                "medium": "🟡 MEDIA - Aplicar mejores prácticas de seguridad",
                "low": "🟢 BAJA - Versión moderna con buenas prácticas por defecto"
            }.get(security_priority, "")
            
            if priority_text:
                adaptations.append(f"""
# 🛡️  PRIORIDAD DE SEGURIDAD: {priority_text}
""")
        
        if major_version:            
            # Version-specific security adaptations
            if self.detected_tech.get("is_legacy"):
                adaptations.append("""
# Reglas CRÍTICAS para Spring Boot 1.x (LEGACY)
find:
  - label: "application.properties"
    description: "CRÍTICO LEGACY: Buscar configuraciones obsoletas de seguridad y credenciales hardcodeadas."
  - label: "SecurityConfiguration.java"
    description: "CRÍTICO LEGACY: Configuración de seguridad legacy. Verificar configuraciones obsoletas."

symbols:
  - label: "HttpSecurity"
    description: "CRÍTICO LEGACY: Configuración HTTP Security v4. Verificar configuraciones obsoletas."
  - label: "@EnableGlobalMethodSecurity"
    description: "LEGACY: Anotación obsoleta en Spring Boot 1.x. Migrar a configuración moderna."
  - label: "WebSecurityConfigurerAdapter"
    description: "CRÍTICO LEGACY: Adapter obsoleto. Alto riesgo de configuraciones inseguras."
  - label: "authorizeRequests()"
    description: "LEGACY: Método obsoleto para autorización. Verificar configuración segura."
""")
            
            elif self.detected_tech.get("is_modern"):
                adaptations.append("""
# Reglas para Spring Boot 2.x (MODERNO)
symbols:
  - label: "@EnableWebSecurity"
    description: "SEGURIDAD: Configuración moderna de Spring Security 5+. Verificar configuración completa."
  - label: "SecurityFilterChain"
    description: "MODERNO: Bean de cadena de filtros de seguridad. Verificar configuración apropiada."
  - label: "authorizeHttpRequests()"
    description: "MODERNO: Método moderno para autorización HTTP. Verificar reglas de acceso."
""")
            
            elif self.detected_tech.get("is_latest"):
                adaptations.append("""
# Reglas para Spring Boot 3.x (ÚLTIMO)
find:
  - label: "SecurityConfig.java"
    description: "MODERNO: Configuración de seguridad Spring Boot 3+. Verificar uso de nuevas características."

symbols:
  - label: "requestMatchers()"
    description: "MODERNO: Nuevo método para matching de requests en Spring Security 6+."
  - label: "@EnableMethodSecurity"
    description: "MODERNO: Nueva anotación para seguridad de métodos en Spring Boot 3+."
  - label: "Observation"
    description: "NUEVO: API de observabilidad de Spring Boot 3+. Verificar no exposición de datos sensibles."
""")
        
        # Feature-specific adaptations
        if self.detected_tech.get("uses_spring_security"):
            adaptations.append("""
# Reglas específicas para Spring Security
find:
  - label: "UserDetailsService.java"
    description: "SEGURIDAD: Servicio de detalles de usuario. Verificar implementación segura."
  - label: "PasswordEncoder.java"
    description: "CRÍTICO: Codificador de passwords. Verificar uso de algoritmos seguros (BCrypt)."

symbols:
  - label: "@PreAuthorize"
    description: "AUTORIZACIÓN: Control de acceso granular. Verificar expresiones SpEL seguras."
  - label: "BCryptPasswordEncoder"
    description: "SEGURIDAD: Codificador seguro de passwords. Verificar configuración apropiada."
  - label: "NoOpPasswordEncoder"
    description: "CRÍTICO: Codificador SIN CIFRADO. NUNCA usar en producción."
""")
        
        if self.detected_tech.get("uses_actuator"):
            adaptations.append("""
# Reglas CRÍTICAS para Spring Boot Actuator
find:
  - label: "application.properties"
    description: "CRÍTICO ACTUATOR: Verificar que endpoints estén protegidos en producción."

symbols:
  - label: "management.endpoints.web.exposure.include"
    description: "CRÍTICO: Endpoints expuestos. Verificar que no sean '*' en producción."
  - label: "/actuator/health"
    description: "ENDPOINT: Health check. Verificar que no exponga información sensible."
  - label: "/actuator/env"
    description: "CRÍTICO: Endpoint de environment. ALTO RIESGO de exposición de secrets."
  - label: "/actuator/configprops"
    description: "CRÍTICO: Properties de configuración. Puede exponer credenciales."
""")
        
        if self.detected_tech.get("uses_spring_data_jpa"):
            adaptations.append("""
# Reglas específicas para Spring Data JPA
symbols:
  - label: "@Query"
    description: "CRÍTICO: Queries personalizadas. Verificar contra SQL Injection en queries nativas."
  - label: "nativeQuery = true"
    description: "CRÍTICO: Query nativa SQL. ALTO RIESGO de SQL Injection si no usa parámetros."
  - label: "EntityManager.createQuery"
    description: "CRÍTICO: Query dinámico. Verificar uso de parámetros preparados."
""")
        
        if self.detected_tech.get("database_h2") and self.detected_tech.get("h2_console_risk"):
            adaptations.append("""
# Reglas CRÍTICAS para H2 Database
find:
  - label: "application.properties"
    description: "CRÍTICO H2: Verificar que h2.console.enabled=false en producción."

symbols:
  - label: "spring.h2.console.enabled"
    description: "CRÍTICO: Consola H2. NUNCA habilitar en producción (acceso directo a BD)."
  - label: "/h2-console"
    description: "CRÍTICO: Endpoint de consola H2. Verificar que esté deshabilitado en producción."
""")
        
        if self.detected_tech.get("uses_webflux"):
            adaptations.append("""
# Reglas específicas para Spring WebFlux (Reactive)
symbols:
  - label: "ServerRequest"
    description: "REACTIVE: Request reactivo. Verificar validación de datos de entrada."
  - label: "ServerResponse"
    description: "REACTIVE: Response reactivo. Verificar headers de seguridad."
  - label: "@EnableWebFluxSecurity"
    description: "SEGURIDAD: Configuración de seguridad reactiva. Verificar configuración completa."
""")
        
        if self.detected_tech.get("uses_spring_cloud"):
            adaptations.append("""
# Reglas específicas para Spring Cloud
find:
  - label: "bootstrap.yml"
    description: "CONFIGURACIÓN CLOUD: Configuración de bootstrap. Verificar secrets y endpoints seguros."

symbols:
  - label: "@EnableConfigServer"
    description: "CONFIG SERVER: Servidor de configuración. Verificar autenticación y cifrado."
  - label: "spring.cloud.config.uri"
    description: "CONFIGURACIÓN: URI del config server. Verificar conexión segura (HTTPS)."
""")
        
        # Security priority based adaptations
        security_priority = self.detected_tech.get("security_priority")
        if security_priority == "high":
            adaptations.append("""
# Reglas adicionales para ALTA PRIORIDAD de seguridad
symbols:
  - label: "LEGACY_CONFIG"
    description: "CRÍTICO: Configuraciones legacy que pueden tener vulnerabilidades conocidas."
  - label: "deprecated"
    description: "OBSOLETO: Código marcado como deprecated. Verificar actualización urgente."
""")
        
        # Add adaptations to the content
        if adaptations:
            content += "\n" + "\n".join(adaptations)
        
        return content

    def _adapt_rules_for_java_legacy_spring(self, content):
        """Adapts Java Legacy Spring rules based on detected version and features."""
        adaptations = []
        
        # Add version detection header at the top
        spring_version = self.detected_tech.get("spring_framework_version")
        major_version = self.detected_tech.get("spring_major_version")
        minor_version = self.detected_tech.get("spring_minor_version")
        
        if spring_version:
            adaptations.append(f"""
# =============================================================================
# DETECCIÓN AUTOMÁTICA: Spring Framework {spring_version}
# =============================================================================""")
            
            if self.detected_tech.get("is_very_legacy"):
                adaptations.append("""
# 🔴 ALERTA CRÍTICA: Versión MUY LEGACY detectada
# Esta versión tiene vulnerabilidades CRÍTICAS conocidas
# ACTUALIZACIÓN URGENTE requerida - Alto riesgo de seguridad""")
            elif self.detected_tech.get("is_legacy"):
                adaptations.append("""
# ⚠️ ADVERTENCIA ALTA: Versión LEGACY detectada
# Esta versión tiene vulnerabilidades conocidas documentadas
# Se recomienda planificar actualización prioritaria""")
            elif self.detected_tech.get("is_old"):
                adaptations.append("""
# ⚠️ Versión ANTIGUA detectada
# Considerar actualización por mejoras de seguridad
# Aplicar parches de seguridad disponibles""")
            else:
                adaptations.append("""
# ✅ Versión relativamente moderna de Spring Framework
# Mantener actualizado con parches de seguridad""")
        elif major_version:
            adaptations.append(f"""
# =============================================================================
# DETECCIÓN AUTOMÁTICA: Spring Framework {major_version}.x
# =============================================================================""")
        
        # Add detected features and technologies summary
        detected_features = []
        if self.detected_tech.get("uses_spring_security"):
            detected_features.append("Spring Security")
        if self.detected_tech.get("uses_spring_webmvc"):
            detected_features.append("Spring WebMVC")
        if self.detected_tech.get("uses_spring_orm"):
            detected_features.append("Spring ORM")
        if self.detected_tech.get("uses_hibernate"):
            detected_features.append("Hibernate ORM")
        if self.detected_tech.get("uses_struts"):
            detected_features.append("⚠️ Apache Struts")
        if self.detected_tech.get("uses_log4j"):
            detected_features.append("⚠️ Log4j")
        if self.detected_tech.get("database_mysql"):
            detected_features.append("MySQL")
        if self.detected_tech.get("database_oracle"):
            detected_features.append("Oracle DB")
        if self.detected_tech.get("database_sqlserver"):
            detected_features.append("SQL Server")
        
        jsp_count = self.detected_tech.get("jsp_files_count", 0)
        if jsp_count > 0:
            detected_features.append(f"JSP files ({jsp_count})")
        
        if detected_features:
            adaptations.append(f"""
# 📦 TECNOLOGÍAS DETECTADAS: {', '.join(detected_features)}
# Las reglas han sido adaptadas automáticamente para estas tecnologías
""")
        
        # Security priority indicator
        security_priority = self.detected_tech.get("security_priority")
        if security_priority:
            priority_text = {
                "critical": "🔴 CRÍTICA - Requiere acción inmediata de seguridad",
                "high": "🟠 ALTA - Planificar revisión de seguridad urgente", 
                "medium": "🟡 MEDIA - Aplicar mejores prácticas de seguridad",
                "low": "🟢 BAJA - Mantener prácticas de seguridad actuales"
            }.get(security_priority, "")
            
            if priority_text:
                adaptations.append(f"""
# 🛡️ PRIORIDAD DE SEGURIDAD: {priority_text}
""")
        
        # Servlet version analysis
        servlet_version = self.detected_tech.get("servlet_version")
        if servlet_version:
            adaptations.append(f"""
# 📋 SERVLET API: Versión {servlet_version} detectada""")
            
            if self.detected_tech.get("servlet_very_legacy"):
                adaptations.append("""
# ⚠️ Servlet API MUY LEGACY - Revisar configuraciones de seguridad web""")
            elif self.detected_tech.get("servlet_legacy"):
                adaptations.append("""
# ⚠️ Servlet API LEGACY - Verificar configuraciones modernas disponibles""")
        
        # Version-specific adaptations
        if major_version:
            if major_version == 1:
                adaptations.append("""
# Reglas CRÍTICAS específicas para Spring Framework 1.x
find:
  - label: "**/*-servlet.xml"
    description: "CRÍTICO 1.x: Configuración servlet legacy. Verificar configuraciones de seguridad obsoletas."
  - label: "web.xml"
    description: "CRÍTICO 1.x: Descriptor web muy legacy. Verificar filtros de seguridad y configuraciones."

symbols:
  - label: "SimpleFormController"
    description: "LEGACY 1.x: Controlador obsoleto. Alto riesgo de vulnerabilidades de validación."
  - label: "MultiActionController"
    description: "LEGACY 1.x: Controlador multi-acción. Verificar validación de entrada."
  - label: "AbstractCommandController"
    description: "LEGACY 1.x: Controlador de comando abstracto. Verificar binding seguro."
  - label: "BeanNameViewResolver"
    description: "LEGACY 1.x: Resolver de vistas. Verificar no exposición de beans sensibles."
""")
            
            elif major_version == 2:
                adaptations.append("""
# Reglas específicas para Spring Framework 2.x
find:
  - label: "applicationContext.xml"
    description: "LEGACY 2.x: Configuración XML. Verificar beans de seguridad y datasources."

symbols:
  - label: "@Controller"
    description: "LEGACY 2.x: Controlador basado en anotaciones. Verificar validación de entrada."
  - label: "@RequestMapping"
    description: "LEGACY 2.x: Mapeo de requests. Verificar métodos HTTP permitidos."
  - label: "FormBackingObject"
    description: "LEGACY 2.x: Objeto de respaldo de formulario. Verificar binding seguro."
  - label: "ModelAndView"
    description: "LEGACY 2.x: Modelo y vista. Verificar no exposición de datos sensibles."
""")
            
            elif major_version == 3:
                adaptations.append("""
# Reglas específicas para Spring Framework 3.x
symbols:
  - label: "@RequestMapping"
    description: "3.x: Mapeo de requests mejorado. Verificar configuración de métodos y paths."
  - label: "@PathVariable"
    description: "3.x: Variables de path. Verificar validación de parámetros de URL."
  - label: "@RequestParam"
    description: "3.x: Parámetros de request. Verificar validación y sanitización."
  - label: "@ModelAttribute"
    description: "3.x: Atributos de modelo. Verificar binding seguro de datos."
""")
        
        # Technology-specific adaptations
        if self.detected_tech.get("uses_spring_security"):
            adaptations.append("""
# Reglas específicas para Spring Security Legacy
find:
  - label: "security-context.xml"
    description: "SEGURIDAD LEGACY: Configuración XML de Spring Security. Verificar configuraciones obsoletas."
  - label: "spring-security.xml"
    description: "SEGURIDAD LEGACY: Archivo principal de seguridad. Verificar autenticación y autorización."

symbols:
  - label: "<security:http>"
    description: "SEGURIDAD XML: Configuración HTTP legacy. Verificar CSRF, session management."
  - label: "<security:authentication-manager>"
    description: "AUTENTICACIÓN XML: Manager legacy. Verificar configuración de providers."
  - label: "<security:user-service>"
    description: "USUARIOS XML: Servicio de usuarios en XML. Buscar credenciales hardcodeadas."
  - label: "<security:password-encoder>"
    description: "CIFRADO XML: Codificador de passwords. Verificar algoritmos seguros."
""")
        
        if self.detected_tech.get("uses_struts"):
            struts_version = self.detected_tech.get("struts_version", "")
            adaptations.append(f"""
# Reglas CRÍTICAS para Apache Struts {struts_version}
find:
  - label: "struts-config.xml"
    description: "CRÍTICO STRUTS: Configuración Struts. ALTO RIESGO de vulnerabilidades S2-XXX."
  - label: "struts.xml"
    description: "CRÍTICO STRUTS: Configuración Struts 2. Verificar versión contra CVEs conocidos."

symbols:
  - label: "ActionSupport"
    description: "STRUTS: Clase base de acciones. Verificar validación de entrada."
  - label: "ActionForm"
    description: "STRUTS: Formularios de acción. Verificar validación y binding seguro."
  - label: "ognl:"
    description: "CRÍTICO STRUTS: Expresiones OGNL. ALTO RIESGO de ejecución de código remoto."
  - label: "%{{"
    description: "CRÍTICO STRUTS: Sintaxis OGNL. Puede permitir ejecución de código malicioso."
""")
        
        if self.detected_tech.get("uses_hibernate"):
            hibernate_version = self.detected_tech.get("hibernate_version", "")
            adaptations.append(f"""
# Reglas específicas para Hibernate {hibernate_version}
find:
  - label: "hibernate.cfg.xml"
    description: "HIBERNATE: Configuración principal. Verificar credenciales y configuraciones de conexión."
  - label: "**/*.hbm.xml"
    description: "HIBERNATE: Archivos de mapeo. Verificar configuraciones de entidades."

symbols:
  - label: "createQuery("
    description: "CRÍTICO HIBERNATE: Queries dinámicas. Verificar contra HQL Injection."
  - label: "createSQLQuery("
    description: "CRÍTICO HIBERNATE: Queries SQL nativas. ALTO RIESGO de SQL Injection."
  - label: "Session.get("
    description: "HIBERNATE: Obtención de entidades. Verificar autorización de acceso."
  - label: "SessionFactory"
    description: "HIBERNATE: Factory de sesiones. Verificar configuración segura."
""")
        
        if self.detected_tech.get("uses_log4j"):
            log4j_version = self.detected_tech.get("log4j_version", "")
            if self.detected_tech.get("log4j_security_risk"):
                adaptations.append(f"""
# Reglas CRÍTICAS para Log4j {log4j_version} (VULNERABILIDAD CONOCIDA)
find:
  - label: "log4j.properties"
    description: "CRÍTICO LOG4J: Configuración Log4j 1.x. VERIFICAR contra vulnerabilidades conocidas."
  - label: "log4j.xml"
    description: "CRÍTICO LOG4J: Configuración XML. Riesgo de Log4Shell y otras vulnerabilidades."

symbols:
  - label: "Logger.getLogger"
    description: "LOG4J 1.x: Logger legacy. Verificar no logging de datos sensibles."
  - label: "log.debug"
    description: "LOGGING: Debug logs. Verificar no exposición de información sensible."
  - label: "log.info"
    description: "LOGGING: Info logs. Verificar contenido seguro para logs."
""")
        
        # JSP-specific adaptations
        jsp_count = self.detected_tech.get("jsp_files_count", 0)
        if jsp_count > 0:
            adaptations.append(f"""
# Reglas específicas para JSP ({jsp_count} archivos detectados)
find:
  - label: "**/*.jsp"
    description: "CRÍTICO JSP: Páginas JSP. Buscar XSS, expresiones sin escapar y lógica de negocio."
  - label: "**/*.jspf"
    description: "CRÍTICO JSP: Fragmentos JSP. Verificar includes seguros y validaciones."

symbols:
  - label: "<%="
    description: "CRÍTICO JSP: Expresiones de salida. ALTO RIESGO de XSS si no se escapa."
  - label: "<jsp:include"
    description: "JSP: Inclusión de páginas. Verificar paths seguros y validación."
  - label: "<jsp:forward"
    description: "JSP: Forward de páginas. Verificar destinos válidos y autorizados."
  - label: "request.getParameter"
    description: "CRÍTICO JSP: Parámetros HTTP. Verificar validación antes de usar."
  - label: "pageContext.setAttribute"
    description: "JSP: Atributos de contexto. Verificar no exposición de datos sensibles."
""")
        
        # Database-specific adaptations
        databases = []
        if self.detected_tech.get("database_mysql"):
            databases.append("MySQL")
        if self.detected_tech.get("database_oracle"):
            databases.append("Oracle")
        if self.detected_tech.get("database_sqlserver"):
            databases.append("SQL Server")
        
        if databases:
            adaptations.append(f"""
# Reglas específicas para bases de datos: {', '.join(databases)}
symbols:
  - label: "DriverManager.getConnection"
    description: "CRÍTICO DB: Conexión directa. Verificar credenciales no hardcodeadas."
  - label: "Statement.executeQuery"
    description: "CRÍTICO DB: Query directo. ALTO RIESGO de SQL Injection."
  - label: "Statement.execute"
    description: "CRÍTICO DB: Ejecución SQL. Verificar uso de PreparedStatement."
  - label: "PreparedStatement.setString"
    description: "DB: Parámetros preparados. Método seguro para evitar SQL Injection."
""")
        
        # Build system adaptations
        if self.detected_tech.get("is_maven"):
            adaptations.append("""
# Reglas específicas para Maven
find:
  - label: "pom.xml"
    description: "MAVEN: Configuración del proyecto. Verificar dependencias sin vulnerabilidades."
  - label: "settings.xml"
    description: "MAVEN: Configuración de usuario. Verificar no exposición de credenciales."
""")
        
        if self.detected_tech.get("is_gradle"):
            adaptations.append("""
# Reglas específicas para Gradle  
find:
  - label: "build.gradle"
    description: "GRADLE: Script de construcción. Verificar dependencias y configuraciones seguras."
  - label: "gradle.properties"
    description: "GRADLE: Propiedades. Verificar no exposición de credenciales."
""")
        
        # Security priority based additional rules
        if security_priority == "critical":
            adaptations.append("""
# Reglas adicionales para PRIORIDAD CRÍTICA
symbols:
  - label: "FIXME"
    description: "CRÍTICO: Código marcado para reparación. Puede indicar vulnerabilidades conocidas."
  - label: "TODO"
    description: "PENDIENTE: Trabajo incompleto. Verificar impacto en seguridad."
  - label: "XXX"
    description: "ADVERTENCIA: Marcador de problemas. Revisar por posibles vulnerabilidades."
  - label: "HACK"
    description: "CRÍTICO: Solución temporal. Alto riesgo de vulnerabilidades."
""")
        
        # Add adaptations to the content
        if adaptations:
            content += "\n" + "\n".join(adaptations)
        
        return content

    def _adapt_rules_for_python(self, content):
        """Adapts Python rules based on detected frameworks and technologies."""
        adaptations = []
        
        # Add detection header at the top
        frameworks = self.detected_tech.get("frameworks_detected", [])
        indicators = self.detected_tech.get("python_indicators", [])
        python_version = self.detected_tech.get("python_version")
        python_path = self.detected_tech.get("python_path")
        python_source = self.detected_tech.get("python_source")
        is_venv = self.detected_tech.get("is_venv", False)
        venv_path = self.detected_tech.get("venv_path")
        
        if frameworks or indicators or python_version:
            adaptations.append(f"""
# =============================================================================
# DETECCIÓN AUTOMÁTICA: Proyecto Python
# =============================================================================""")
            
            # Añadir información de versión de Python
            if python_version:
                python_major = self.detected_tech.get("python_major_version", "")
                python_minor = self.detected_tech.get("python_minor_version", "")
                
                version_info = f"# 🐍 PYTHON: Versión {python_version}"
                if python_path:
                    version_info += f"\n# 📍 RUTA: {python_path}"
                
                # Indicar fuente de detección
                source_labels = {
                    "venv": "entorno virtual",
                    "pyenv": "archivo .python-version (pyenv)",
                    "pyproject": "pyproject.toml",
                    "pipfile": "Pipfile",
                    "setup.py": "setup.py",
                    "system": "intérprete del sistema"
                }
                source_label = source_labels.get(python_source, python_source)
                version_info += f"\n# 🔧 FUENTE: {source_label}"
                
                if is_venv and venv_path:
                    version_info += f"\n# 📁 VENV: {venv_path}"
                
                # Advertencias según versión
                if python_major == 2:
                    version_info += "\n# ⚠️ ADVERTENCIA: Python 2.x está OBSOLETO. Migrar a Python 3.x urgentemente."
                elif python_major == 3 and python_minor and python_minor < 8:
                    version_info += f"\n# ⚠️ ADVERTENCIA: Python 3.{python_minor} tiene soporte limitado. Considerar actualizar."
                elif python_major == 3 and python_minor and python_minor >= 11:
                    version_info += f"\n# ✅ Python 3.{python_minor} es una versión moderna con mejoras de rendimiento."
                
                adaptations.append(version_info)
            
            if frameworks:
                adaptations.append(f"""
# 📦 FRAMEWORKS DETECTADOS: {', '.join(frameworks)}
# Las reglas han sido adaptadas automáticamente para estos frameworks""")
            
            if indicators:
                adaptations.append(f"""
# 🔍 INDICADORES ENCONTRADOS: {', '.join(indicators)}""")
        
        # Security priority indicator
        security_priority = self.detected_tech.get("security_priority")
        if security_priority:
            priority_text = {
                "high": "🔴 ALTA - Configuraciones inseguras detectadas",
                "medium": "🟡 MEDIA - Revisar dependencias y configuraciones",
                "low": "🟢 BAJA - Configuración estándar detectada"
            }.get(security_priority, "")
            
            if priority_text:
                adaptations.append(f"""
# 🛡️ PRIORIDAD DE SEGURIDAD: {priority_text}""")
        
        # Django-specific adaptations
        if self.detected_tech.get("is_django"):
            django_version = self.detected_tech.get("django_version", "versión no detectada")
            adaptations.append(f"""
# Reglas específicas para Django {django_version}
find:
  - label: "settings/**/*.py"
    description: "CRÍTICO DJANGO: Configuraciones por entorno. Verificar no exposición de secrets."
  - label: "**/migrations/*.py"
    description: "DJANGO: Migraciones de BD. Verificar no datos sensibles en migraciones."
  - label: "**/templatetags/*.py"
    description: "DJANGO: Template tags. Verificar no exposición de datos sensibles en templates."

symbols:
  - label: "django.db.models.Model"
    description: "DJANGO: Modelos de datos. Verificar validaciones y campos sensibles."
  - label: "django.contrib.admin"
    description: "CRÍTICO DJANGO: Admin interface. Verificar permisos y campos expuestos."
  - label: "django.shortcuts.render"
    description: "DJANGO: Renderizado de templates. Verificar contexto y datos expuestos."
  - label: "HttpResponse"
    description: "DJANGO: Respuestas HTTP. Verificar headers de seguridad."
  - label: "JsonResponse"
    description: "DJANGO: Respuestas JSON. Verificar no exposición de información sensible."
""")
            
            if self.detected_tech.get("debug_enabled"):
                adaptations.append("""
# ADVERTENCIA: DEBUG=True detectado
symbols:
  - label: "DEBUG = True"
    description: "CRÍTICO DJANGO: Debug habilitado. NUNCA usar en producción."
""")
            
            if self.detected_tech.get("hardcoded_secret_key"):
                adaptations.append("""
# CRÍTICO: SECRET_KEY hardcodeada detectada
symbols:
  - label: "SECRET_KEY = "
    description: "CRÍTICO DJANGO: Clave secreta hardcodeada. Usar variables de entorno."
""")
                
            # Database-specific adaptations for Django
            if self.detected_tech.get("database_sqlite"):
                adaptations.append("""
# Base de datos SQLite detectada
find:
  - label: "db.sqlite3"
    description: "DJANGO SQLite: Base de datos SQLite. Verificar no versionado en producción."
""")
            elif self.detected_tech.get("database_postgresql"):
                adaptations.append("""
# Base de datos PostgreSQL detectada
symbols:
  - label: "psycopg2"
    description: "DJANGO PostgreSQL: Driver PostgreSQL. Verificar conexiones seguras."
""")
            elif self.detected_tech.get("database_mysql"):
                adaptations.append("""
# Base de datos MySQL detectada
symbols:
  - label: "MySQLdb"
    description: "DJANGO MySQL: Driver MySQL. Verificar conexiones y configuraciones seguras."
""")
        
        # Flask-specific adaptations
        if self.detected_tech.get("is_flask"):
            flask_version = self.detected_tech.get("flask_version", "versión no detectada")
            adaptations.append(f"""
# Reglas específicas para Flask {flask_version}
symbols:
  - label: "Flask(__name__)"
    description: "FLASK: Aplicación Flask. Verificar configuración segura."
  - label: "@app.route"
    description: "FLASK: Rutas de aplicación. Verificar autenticación y validación."
  - label: "request.form"
    description: "CRÍTICO FLASK: Datos de formulario. Verificar validación y sanitización."
  - label: "request.args"
    description: "CRÍTICO FLASK: Parámetros URL. Verificar validación contra inyecciones."
  - label: "request.json"
    description: "FLASK: Datos JSON. Verificar validación de estructura y contenido."
  - label: "session["
    description: "FLASK: Sesiones. Verificar configuración segura de cookies."
  - label: "render_template"
    description: "FLASK: Renderizado templates. Verificar escapado automático habilitado."
  - label: "make_response"
    description: "FLASK: Respuestas HTTP. Verificar headers de seguridad."
""")
            
            if self.detected_tech.get("debug_enabled"):
                adaptations.append("""
# ADVERTENCIA: Debug mode detectado en Flask
symbols:
  - label: "debug=True"
    description: "CRÍTICO FLASK: Debug habilitado. NUNCA usar en producción."
  - label: "app.debug = True"
    description: "CRÍTICO FLASK: Debug configurado. Verificar que no vaya a producción."
""")
        
        # FastAPI-specific adaptations
        if self.detected_tech.get("is_fastapi"):
            fastapi_version = self.detected_tech.get("fastapi_version", "versión no detectada")
            adaptations.append(f"""
# Reglas específicas para FastAPI {fastapi_version}
symbols:
  - label: "FastAPI()"
    description: "FASTAPI: Aplicación FastAPI. Verificar configuración de CORS y middleware."
  - label: "@app.get"
    description: "FASTAPI: Endpoints GET. Verificar validación de parámetros."
  - label: "@app.post"
    description: "CRÍTICO FASTAPI: Endpoints POST. Verificar validación de body y autenticación."
  - label: "@app.put"
    description: "FASTAPI: Endpoints PUT. Verificar autorización y validación."
  - label: "@app.delete"
    description: "CRÍTICO FASTAPI: Endpoints DELETE. Verificar autorización estricta."
  - label: "Depends("
    description: "FASTAPI: Inyección de dependencias. Verificar validación de dependencias."
  - label: "HTTPException"
    description: "FASTAPI: Excepciones HTTP. Verificar no exposición de información interna."
  - label: "Request"
    description: "FASTAPI: Objeto request. Verificar validación de datos de entrada."
""")
        
        # Package management adaptations
        if self.detected_tech.get("is_poetry"):
            adaptations.append("""
# Proyecto Poetry detectado
find:
  - label: "pyproject.toml"
    description: "POETRY: Configuración Poetry. Verificar dependencias y versiones."
""")
        
        if self.detected_tech.get("is_pipenv"):
            adaptations.append("""
# Proyecto Pipenv detectado
find:
  - label: "Pipfile"
    description: "PIPENV: Configuración Pipenv. Verificar dependencias y configuraciones."
  - label: "Pipfile.lock"
    description: "PIPENV: Lock file. Verificar integridad de dependencias."
""")
        
        # Requirements analysis
        requirements = self.detected_tech.get("requirements", [])
        if requirements:
            risky_packages = self.detected_tech.get("risky_packages", [])
            if risky_packages:
                adaptations.append(f"""
# ADVERTENCIA: Paquetes de riesgo detectados
# Paquetes problemáticos: {', '.join(risky_packages)}
symbols:
  - label: "import pickle"
    description: "CRÍTICO: Paquete pickle detectado. Verificar uso seguro."
  - label: "import md5"
    description: "VULNERABLE: MD5 detectado. Usar algoritmos más seguros."
""")
        
        # WSGI/ASGI adaptations
        if self.detected_tech.get("has_wsgi"):
            adaptations.append("""
# Configuración WSGI detectada
find:
  - label: "wsgi.py"
    description: "WSGI: Configuración servidor WSGI. Verificar configuración de producción."
""")
        
        if self.detected_tech.get("has_asgi"):
            adaptations.append("""
# Configuración ASGI detectada
find:
  - label: "asgi.py"
    description: "ASGI: Configuración servidor ASGI. Verificar configuración async segura."
""")
        
        # Testing framework adaptations
        if self.detected_tech.get("has_pytest"):
            adaptations.append("""
# Framework de testing Pytest detectado
find:
  - label: "pytest.ini"
    description: "TESTING: Configuración pytest. Verificar no exposición de credenciales de test."
  - label: "conftest.py"
    description: "TESTING: Configuración fixtures. Verificar fixtures seguros."
""")
        
        if self.detected_tech.get("has_tox"):
            adaptations.append("""
# Tox detectado para testing
find:
  - label: "tox.ini"
    description: "TESTING: Configuración tox. Verificar comandos de test seguros."
""")
        
        # Docker adaptations
        if self.detected_tech.get("has_docker"):
            adaptations.append("""
# Docker detectado
find:
  - label: "Dockerfile"
    description: "DOCKER: Configuración Docker. Verificar usuario no-root y secrets seguros."
  - label: "docker-compose.yml"
    description: "DOCKER: Orquestación. Verificar configuración de redes y volúmenes."
""")
        
        # Add adaptations to the content
        if adaptations:
            content += "\n" + "\n".join(adaptations)
        
        return content

    def _adapt_rules(self, base_rules_content):
        """Adapts rules based on detected technologies."""
        if not self.detected_tech:
            return base_rules_content
        
        adapted_content = base_rules_content
        
        if self.project_type == "angular":
            adapted_content = self._adapt_rules_for_angular(adapted_content)
            if self.verbose and self.detected_tech:
                print(f"Adapted Angular rules based on detected features: {list(self.detected_tech.keys())}")
        
        elif self.project_type == "springboot":
            adapted_content = self._adapt_rules_for_spring_boot(adapted_content)
            if self.verbose and self.detected_tech:
                print(f"Adapted Spring Boot rules based on detected features: {list(self.detected_tech.keys())}")
        
        elif self.project_type == "java_legacy_spring":
            adapted_content = self._adapt_rules_for_java_legacy_spring(adapted_content)
            if self.verbose and self.detected_tech:
                print(f"Adapted Java Legacy Spring rules based on detected features: {list(self.detected_tech.keys())}")
        
        elif self.project_type == "python":
            adapted_content = self._adapt_rules_for_python(adapted_content)
            if self.verbose and self.detected_tech:
                print(f"Adapted Python rules based on detected features: {list(self.detected_tech.keys())}")
        
        return adapted_content

    def generate(self):
        """Generates the final set of rules with frontmatter and content."""
        base_rules_data = self._load_base_template()
        
        # Apply adaptations based on detected technologies to the content
        adapted_content = self._adapt_rules(base_rules_data.get("content", ""))
        
        # TODO: Add custom rules merging logic here if needed
        
        # Return the complete structure with frontmatter
        self.rules = {
            "frontmatter": base_rules_data.get("frontmatter"),
            "content": adapted_content
        }
        return self.rules


# Main function to be called from ruleforge.py
def generate_rules(project_type, detected_tech=None, custom_rules_data=None, verbose=False):
    """Factory function to create and generate rules for a given project type."""
    if not project_type:
        if verbose:
            print("Error: Project type is required to generate rules.")
        return None

    rule_set_generator = RuleSet(project_type, detected_tech, custom_rules_data, verbose)
    return rule_set_generator.generate() 