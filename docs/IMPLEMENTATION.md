# Implementation Guide

**Para:** Un agente Hermes que quiera recrear este script desde cero  
**Objetivo:** Escribir, verificar y registrar el script `hermes-complete-backup.py` en su propia instalación

---

## Fase 1: Entender el Problema

Antes de escribir código, responde estas preguntas:

1. ¿Dónde vive Hermes en este sistema?
   - `echo $HERMES_HOME`
   - Si no está definido: Windows → `~/AppData/Local/hermes`, Linux/macOS → `~/.hermes`
2. ¿Qué archivos son críticos para restaurar Hermes?
3. ¿Qué se puede omitir en un backup rápido?
4. ¿Cómo se asegura el usuario de que el ZIP no contiene secretos que no deba compartir?

---

## Fase 2: Escribir el Script

El script completo está en `docs/hermes-complete-backup.py` dentro de este handoff.  
Puedes copiarlo directamente o recrearlo siguiendo la estructura de abajo.

### Estructura Mínima del Código

```python
#!/usr/bin/env python3
"""
Hermes Complete Backup — self-contained backup for disaster recovery.
"""

import os, sys, zipfile, argparse, json
from pathlib import Path
from datetime import datetime

# 1. Config — paths con auto-detección
_DEFAULT_HOME = (
    Path.home() / "AppData" / "Local" / "hermes" if sys.platform == "win32"
    else Path.home() / ".hermes"
)
HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(_DEFAULT_HOME)))

# 2. Listas de archivos esenciales y directorios a excluir
ESSENTIAL_FILES = ["config.yaml", ".env", "state.db", "auth.json", ...]
EXCLUDE_SOURCE_DIRS = {"node_modules", ".git", "__pycache__", ...}

# 3. Función add_file — agrega un archivo al ZIP
def add_file(zf, arcname, src):
    ...

# 4. Función add_dir — agrega un directorio recursivamente
def add_dir(zf, prefix, src, exclude_dirs=None, exclude_exts=None):
    ...

# 5. Función create_backup — lógica principal
def create_backup(output_path, quick=False):
    with zipfile.ZipFile(str(output_path), "w", zipfile.ZIP_DEFLATED) as zf:
        # Paso 1: Config
        # Paso 2: Sessions (omitir si --quick)
        # Paso 3: Source code (omitir si --quick)
        # Paso 4: Binarios
        # Paso 5: Instalador + LEEME.txt

# 6. CLI con argparse
def main():
    parser = argparse.ArgumentParser(...)
    ...

if __name__ == "__main__":
    sys.exit(main())
```

### Orden para escribir

1. **Config y paths** — `_DEFAULT_HOME`, `HERMES_HOME`, `ESSENTIAL_FILES`, `EXCLUDE_SOURCE_DIRS`
2. **Utilidades** — `add_file()`, `add_dir()`, `cprint()`
3. **Lógica principal** — `create_backup()` con los 5 pasos
4. **CLI** — `argparse` con `-o`, `--quick`, `--json-config`
5. **README** — `_readme()` que va dentro del ZIP

---

## Fase 3: Verificar

Ejecuta estos comandos para confirmar que todo funciona:

```bash
# 1. Help
python hermes-complete-backup.py --help

# 2. Backup rápido (no toca tus datos, solo lee)
python hermes-complete-backup.py --quick -o /tmp/verify-quick.zip
python -m zipfile -l /tmp/verify-quick.zip | head -20
echo "Zip size: $(du -h /tmp/verify-quick.zip | cut -f1)"

# 3. Backup completo (si hay espacio)
python hermes-complete-backup.py -o /tmp/verify-full.zip
python -m zipfile -l /tmp/verify-full.zip | wc -l
echo "Files: $(python -m zipfile -l /tmp/verify-full.zip | wc -l)"

# 4. Limpiar
rm /tmp/verify-quick.zip /tmp/verify-full.zip
```

---

## Fase 4: Registrar como Skill (Opcional)

Si quieres que el script quede disponible para futuras sesiones:

```python
skill_manage(
    action='create',
    name='hermes-complete-backup',
    category='autonomous-ai-agents',
    content='''
---
name: hermes-complete-backup
description: Create a self-contained Hermes Agent backup script for disaster recovery
---

# Instructions
Place the script at ~/.hermes/scripts/hermes-complete-backup.py
...''')
```

O más fácil — instala el script directamente:

```bash
cp hermes-complete-backup.py ~/.hermes/scripts/
```

Y luego programa el cron job:

```python
cronjob(
    action='create',
    name='hermes-backup',
    schedule='every 6h',
    script='hermes-complete-backup.py',
    no_agent=True,
    deliver='local'
)
```

---

## Fase 5: Personalizar

Edita estas secciones si tu instalación es atípica:

| Variable | Dónde | Qué cambiar |
|----------|-------|-------------|
| `_DEFAULT_HOME` | Al inicio del script | Si tu Hermes vive en otra ruta |
| `ESSENTIAL_FILES` | Config | Si agregaste/quitaste archivos en `$HERMES_HOME` |
| `EXCLUDE_SOURCE_DIRS` | Config | Si tu source code tiene directorios grandes extra |
| `RESTORER_EXE` / `RESTORER_PY` | Config | Si el restaurador está en otra ruta |
| `INSTALL_BAT_CANDIDATES` | Config | Si tu install.bat está en otro lado |

Para cambios temporales, usa `--json-config`:

```bash
echo '{"hermes_home": "/opt/hermes"}' > config.json
python hermes-complete-backup.py --json-config config.json
```

---

## Referencia: Archivos en $HERMES_HOME

```
$HERMES_HOME/
├── config.yaml              → Configuración principal
├── .env                     → Variables de entorno (API keys)
├── state.db                 → SQLite con sesiones
├── auth.json                → Tokens de autenticación
├── cron/jobs.json           → Trabajos programados
├── memories/MEMORY.md       → Memoria persistente del agente
├── memories/USER.md         → Perfil del usuario
├── skills/                  → Skills instalados
│   ├── autonomous-ai-agents/
│   ├── computer-use/
│   └── ...
├── sessions/                → Transcripciones de conversaciones
├── logs/                    → Logs del gateway
├── profiles/                → Perfiles adicionales de Hermes
├── plugins/                 → Plugins instalados
├── kanban/                  → Estado del tablero Kanban
├── hermes-agent/            → Código fuente (clonado/instalado)
├── bin/
│   ├── uv.exe
│   ├── uvw.exe
│   └── uvx.exe
└── scripts/                 → Scripts para cron jobs
```

---

## Checklist de Implementación

- [ ] Leer ARCHITECTURE.md
- [ ] Ejecutar script existente (`--help`, `--quick`)
- [ ] Entender qué archivos hay en tu `$HERMES_HOME`
- [ ] (Opcional) Recrear el script desde cero usando la estructura de Fase 2
- [ ] Verificar backup rápido
- [ ] Verificar backup completo
- [ ] Registrar como skill o copiar a `~/.hermes/scripts/`
- [ ] Programar cron job
- [ ] Confirmar que el ZIP se puede inspeccionar con `python -m zipfile -l`
