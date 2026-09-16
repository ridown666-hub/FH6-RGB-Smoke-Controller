"""Opt-in, current-user Windows startup registration. No elevation required."""
import subprocess
import sys
from pathlib import Path

KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'
NAME = 'RicardoStonePT_FH6RGB'

def command():
    executable = Path(sys.executable).resolve()
    if getattr(sys, 'frozen', False):
        return subprocess.list2cmdline([str(executable)])
    windowless = executable.with_name('pythonw.exe')
    if windowless.exists():
        executable = windowless
    return subprocess.list2cmdline([str(executable), str(Path(__file__).with_name('app.py').resolve())])

def enabled():
    if sys.platform != 'win32':
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY) as key:
            value, _ = winreg.QueryValueEx(key, NAME)
            return bool(value)
    except FileNotFoundError:
        return False

def set_enabled(value):
    if sys.platform != 'win32':
        raise OSError('Esta opção está disponível no Windows.')
    import winreg
    with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, KEY, 0, winreg.KEY_SET_VALUE) as key:
        if value:
            winreg.SetValueEx(key, NAME, 0, winreg.REG_SZ, command())
        else:
            try:
                winreg.DeleteValue(key, NAME)
            except FileNotFoundError:
                pass
