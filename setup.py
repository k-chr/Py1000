from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [], include_files= ['images/', 'sounds/'])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable(
        script='main.py',
        base=base,
        targetName = 'Py1000',
        icon="icon.ico"  
    )
]

setup(
      name='Py1000',
      version = '1.0',
      description = '"Py1000 - the card game"',
      author="Limak & Hedgehog",
      options = dict(build_exe = buildOptions, bdist_msi = {'all_users':True,
                                                            'initial_target_dir':'C:\\Program Files\\Py1000',
                                                            'install_icon':'installer_icon.ico',
                                                            }),
      executables = executables
)
