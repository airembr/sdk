from unittest.mock import patch
import sys
from airembr.sdk.common.invoker import pip_install, import_package, load_callable, is_installed, is_coroutine

@patch('subprocess.check_call')
def test_pip_install(mock_check_call):
    pip_install("requests")
    mock_check_call.assert_called_with([sys.executable, '-m', 'pip', 'install', 'requests'])
    
    pip_install("requests", upgrade=True)
    mock_check_call.assert_called_with([sys.executable, '-m', 'pip', 'install', 'requests', '-U'])

@patch('importlib.import_module')
def test_import_package(mock_import_module):
    import_package("os")
    mock_import_module.assert_called_with("os")

def test_load_callable():
    import os
    func = load_callable(os, "getpid")
    assert func == os.getpid

def test_is_installed():
    assert is_installed("os")
    assert not is_installed("non_existent_package_12345")

def test_is_coroutine():
    async def async_func():
        pass
    def sync_func():
        pass
    assert is_coroutine(async_func)
    assert not is_coroutine(sync_func)
