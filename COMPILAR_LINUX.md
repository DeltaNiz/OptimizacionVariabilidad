# Compilación para Linux - SODEV-CG

## � Inicio Rápido

```bash
# 1. Compilar con PyInstaller
pyinstaller portable_linux.spec

# 2. Crear AppImage (máxima compatibilidad)
chmod +x crear_appimage.sh
./crear_appimage.sh

# 3. Probar
./SODEV-CG-x86_64.AppImage
```

---

## �📋 Requisitos en Linux

1. **Python 3.8+** y dependencias del sistema:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3-pip python3-dev python3-tk
   
   # Fedora/RHEL
   sudo dnf install python3-pip python3-devel python3-tkinter
   
   # Arch Linux
   sudo pacman -S python-pip tk
   ```

2. **Dependencias Python**:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

---

## 🚀 Compilar en Linux

### Compilar el ejecutable
```bash
pyinstaller portable_linux.spec
```

**Nota**: Genera una carpeta `dist/SODEV-CG/` con el ejecutable y todas sus dependencias (modo onedir).

### Probar
```bash
cd dist/SODEV-CG
./SODEV-CG
```

---

## 📦 Distribución

### Crear archivo .tar.gz
```bash
cd dist
tar -czf SODEV-CG-Linux.tar.gz SODEV-CG/
```

**Nota**: El resultado será una carpeta con el ejecutable y sus dependencias.

### Crear AppImage (Recomendado - Máxima Compatibilidad)

AppImage crea un **único archivo ejecutable** que funciona en **cualquier** distribución Linux moderna.

**Método Automático (Recomendado):**
```bash
# Dar permisos de ejecución al script
chmod +x crear_appimage.sh

# Ejecutar
./crear_appimage.sh
```

El script:
1. ✅ Descarga `appimagetool` automáticamente
2. ✅ Crea la estructura AppDir
3. ✅ Genera `SODEV-CG-x86_64.AppImage`

**Método Manual:**

**Método Manual:**

1. **Descargar appimagetool**:
   ```bash
   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
   chmod +x appimagetool-x86_64.AppImage
   ```

2. **Crear estructura AppDir**:
   ```bash
   mkdir -p SODEV-CG.AppDir/usr/bin
   cp -r dist/SODEV-CG/* SODEV-CG.AppDir/usr/bin/
   cp media/icono.png SODEV-CG.AppDir/sodev-cg.png
   ```

3. **Crear archivo .desktop**:
   ```bash
   cat > SODEV-CG.AppDir/sodev-cg.desktop << 'EOF'
   [Desktop Entry]
   Name=SODEV-CG
   Exec=SODEV-CG
   Icon=sodev-cg
   Type=Application
   Categories=Science;Education;
   EOF
   ```

4. **Crear AppRun**:
   ```bash
   cat > SODEV-CG.AppDir/AppRun << 'EOF'
   #!/bin/bash
   SELF=$(readlink -f "$0")
   HERE=${SELF%/*}
   cd "${HERE}/usr/bin"
   exec "${HERE}/usr/bin/SODEV-CG" "$@"
   EOF
   chmod +x SODEV-CG.AppDir/AppRun
   ```

5. **Generar AppImage**:
   ```bash
   ARCH=x86_64 ./appimagetool-x86_64.AppImage SODEV-CG.AppDir SODEV-CG-x86_64.AppImage
   ```

**Resultado**: Un archivo `SODEV-CG-x86_64.AppImage` que funciona en casi cualquier distribución Linux.

**Uso del AppImage**:
```bash
chmod +x SODEV-CG-x86_64.AppImage
./SODEV-CG-x86_64.AppImage
```

---

## 🎯 Distribuciones Probadas

- ✅ Ubuntu 20.04+ / Linux Mint 20+
- ✅ Debian 11+
- ✅ Fedora 35+
- ✅ Arch Linux (rolling)
- ✅ openSUSE Leap 15.3+

---

## 🔧 Solución de Problemas

### Error: "Failed to extract PIL/_avif" o "Failed to extract matplotlib"
**Solución**: El archivo `.spec` ahora usa modo "onedir" que evita estos problemas.
Recompila con:
```bash
pyinstaller --clean portable_linux.spec
```
El ejecutable estará en `dist/SODEV-CG/SODEV-CG`

### Error: "libQt5Core.so.5: cannot open shared object file"
```bash
# Ubuntu/Debian
sudo apt-get install libqt5core5a libqt5gui5 libqt5widgets5

# Fedora
sudo dnf install qt5-qtbase qt5-qtbase-gui
```

### Error: "No module named '_tkinter'"
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### El ejecutable no se inicia
```bash
# Dar permisos de ejecución
chmod +x dist/SODEV-CG

# Verificar dependencias
ldd dist/SODEV-CG
```

### Problemas con multiprocessing
Si hay errores con `multiprocessing`, edita `portable_linux.spec` y cambia:
```python
console=False,  # Cambiar a True para ver errores
```

---

## 📂 Archivos

- `portable_complete.spec` → Para Windows
- `portable_macos.spec` → Para macOS
- `portable_linux.spec` → Para Linux (este)
- `media/icono.png` → Icono usado en Linux

---

## ✅ Verificación Post-Compilación

```bash
# Verificar tamaño
ls -lh dist/SODEV-CG

# Verificar dependencias compartidas
ldd dist/SODEV-CG

# Ejecutar
./dist/SODEV-CG
```

---

## 🐧 Notas Específicas de Linux

1. **Portabilidad limitada**: El ejecutable compilado en una distribución puede no funcionar en otras debido a diferencias en bibliotecas del sistema.

2. **Recomendación**: Compila en la distribución más antigua que quieras soportar (ej: Ubuntu 20.04 LTS).

3. **Alternativa AppImage**: Para máxima portabilidad, usa AppImage (incluye todas las dependencias).

4. **Tamaño**: El ejecutable será de ~150-300 MB debido a todas las dependencias científicas (NumPy, Pandas, Matplotlib).

5. **Ubicación de datos**: En Linux, los análisis se guardan en `~/SODEV-CG/data/` (carpeta home del usuario), no dentro del ejecutable.

6. **AppImage**: Si usas AppImage, los archivos temporales se guardan en `/tmp/` y los análisis en `~/SODEV-CG/data/`. El AppImage monta un sistema de archivos de solo lectura, por lo que todo se escribe fuera del ejecutable.

---

## 🎨 Icono de Escritorio (Opcional)

Para agregar un lanzador al menú de aplicaciones:

```bash
# Crear archivo .desktop
cat > ~/.local/share/applications/sodev-cg.desktop << EOF
[Desktop Entry]
Name=SODEV-CG
Comment=Análisis de Variabilidad Estelar
Exec=/ruta/completa/a/SODEV-CG
Icon=/ruta/completa/a/media/icono.png
Terminal=false
Type=Application
Categories=Science;Education;
EOF

# Actualizar base de datos de aplicaciones
update-desktop-database ~/.local/share/applications/
```

---

**Versión**: 0.1.0  
**Plataforma**: Linux (x86_64)  
**Última actualización**: Noviembre 2025
