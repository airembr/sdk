import os
import importlib

_cached = None  # cache the loaded module

def import_package():
    global _cached
    if _cached is not None:
        return _cached

    pkg = 'pararun_os' if os.getenv('LICENSE') else 'pararun'
    try:
        _cached = importlib.import_module(pkg)
    except ModuleNotFoundError:
        # fallback to the other one
        fallback = 'pararun' if pkg == 'pararun_os' else 'pararun_os'
        _cached = importlib.import_module(fallback)

    return _cached
