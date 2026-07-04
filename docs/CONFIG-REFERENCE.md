# Configuration Reference

## Variables de Entorno

| Variable | Propósito | Default (Windows) | Default (Linux/macOS) |
|----------|-----------|-------------------|----------------------|
| `$HERMES_HOME` | Directorio raíz de Hermes | `~/AppData/Local/hermes` | `~/.hermes` |

Si `$HERMES_HOME` no está definida, el script usa el default según `sys.platform`.

---

## Archivo de Configuración JSON (`--json-config`)

### Formato

```json
{
    "hermes_home": "C:\\Users\\alice\\AppData\\Local\\hermes",
    "hermes_source": "C:\\Users\\alice\\AppData\\Local\\hermes\\hermes-agent",
    "restorer_exe": "C:\\Users\\alice\\Desktop\\hermes-restore.exe",
    "restorer_py": "C:\\Users\\alice\\Desktop\\hermes_restore.py"
}
```

### Campos

| Campo | Tipo | Descripción | Default |
|-------|------|-------------|---------|
| `hermes_home` | string (path) | Directorio de Hermes | Auto-detectado |
| `hermes_source` | string (path) | Código fuente de Hermes | `{hermes_home}/hermes-agent` |
| `restorer_exe` | string (path) | Restaurador standalone .exe | `~/Desktop/hermes-restore.exe` |
| `restorer_py` | string (path) | Restaurador Python | `~/Desktop/hermes_restore.py` |

### Uso

```bash
python hermes-complete-backup.py --json-config mi-config.json
python hermes-complete-backup.py --json-config mi-config.json --quick -o backup.zip
```

---

## Archivos Esenciales (ESSENTIAL_FILES)

Estos archivos se buscan en la raíz de `$HERMES_HOME`:

| Archivo | ¿Crítico? | Contiene |
|---------|-----------|----------|
| `config.yaml` | ✅ Sí | Configuración de modelos, proveedores, API keys |
| `.env` | ✅ Sí | Credenciales, tokens, proxy |
| `state.db` | ✅ Sí | Todo el historial de sesiones SQLite |
| `auth.json` | ✅ Sí | OAuth tokens (GitHub, Discord, etc.) |
| `auth.lock` | ❌ Opcional | Lock de autenticación |
| `channel_directory.json` | ❌ Opcional | Mapa de canales de gateway |
| `discord_threads.json` | ❌ Opcional | Hilos de Discord |
| `gateway_state.json` | ❌ Opcional | Estado actual del gateway |
| `gateway.lock` | ❌ Opcional | Lock del gateway |
| `gateway.pid` | ❌ Opcional | PID del proceso gateway |
| `processes.json` | ❌ Opcional | Procesos en background |
| `SOUL.md` | ❌ Opcional | Personalidad/configuración del agente |
| `.hermes_history` | ❌ Opcional | Historial de comandos |

---

## Directorios Esenciales (ESSENTIAL_DIRS)

| Directorio | ¿Crítico? | Contenido |
|------------|-----------|-----------|
| `cron/` | ✅ Sí | `jobs.json` con todos los trabajos programados |
| `memories/` | ✅ Sí | `MEMORY.md` + `USER.md` (memoria persistente) |
| `kanban/` | ❌ Opcional | Estado del tablero Kanban |

---

## Exclusiones de Source Code

### Directorios excluidos (`EXCLUDE_SOURCE_DIRS`)

| Directorio | Razón |
|------------|-------|
| `node_modules` | Gigabytes de dependencias JS reinstalables |
| `.git` | Historial completo de git (cientos de MB) |
| `__pycache__` | Archivos .pyc compilados (innecesarios) |
| `venv`, `.venv` | Entorno virtual (recreable con uv/pip) |
| `build`, `dist` | Artefactos compilados |
| `.github` | Workflows de CI (no necesarios para ejecutar) |
| `docs`, `website`, `web` | Documentación renderizada |
| `nix`, `docker` | Configuración de contenedores |
| `tui_gateway`, `ui-tui` | Interfaces de usuario adicionales |
| `apps` | Aplicaciones complementarias |
| `optional-mcps`, `optional-skills` | Componentes opcionales |
| `locales`, `assets` | Archivos de traducción/imágenes |

### Extensiones excluidas (`EXCLUDE_SOURCE_EXTS`)

| Extensión | Razón |
|-----------|-------|
| `.jpg`, `.jpeg`, `.png`, `.gif`, `.ico` | Imágenes (grandes, no esenciales) |
| `.woff`, `.woff2`, `.ttf`, `.eot` | Fuentes (reinstalables con pip) |
| `.mp4`, `.webm` | Videos (raros en source code, pero grandes) |

---

## Archivos Opcionales Buscados

### Binarios

| Ruta | Propósito |
|------|-----------|
| `$HERMES_HOME/bin/uv.exe` | Gestor de paquetes uv |
| `$HERMES_HOME/bin/uvw.exe` | uv wrapper Windows |
| `$HERMES_HOME/bin/uvx.exe` | uvx para ejecutar herramientas |
| `~/Desktop/hermes-restore.exe` | Restaurador standalone (para clean OS) |
| `~/Desktop/hermes_restore.py` | Restaurador Python (alternativa) |

### Installer

| Ruta | Propósito |
|------|-----------|
| `junto al script/install.bat` | Instalador one-click para Windows |
| `../install.bat` | Relativo al directorio del script |
| `~/Desktop/hermes-restore-app/src/install.bat` | Ruta alternativa |
