from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# Modules to EXCLUDE from Cython compilation (network I/O, dynamic imports, async)
EXCLUDE_PATTERNS = [
    "app.ai_tutor.services.providers",
    "app.ai_tutor.services.tts",
    "app.ai_tutor.router",
    "app.ai_tutor.main",
    "app.ai_tutor.schemas",
    "app.ai_tutor.services.ai_settings_resolver",
    "app.ai_tutor.services.response_validator",
    "app.services.licensing.client",
    "app.services.licensing.crypto",
    "app.services.licensing.machine_fingerprint",
    "app.services.licensing.api",
    "app.services.settings_service",
    "app.bridge.exam_bridge",
    "app.bridge.question_import_bridge",
    "app.database.database",
    "app.database.models",
]

def should_exclude(mod_path: str) -> bool:
    for pattern in EXCLUDE_PATTERNS:
        if mod_path.startswith(pattern):
            return True
    return False

extensions = []
for root, dirs, files in os.walk("app"):
    for f in files:
        if f.endswith(".py"):
            py_path = os.path.join(root, f)
            mod_path = os.path.splitext(py_path)[0].replace(os.sep, ".")
            if not should_exclude(mod_path):
                extensions.append(Extension(mod_path, [py_path]))

ext_modules = cythonize(
    extensions,
    compiler_directives={"language_level": "3"},
)

setup(
    name="lls-cbt",
    packages=["app"],
    ext_modules=ext_modules,
)