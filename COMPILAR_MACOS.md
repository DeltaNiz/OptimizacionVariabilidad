# Compilación para macOS - SODEV-CG

## ⚠️ IMPORTANTE
PyInstaller **NO permite compilación cruzada**:
- No puedes compilar para macOS desde Windows
- Necesitas un Mac para generar el `.app`

---

## 📋 Requisitos en macOS

1. **Xcode Command Line Tools**:
   ```bash
   xcode-select --install
   ```

2. **Python y dependencias**:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller pillow
   ```

---

## 🚀 Compilar en macOS

### Paso 1: Generar icono .icns (solo primera vez)
```bash
python generar_icono_macos.py
```

### Paso 2: Compilar la aplicación
```bash
pyinstaller portable_macos.spec
```

### Paso 3: Probar
```bash
open dist/SODEV-CG.app
```

---

## 📦 Distribución

### Crear DMG (recomendado)
```bash
hdiutil create -volname "SODEV-CG" \
  -srcfolder dist/SODEV-CG.app \
  -ov -format UDZO \
  dist/SODEV-CG.dmg
```

### O crear ZIP
```bash
cd dist
zip -r SODEV-CG-macOS.zip SODEV-CG.app
```

---

## 📂 Archivos

- `portable_complete.spec` → Para Windows (mantener sin cambios)
- `portable_macos.spec` → Para macOS (nuevo)
- `generar_icono_macos.py` → Genera icono .icns
- `media/icono.icns` → Icono para macOS (se genera automáticamente)

---

## ✅ Flujo de Trabajo

### En Windows (como siempre):
```powershell
pyinstaller portable_complete.spec
# Genera: dist/SODEV-CG.exe
```

### En macOS (nuevo):
```bash
# Primera vez:
python generar_icono_macos.py

# Compilar:
pyinstaller portable_macos.spec
# Genera: dist/SODEV-CG.app
```

---

## 🆘 Problemas Comunes

**"No such file: media/icono.icns"**
→ Ejecuta primero: `python generar_icono_macos.py`

**"App no se abre" (macOS Gatekeeper)**
→ Ejecuta: `xattr -cr dist/SODEV-CG.app`

**"iconutil: command not found"**
→ Instala Xcode Command Line Tools: `xcode-select --install`
