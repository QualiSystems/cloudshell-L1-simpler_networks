# -*- mode: python -*-
block_cipher = None

import os
import PyInstaller.utils.hooks

CS_L1_NETCORE = "../cloudshell-L1-networking-core"

HOME = "C:\Github\cloudshell-L1-simpler_networks"

def add_data_files(related_path, root_path="."):

    path = os.path.join(root_path, related_path)
    templates = []
    for resp_temp_file in os.listdir(path):
        templates.append((os.path.join(related_path, resp_temp_file),
                          os.path.join(path, resp_temp_file),
                          "DATA"))
    return templates

a = Analysis(['main.py'],
             pathex=[os.path.join(HOME, "cloudshell-core"), os.path.join(HOME, "cloudshell-cli"),
             os.path.join(HOME, "cloudshell-L1-networking-core"), os.path.join(HOME, "cloudshell-L1-simpler_networks")],
             binaries=None,
             datas=PyInstaller.utils.hooks.collect_data_files('cloudshell.core.logger') + \
             PyInstaller.utils.hooks.collect_data_files('simpler_networks'),
             hiddenimports=PyInstaller.utils.hooks.collect_submodules('cloudshell-cli') + \
             PyInstaller.utils.hooks.collect_submodules('paramiko') + [
                "simpler_networks"
             ] + PyInstaller.utils.hooks.collect_submodules('cloudshell'),
             hookspath=["..\cloudshell-cli\."],
             runtime_hooks=None,
             excludes=["cloudshell.snmp", "cloudshell.shell", "cloudshell.networking"],
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries + add_data_files("cloudshell/layer_one/core/response/templates", CS_L1_NETCORE) + \
          add_data_files("cloudshell/layer_one/core/response/resource_info/templates", CS_L1_NETCORE),
          a.zipfiles,
          a.datas,
          name='SIMPLER NETWORKS',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          version='version.txt',
          icon=os.path.join(CS_L1_NETCORE, "img/icon.ico")
          )

