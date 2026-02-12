#!/usr/bin/env node
/**
 * Wrapper Node.js para el servidor MCP Python de RuleForge
 * Este wrapper ejecuta el servidor Python y gestiona la comunicación stdio
 * 
 * Características:
 * - Detección automática de Python (3.8+)
 * - Soporte multiplataforma (Windows, Linux, Mac)
 * - Logging detallado para diagnóstico
 */

import { spawn, spawnSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { writeFileSync, mkdirSync, existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Crear directorio de logs
const logsDir = join(__dirname, 'logs');
try {
  mkdirSync(logsDir, { recursive: true });
} catch (e) {}

// Log de inicio
const now = new Date();
const logFile = join(logsDir, `wrapper_${now.toISOString().replace(/:/g, '-').split('.')[0]}.log`);

function log(msg) {
  const timestamp = new Date().toISOString();
  const logMsg = `[${timestamp}] ${msg}\n`;
  try {
    writeFileSync(logFile, logMsg, { flag: 'a' });
  } catch (e) {
    console.error('Error writing log:', e);
  }
}

/**
 * Verifica si un comando de Python existe y retorna su versión
 * @param {string} cmd - Comando a verificar (python, python3, py, etc.)
 * @returns {object|null} - {cmd, version} si es válido, null si no
 */
function checkPython(cmd) {
  try {
    const result = spawnSync(cmd, ['--version'], {
      encoding: 'utf8',
      timeout: 5000,
      windowsHide: true,
      shell: process.platform === 'win32'
    });
    
    if (result.status === 0) {
      // La salida puede estar en stdout o stderr dependiendo de la versión
      const output = (result.stdout || result.stderr || '').trim();
      const match = output.match(/Python\s+(\d+)\.(\d+)\.(\d+)/i);
      
      if (match) {
        const major = parseInt(match[1]);
        const minor = parseInt(match[2]);
        const patch = parseInt(match[3]);
        const version = `${major}.${minor}.${patch}`;
        
        // Verificar que sea Python 3.8 o superior
        if (major === 3 && minor >= 8) {
          log(`  ✓ ${cmd} -> Python ${version} (compatible)`);
          return { cmd, version, major, minor, patch };
        } else {
          log(`  ✗ ${cmd} -> Python ${version} (requiere 3.8+)`);
        }
      }
    }
  } catch (e) {
    log(`  ✗ ${cmd} -> Error: ${e.message}`);
  }
  return null;
}

/**
 * Detecta automáticamente la instalación de Python
 * Busca en orden de prioridad y retorna el primer Python válido (3.8+)
 * @returns {string} - Ruta o comando del ejecutable de Python
 */
function findPython() {
  log('Buscando instalación de Python...');
  
  // Lista de candidatos a probar en orden de prioridad
  const candidates = [];
  
  // 1. Variable de entorno PYTHON_PATH (permite override manual)
  if (process.env.PYTHON_PATH) {
    candidates.push(process.env.PYTHON_PATH);
  }
  
  // 2. Variable de entorno RULEFORGE_PYTHON (específica para RuleForge)
  if (process.env.RULEFORGE_PYTHON) {
    candidates.push(process.env.RULEFORGE_PYTHON);
  }
  
  // 3. Comandos genéricos del PATH
  candidates.push('python3');  // Preferido en Linux/Mac
  candidates.push('python');   // Genérico
  
  // 4. Windows: py launcher (gestiona múltiples versiones)
  if (process.platform === 'win32') {
    candidates.push('py -3');  // Fuerza Python 3
    candidates.push('py');
  }
  
  // 5. Rutas comunes de instalación en Windows
  if (process.platform === 'win32') {
    const userHome = process.env.USERPROFILE || process.env.HOME;
    const programFiles = process.env.ProgramFiles || 'C:\\Program Files';
    const localAppData = process.env.LOCALAPPDATA;
    
    // Python instalado desde python.org (versiones recientes)
    for (let minor = 13; minor >= 8; minor--) {
      candidates.push(`C:\\Python3${minor}\\python.exe`);
      candidates.push(`${programFiles}\\Python3${minor}\\python.exe`);
      if (localAppData) {
        candidates.push(`${localAppData}\\Programs\\Python\\Python3${minor}\\python.exe`);
      }
    }
    
    // Anaconda/Miniconda
    if (userHome) {
      candidates.push(`${userHome}\\Anaconda3\\python.exe`);
      candidates.push(`${userHome}\\Miniconda3\\python.exe`);
      candidates.push(`${userHome}\\anaconda3\\python.exe`);
      candidates.push(`${userHome}\\miniconda3\\python.exe`);
    }
  }
  
  // 6. Rutas comunes en Linux/Mac
  if (process.platform !== 'win32') {
    candidates.push('/usr/bin/python3');
    candidates.push('/usr/local/bin/python3');
    candidates.push('/opt/homebrew/bin/python3');  // Homebrew en Mac ARM
    
    const userHome = process.env.HOME;
    if (userHome) {
      // pyenv
      candidates.push(`${userHome}/.pyenv/shims/python3`);
      candidates.push(`${userHome}/.pyenv/shims/python`);
      // Anaconda/Miniconda
      candidates.push(`${userHome}/anaconda3/bin/python`);
      candidates.push(`${userHome}/miniconda3/bin/python`);
    }
  }
  
  // Probar cada candidato
  for (const candidate of candidates) {
    if (!candidate) continue;
    
    const result = checkPython(candidate);
    if (result) {
      log(`Python encontrado: ${candidate} (v${result.version})`);
      return candidate;
    }
  }
  
  // No se encontró Python válido
  const errorMsg = `
ERROR: No se encontró una instalación válida de Python 3.8+

RuleForge MCP requiere Python 3.8 o superior.

Soluciones:
1. Instala Python desde https://www.python.org/downloads/
2. Asegúrate de que Python está en el PATH del sistema
3. O establece la variable de entorno RULEFORGE_PYTHON con la ruta al ejecutable

Ejemplo (Windows):
  set RULEFORGE_PYTHON=C:\\Python311\\python.exe

Ejemplo (Linux/Mac):
  export RULEFORGE_PYTHON=/usr/bin/python3
`;
  
  log(errorMsg);
  console.error(errorMsg);
  process.exit(1);
}

log('='.repeat(60));
log('WRAPPER NODE.JS INICIADO');
log(`Directorio: ${__dirname}`);
log(`Node version: ${process.version}`);
log(`Plataforma: ${process.platform}`);
log('='.repeat(60));

// Detectar Python automáticamente
const pythonPath = findPython();
const serverScript = join(__dirname, 'server.py');

log(`Python seleccionado: ${pythonPath}`);
log(`Script: ${serverScript}`);

// Opciones para spawn
const spawnOptions = {
  cwd: __dirname,
  stdio: ['pipe', 'pipe', 'pipe'], // stdin, stdout, stderr
  windowsHide: true
};

log('Ejecutando servidor Python...');

// Ejecutar el servidor Python
const pythonProcess = spawn(pythonPath, ['-u', serverScript], spawnOptions);

log(`Proceso Python iniciado con PID: ${pythonProcess.pid}`);

// Conectar stdin
process.stdin.pipe(pythonProcess.stdin);

// Conectar stdout
pythonProcess.stdout.pipe(process.stdout);

// Capturar stderr para logging
pythonProcess.stderr.on('data', (data) => {
  const msg = data.toString();
  log(`[STDERR] ${msg}`);
  process.stderr.write(data);
});

// Manejar errores
pythonProcess.on('error', (error) => {
  log(`ERROR: ${error.message}`);
  log(error.stack);
  process.exit(1);
});

// Manejar cierre del proceso
pythonProcess.on('close', (code, signal) => {
  log(`Proceso Python cerrado. Código: ${code}, Señal: ${signal}`);
  process.exit(code || 0);
});

// Manejar señales de terminación
process.on('SIGINT', () => {
  log('SIGINT recibido, terminando...');
  pythonProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
  log('SIGTERM recibido, terminando...');
  pythonProcess.kill('SIGTERM');
});

log('Wrapper configurado correctamente, esperando comunicación...');

