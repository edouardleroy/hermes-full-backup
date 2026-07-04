# Architecture — Hermes Complete Backup

## Visión General

El script `hermes-complete-backup.py` es un **script único, autocontenido y sin dependencias** que empaqueta todo el estado de Hermes Agent en un archivo ZIP listo para restaurar en caso de desastre.

---

## Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│                     hermes-complete-backup.py                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Resolver HERMES_HOME                                     │
│     ├─ ¿Variable de entorno $HERMES_HOME? → usar esa         │
│     └─ ¿Windows? → ~/AppData/Local/hermes                    │
│        ¿Linux/macOS? → ~/.hermes                             │
│                                                             │
│  2. Crear ZIP con 5 secciones:                               │
│     ├─ Config (config.yaml, .env, state.db, skills, cron…)   │
│     ├─ Sessions/Logs (omitido si --quick)                    │
│     ├─ Source code (omitido si --quick)                      │
│     ├─ Binarios (uv.exe, restorer…)                          │
│     └─ Instalador + LEEME.txt                                │
│                                                             │
│  3. Mostrar resumen (tamaño, archivos, ruta)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Estructura del ZIP Generado

```
backup.zip
├── config.yaml              ← Configuración de Hermes
├── .env                     ← Credenciales (API keys, tokens) ⚠️
├── state.db                 ← Base de datos de sesiones SQLite
├── auth.json                ← Tokens OAuth
├── auth.lock                ← Lock de autenticación
├── channel_directory.json   ← Directorio de canales
├── discord_threads.json     ← Hilos de Discord
├── gateway_state.json       ← Estado del gateway
├── gateway.lock             ← Lock del gateway
├── gateway.pid              ← PID del gateway
├── processes.json           ← Procesos en background
├── SOUL.md                  ← Personalidad del agente
├── .hermes_history          ← Historial
├── cron/                    ← Trabajos programados
│   ├── jobs.json
│   └── ...
├── memories/                ← Memorias persistentes
│   ├── MEMORY.md
│   ├── USER.md
│   └── ...
├── kanban/                  ← Estado de tablero Kanban
├── skills/                  ← Skills instalados
│   ├── autonomous-ai-agents/
│   ├── computer-use/
│   ├── creative/
│   └── ...
├── sessions/                ← (solo full backup) Transcripciones
├── logs/                    ← (solo full backup) Logs
├── plugins/                 ← (solo full backup) Plugins
├── profiles/                ← (solo full backup) Perfiles adicionales
├── hermes-agent/            ← (solo full backup) Código fuente
│   ├── pyproject.toml
│   ├── hermes_cli/
│   └── ...
├── bin/
│   ├── uv.exe               ← Gestor de paquetes
│   ├── uvw.exe
│   ├── uvx.exe
├── hermes-restore.exe       ← Restaurador standalone
├── hermes_restore.py        ← Restaurador Python (alternativa)
├── install.bat              ← Instalador one-click (Windows)
└── LEEME.txt                ← Instrucciones dentro del ZIP
```

---

## Decisiones Técnicas

### 1. Sin dependencias externas

Usa solo `zipfile`, `argparse`, `json`, `pathlib`, `os`, `sys`, `datetime` — todo en la stdlib de Python. Cero `pip install`.

### 2. Auto-detección multiplataforma

```python
_DEFAULT_HOME = (
    Path.home() / "AppData" / "Local" / "hermes"   # Windows
    if sys.platform == "win32"
    else Path.home() / ".hermes"                     # Linux / macOS
)
```

### 3. Variable de entorno $HERMES_HOME

Si el usuario tiene `$HERMES_HOME` configurado, se usa ese path. Si no, se cae al default según plataforma. Esto permite:

- Instalaciones personalizadas
- Múltiples perfiles
- CI/CD con rutas temporales

### 4. Exclusión inteligente de directorios

```python
EXCLUDE_SOURCE_DIRS = {
    "node_modules", ".git", "__pycache__", "venv", ".venv",
    "build", "dist", ".github", "docs", ...
}
```

Evita empaquetar gigabytes de `node_modules`, históricos de git, o entornos virtuales.

### 5. Modo --quick

Para backups frecuentes (cada 6h), el modo `--quick` omite:
- Sessions (pueden ser cientos de MB de JSONL)
- Logs
- Código fuente (`hermes-agent/` que se reinstala con `pip install`)

Esto reduce el backup de ~150 MB a ~60 MB.

### 6. Configuración externa vía --json-config

```json
{
    "hermes_home": "/custom/path/hermes",
    "hermes_source": "/custom/path/hermes-agent",
    "restorer_exe": "/tools/hermes-restore.exe",
    "restorer_py": "/tools/hermes_restore.py"
}
```

Útil para:
- CI/CD pipelines
- Instalaciones no estándar
- Override temporal sin editar el script

---

## Consideraciones de Seguridad

| Riesgo | Mitigación |
|--------|-----------|
| El ZIP contiene `.env` con API keys | `LEEME.txt` advierte explícitamente |
| `auth.json` con OAuth tokens | El script no los filtra ni los excluye — es intencional (es un backup de todo) |
| Compartir el ZIP por error | No hay mitigación técnica — es responsabilidad del usuario |
| Path traversal en nombres de archivo | `zipfile.write()` con arcname explícito previene esto |

---

## Compatibilidad

| Plataforma | Estado |
|------------|--------|
| Windows 10/11 | ✅ Probado |
| Linux (Ubuntu, Debian) | ✅ Auto-detecta `~/.hermes` |
| macOS | ✅ Auto-detecta `~/.hermes` |
| CI/CD (GitHub Actions) | ✅ Vía `--json-config` |
