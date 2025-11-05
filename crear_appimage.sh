#!/bin/bash
# Script para crear AppImage de SODEV-CG
# Debe ejecutarse DESPUÉS de compilar con PyInstaller
# Uso: ./crear_appimage.sh

set -e  # Salir si hay algún error

echo "=================================="
echo "  Creador de AppImage - SODEV-CG"
echo "=================================="
echo ""

# Verificar que existe la compilación
if [ ! -d "dist/SODEV-CG" ]; then
    echo "❌ Error: No se encuentra dist/SODEV-CG"
    echo "   Primero compila con: pyinstaller portable_linux.spec"
    exit 1
fi

echo "✓ Compilación encontrada en dist/SODEV-CG"

# Descargar appimagetool si no existe
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo ""
    echo "📥 Descargando appimagetool..."
    wget -q --show-progress https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
    echo "✓ appimagetool descargado"
else
    echo "✓ appimagetool ya existe"
fi

# Limpiar AppDir anterior si existe
if [ -d "SODEV-CG.AppDir" ]; then
    echo ""
    echo "🧹 Limpiando AppDir anterior..."
    rm -rf SODEV-CG.AppDir
fi

# Crear estructura AppDir
echo ""
echo "📁 Creando estructura AppDir..."
mkdir -p SODEV-CG.AppDir/usr/bin
mkdir -p SODEV-CG.AppDir/usr/lib
mkdir -p SODEV-CG.AppDir/usr/share/applications
mkdir -p SODEV-CG.AppDir/usr/share/icons/hicolor/256x256/apps

# Copiar ejecutable y dependencias
echo "📦 Copiando archivos..."
cp -r dist/SODEV-CG/* SODEV-CG.AppDir/usr/bin/

# Copiar icono
if [ -f "media/icono.png" ]; then
    cp media/icono.png SODEV-CG.AppDir/sodev-cg.png
    cp media/icono.png SODEV-CG.AppDir/usr/share/icons/hicolor/256x256/apps/sodev-cg.png
    echo "✓ Icono copiado"
else
    echo "⚠️  Advertencia: No se encontró media/icono.png"
fi

# Crear archivo .desktop
echo ""
echo "📝 Creando archivo .desktop..."
cat > SODEV-CG.AppDir/sodev-cg.desktop << 'EOF'
[Desktop Entry]
Name=SODEV-CG
Comment=Análisis de Variabilidad Estelar
Exec=SODEV-CG
Icon=sodev-cg
Type=Application
Categories=Science;Education;Astronomy;
Terminal=false
EOF

cp SODEV-CG.AppDir/sodev-cg.desktop SODEV-CG.AppDir/usr/share/applications/

# Crear AppRun
echo "🔧 Creando AppRun..."
cat > SODEV-CG.AppDir/AppRun << 'EOF'
#!/bin/bash
# AppRun para SODEV-CG

SELF=$(readlink -f "$0")
HERE=${SELF%/*}

# Configurar variables de entorno
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"

# Ejecutar aplicación
cd "${HERE}/usr/bin"
exec "${HERE}/usr/bin/SODEV-CG" "$@"
EOF

chmod +x SODEV-CG.AppDir/AppRun

# Verificar estructura
echo ""
echo "✓ Estructura AppDir creada:"
ls -la SODEV-CG.AppDir/

# Generar AppImage
echo ""
echo "🔨 Generando AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage SODEV-CG.AppDir SODEV-CG-x86_64.AppImage

# Verificar resultado
if [ -f "SODEV-CG-x86_64.AppImage" ]; then
    chmod +x SODEV-CG-x86_64.AppImage
    SIZE=$(du -h SODEV-CG-x86_64.AppImage | cut -f1)
    
    echo ""
    echo "=================================="
    echo "✅ ¡AppImage creado exitosamente!"
    echo "=================================="
    echo ""
    echo "📦 Archivo: SODEV-CG-x86_64.AppImage"
    echo "📊 Tamaño: $SIZE"
    echo ""
    echo "Para probar:"
    echo "  ./SODEV-CG-x86_64.AppImage"
    echo ""
    echo "Para distribuir:"
    echo "  Los usuarios solo necesitan:"
    echo "  1. Descargar SODEV-CG-x86_64.AppImage"
    echo "  2. chmod +x SODEV-CG-x86_64.AppImage"
    echo "  3. ./SODEV-CG-x86_64.AppImage"
    echo ""
else
    echo ""
    echo "❌ Error: No se pudo crear el AppImage"
    exit 1
fi
