pyinstaller --onefile driver.spec
copy datamodel\*.xml dist /Y
copy simpler_networks_runtimeconfig.yml dist /Y
