# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

# Bundle web assets and data template (never bundle .env or private keys!)
# Include app/ai_tutor as data files since modules are dynamically imported
datas = [('app/web', 'app/web'), ('data', 'data')]

binaries = []
hiddenimports = [
    'sqlalchemy',
    'sqlalchemy.orm',
    'sqlalchemy.sql',
    'sqlalchemy.dialects',
    'sqlalchemy.dialects.sqlite',
    'cryptography',
    'cryptography.hazmat',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives.asymmetric',
    'cryptography.hazmat.primitives.asymmetric.ed25519',
    'cryptography.hazmat.primitives.serialization',
    'pydantic',
    'pydantic_core',
    'pydantic_settings',
    'ssl',
    '_ssl',
    'hashlib',
    '_hashlib',
    'certifi',
    'requests',
    'charset_normalizer',
    'idna',
    'urllib3',
    'dotenv',
    'google',
    'google.genai',
    'google.genai.types',
    'google.auth',
    'httpx',
    'httpcore',
    'anyio',
    'sniffio',
    'pyttsx3',
    'pyttsx3.drivers',
    'pyttsx3.drivers.sapi5',
    'pythoncom',
    'pywintypes',
    'win32com',
    'win32com.client',
    'app.ai_tutor.main',
    'app.ai_tutor.router',
    'app.ai_tutor.schemas',
    'app.ai_tutor.services.ai_settings_resolver',
    'app.ai_tutor.services.response_validator',
    'app.ai_tutor.services.tts',
    'app.ai_tutor.services.providers.base',
    'app.ai_tutor.services.providers.provider_manager',
    'app.ai_tutor.services.providers.gemini',
    'app.ai_tutor.services.providers.ollama',
    'app.ai_tutor.services.providers.remote_server',
    'app.ai_tutor.services.providers',
    'app.database.database',
    'app.database.models',
    'app.database.__init__',
    'app.services.settings_service',
    'app.services.licensing.client',
    'app.services.licensing.crypto',
    'app.services.licensing.machine_fingerprint',
    'app.services.licensing.api',
    'uvicorn',
    'uvicorn.logging',
    'uvicorn._logging',
    'uvicorn.loops',
    'uvicorn.loops.asyncio',
    'uvicorn.loops.none',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'uvicorn.middleware',
    'uvicorn.middleware.asgi2',
    'uvicorn.middleware.message_logger',
    'uvicorn.middleware.proxy_headers',
    'uvicorn.middleware.wsgi',
    'uvicorn.config',
    'uvicorn.main',
    'uvicorn.server',
    'uvicorn.supervisors',
    'h11',
    'h11._connection',
    'h11._events',
    'h11._readers',
    'h11._writers',
    'h11._util',
    'h11._state',
    'h11._headers',
    'h11._receivebuffer',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'fastapi',
    'fastapi.routing',
    'fastapi.middleware',
    'fastapi.middleware.cors',
    'fastapi.responses',
    'fastapi.exceptions',
    'starlette',
    'starlette.applications',
    'starlette.routing',
    'starlette.middleware',
    'starlette.middleware.cors',
    'starlette.responses',
    'starlette.exceptions',
    'starlette.types',
]

# Collect full packages
for pkg in ['pyside6', 'uvicorn', 'fastapi', 'certifi', 'google.genai', 'httpx', 'httpcore', 'anyio', 'pyttsx3', 'h11', 'sqlalchemy']:
    try:
        tmp_ret = collect_all(pkg)
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]
    except Exception as e:
        print(f"[Warning] Hook collect_all({pkg}) notice: {e}")

# Explicitly bundle OpenSSL DLLs from the uv-managed Python installation
_ssl_search_dirs = []

# uv Python base (primary source)
_uv_python = r'C:\Users\USER\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\DLLs'
if os.path.isdir(_uv_python):
    _ssl_search_dirs.append(_uv_python)

# Fallback: walk common locations
for _candidate in [
    os.path.join(os.path.dirname(sys.executable), '..', 'DLLs'),
    os.path.join(sys.prefix, 'DLLs'),
    os.path.dirname(sys.executable),
]:
    _candidate = os.path.normpath(_candidate)
    if os.path.isdir(_candidate) and _candidate not in _ssl_search_dirs:
        _ssl_search_dirs.append(_candidate)

_ssl_dll_names = [
    'libssl-3-x64.dll', 'libcrypto-3-x64.dll',
    'libssl-3.dll',     'libcrypto-3.dll',
    'libssl-1_1-x64.dll', 'libcrypto-1_1-x64.dll',
    '_ssl.pyd', '_hashlib.pyd',
]
for _search in _ssl_search_dirs:
    for _dll in _ssl_dll_names:
        _path = os.path.join(_search, _dll)
        if os.path.isfile(_path) and not any(_path == b[0] for b in binaries):
            binaries.append((_path, '.'))
            print(f'[SSL] Bundling: {_path}')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LLS-CBT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app/web/images/company_logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LLS-CBT',
)
