# Test Plan — Hermes Complete Backup

Usa este plan para verificar que el script funciona correctamente en cualquier instalación de Hermes.

---

## Prerrequisitos

- [ ] Python 3.8+ instalado (`python --version`)
- [ ] Hermes Agent instalado (el directorio `$HERMES_HOME` existe)
- [ ] Espacio en disco suficiente (~2 GB para backup completo)

---

## Test 1: Ayuda

```bash
python hermes-complete-backup.py --help
```

**Esperado:** Muestra usage con `-o`, `--quick`, `--json-config`

**Resultado:** ⬜ Pasa  ⬜ Fall

---

## Test 2: Backup Rápido

```bash
python hermes-complete-backup.py --quick -o /tmp/test-quick.zip
```

**Esperado:** 
- Exit code 0
- Mensaje "BACKUP COMPLETE" con tamaño y cantidad de archivos
- El ZIP existe

```bash
python -m zipfile -l /tmp/test-quick.zip | head -20
```

**Esperado:** Muestra `config.yaml`, `.env`, `state.db`, `skills/`, etc.

**Resultado:** ⬜ Pasa  ⬜ Fall

---

## Test 3: Backup Completo

```bash
python hermes-complete-backup.py -o /tmp/test-full.zip
```

**Esperado:**
- Exit code 0
- Más archivos que el backup rápido
- Incluye `sessions/`, `logs/`, `hermes-agent/`, `plugins/`, `profiles/`

```bash
echo "Quick files:  $(python -m zipfile -l /tmp/test-quick.zip | wc -l)"
echo "Full files:   $(python -m zipfile -l /tmp/test-full.zip | wc -l)"
```

**Esperado:** Full tiene significativamente más archivos que Quick

**Resultado:** ⬜ Pasa  ⬜ Fall

---

## Test 4: Archivos Críticos

```bash
python -c "
import zipfile
z = zipfile.ZipFile('/tmp/test-full.zip')
names = z.namelist()
critical = ['config.yaml', '.env', 'state.db', 'auth.json']
for c in critical:
    found = c in names
    print(f'  {c:20s} {\"✅\" if found else \"❌\"}'  )
"
```

**Esperado:** Todos los archivos críticos presentes

**Resultado:** ⬜ Pasa  ⬜ Fall

---

## Test 5: Configuración Externa

```bash
# Crear config temporal
echo '{"hermes_home": "/nonexistent/path"}' > /tmp/test-external-config.json

# Correr con esa config
python hermes-complete-backup.py --json-config /tmp/test-external-config.json -o /tmp/test-external.zip 2>&1 | head -5

rm /tmp/test-external-config.json /tmp/test-external.zip
```

**Esperado:** Mensaje "Loaded config from ..." o error de path inexistente

**Resultado:** ⬜ Pasa  ⬜ Fall

---

## Test 6: LEEME.txt Dentro del ZIP

```bash
python -c "
import zipfile
z = zipfile.ZipFile('/tmp/test-full.zip')
readme = z.read('LEEME.txt').decode()
assert 'WARNING' in readme, 'No security warning found'
assert 'RESTORE' in readme, 'No restore instructions found'
print('✅ LEEME.txt contains security warning and restore instructions')
"
```

**Esperado:** El LEEME.txt incluye advertencia de seguridad y pasos de restauración

**Resultado:** ⬜ Pasa  ⬜ Fall

---

## Test 7: Sin $HERMES_HOME (simular)

```bash
# Ejecutar sin $HERMES_HOME para probar auto-detección
env -u HERMES_HOME python hermes-complete-backup.py --quick -o /tmp/test-no-env.zip 2>&1 | head -10
rm /tmp/test-no-env.zip
```

**Esperado:** El script funciona, usa el default de plataforma

**Resultado:** ⬜ Pasa  ⬜ Fall

---

## Test 8: Limpieza

```bash
rm /tmp/test-quick.zip /tmp/test-full.zip
```

**Esperado:** Sin errores

**Resultado:** ⬜ Pasa  ⬜ Fall

---

## Test 9: ZIP Válido (Integridad)

```bash
python -c "
import zipfile
try:
    z = zipfile.ZipFile('/tmp/test-full.zip')
    bad = z.testzip()
    if bad:
        print(f'❌ Corrupt file: {bad}')
    else:
        print('✅ ZIP integrity check passed')
except Exception as e:
    print(f'❌ Cannot open ZIP: {e}')
"
```

**Esperado:** "ZIP integrity check passed"

**Resultado:** ⬜ Pasa  ⬜ Fall

---

## Resumen

| Test | Estado |
|------|--------|
| 1. Ayuda | ⬜ |
| 2. Backup Rápido | ⬜ |
| 3. Backup Completo | ⬜ |
| 4. Archivos Críticos | ⬜ |
| 5. Configuración Externa | ⬜ |
| 6. LEEME.txt | ⬜ |
| 7. Sin $HERMES_HOME | ⬜ |
| 8. Limpieza | ⬜ |
| 9. Integridad ZIP | ⬜ |
| **Total** | **/9** |
