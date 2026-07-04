# Hermes Complete Backup — Handoff Package

**Para:** Otro agente Hermes  
**Propósito:** Recrear un script de backup completo y auto-contenido para Hermes Agent  
**Versión:** 1.0.0  

---

## ¿Qué es esto?

Este handoff contiene todo lo que otro Hermes necesita para **entender, recrear y personalizar** el script `hermes-complete-backup.py` en su propia instalación.

El script genera un archivo `.zip` con todo lo necesario para restaurar Hermes desde cero en un sistema operativo limpio:

- Configuración (`config.yaml`, `.env`, `state.db`, `auth.json`)
- Skills, cron jobs, memorias, perfiles
- Código fuente de Hermes Agent
- Binarios (`uv.exe`)
- Script de instalación (`install.bat`)
- Instrucciones de recuperación

---

## Estructura del Handoff

```
hermes-handoff/
├── README.md                       ← Este archivo (punto de entrada)
├── hermes-complete-backup.py       ← El script listo para usar
├── docs/
│   ├── ARCHITECTURE.md             ← Diseño, decisiones técnicas, estructura del ZIP
│   ├── IMPLEMENTATION.md           ← Paso a paso para recrear el script desde cero
│   └── CONFIG-REFERENCE.md         ← Referencia de configuración y paths
├── examples/
│   └── config.example.json         ← Ejemplo de archivo de configuración externo
└── tests/
    └── TEST-PLAN.md                ← Plan de verificación (lo que debe pasar para dar por bueno el script)
```

---

## Quick Start

El script ya está listo para ejecutarse:

```bash
# Ver ayuda
python hermes-complete-backup.py --help

# Backup rápido (solo config + skills, sin source code)
python hermes-complete-backup.py --quick -o ~/test-backup.zip

# Backup completo
python hermes-complete-backup.py -o ~/hermes-full-$(date +%Y%m%d).zip

# Con configuración externa
python hermes-complete-backup.py --json-config config.json
```

---

## Flujo de Implementación para Otro Hermes

1. **Leer** `docs/IMPLEMENTATION.md` — pasos exactos para crear el script
2. **Leer** `docs/ARCHITECTURE.md` — entender el diseño y decisiones
3. **Ejecutar** el script directamente (ya incluido) para probar
4. **Opcional:** Crear el skill con `skill_manage(action='create', ...)` para que quede persistente
5. **Verificar** con `tests/TEST-PLAN.md`

---

## ¿Por qué este enfoque?

| Decisión | Razón |
|----------|-------|
| Script único sin dependencias | Solo `zipfile` + `argparse` (stdlib) — funciona en cualquier Python |
| `$HERMES_HOME` como fuente de verdad | Funciona en Windows, Linux y macOS sin cambios |
| `--json-config` para personalizar | Permite override sin editar el script |
| Aviso de credenciales en LEEME.txt | El ZIP contiene `.env` y `auth.json` — el usuario debe saberlo |
| `--quick` mode | Útil para backups frecuentes sin el peso del source code |

---

## Dependencias

- **Python 3.8+** (solo stdlib — `zipfile`, `argparse`, `json`, `pathlib`)
- **Hermes Agent** instalado (para que `$HERMES_HOME` tenga contenido que respaldar)

Cero dependencias externas. Cero `pip install`.
