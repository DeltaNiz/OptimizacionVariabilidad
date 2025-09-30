# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules
block_cipher = None

hiddenimports = (
    collect_submodules('numpy') +
    collect_submodules('pandas') +
    collect_submodules('matplotlib') +
    collect_submodules('PyAstronomy') +
    collect_submodules('numba') +
    collect_submodules('multiprocessing') +
    collect_submodules('concurrent.futures') +
    ['multiprocessing.spawn', 'multiprocessing.pool', 'multiprocessing.queues', 'multiprocessing.synchronize',
     'PyAstronomy.pyTiming', 'PyAstronomy.pyTiming.pyPeriod', 'PyAstronomy.pyTiming.pyPDM']
)

a = Analysis([
    'Frontend/main.py',
],
    pathex=['.'],
    binaries=[],
    datas=[
        ('copiar.py', '.'),
        ('procesofull.py', '.'),
        ('Fase_monocolor.py', '.'),
        ('Analisis.py', '.'),
        ('Frontend/DatosF.py', 'Frontend/'),
        ('Frontend/DatosNF.py', 'Frontend/'),
        ('Frontend/SubirArchivos.py', 'Frontend/'),
        ('media/icono.ico', 'media/'),  # Incluir el icono en formato ICO
        # Agrega aquí otros archivos de datos necesarios
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SODEV-CG',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='media/icono.ico'  # Establecer el icono del ejecutable con múltiples tamaños
)