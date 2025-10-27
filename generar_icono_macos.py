#!/usr/bin/env python3
"""
Script para generar icono .icns para macOS desde PNG
Solo funciona en macOS con iconutil instalado

Uso:
    python generar_icono_macos.py
"""

import os
import sys
import subprocess
from pathlib import Path

def generar_icns():
    """Genera archivo .icns desde PNG usando iconutil de macOS"""
    
    # Verificar que estamos en macOS
    if sys.platform != 'darwin':
        print("❌ Este script solo funciona en macOS")
        print("   En Windows, el icono .icns no es necesario")
        return False
    
    # Rutas
    base_dir = Path(__file__).parent
    png_path = base_dir / 'media' / 'icono.png'
    icns_path = base_dir / 'media' / 'icono.icns'
    iconset_dir = base_dir / 'media' / 'icono.iconset'
    
    # Verificar que existe el PNG
    if not png_path.exists():
        print(f"❌ No se encuentra: {png_path}")
        return False
    
    print(f"✓ PNG encontrado: {png_path}")
    
    try:
        from PIL import Image
        
        # Cargar imagen
        img = Image.open(png_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Crear directorio iconset
        iconset_dir.mkdir(exist_ok=True)
        print(f"✓ Creando iconset temporal...")
        
        # Tamaños estándar para macOS
        sizes = [(16, 16), (32, 32), (128, 128), (256, 256), (512, 512)]
        
        for size in sizes:
            # Versión normal
            resized = img.resize(size, Image.Resampling.LANCZOS)
            filename = f"icon_{size[0]}x{size[1]}.png"
            resized.save(iconset_dir / filename)
            print(f"  ✓ {filename}")
            
            # Versión @2x (Retina)
            if size[0] <= 512:
                double_size = (size[0] * 2, size[1] * 2)
                resized_2x = img.resize(double_size, Image.Resampling.LANCZOS)
                filename_2x = f"icon_{size[0]}x{size[1]}@2x.png"
                resized_2x.save(iconset_dir / filename_2x)
                print(f"  ✓ {filename_2x}")
        
        # Ejecutar iconutil
        print("\n✓ Generando .icns con iconutil...")
        result = subprocess.run(
            ['iconutil', '-c', 'icns', str(iconset_dir), '-o', str(icns_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Icono generado: {icns_path}")
            
            # Limpiar iconset temporal
            import shutil
            shutil.rmtree(iconset_dir)
            print("✓ Limpieza completada")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
            
    except ImportError:
        print("❌ Pillow no está instalado")
        print("   Instala con: pip install Pillow")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Generador de Icono .icns para macOS")
    print("=" * 60 + "\n")
    
    if generar_icns():
        print("\n✅ ¡Listo! Ahora puedes compilar con:")
        print("   pyinstaller portable_macos.spec")
    else:
        print("\n❌ Error generando icono")
        sys.exit(1)
