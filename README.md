# Generador de Iconos Comerciales

Aplicacion sencilla en Python/Tkinter para generar iconos circulares con el numero de comercial.

## Uso

Instala dependencias:

```powershell
python -m pip install -r requirements.txt
```

Ejecuta la aplicacion:

```powershell
python .\icono.py
```

## Generar EXE para Windows

La forma recomendada es generar una carpeta de aplicacion con PyInstaller, no un unico `.exe`.
Suele dar menos falsos positivos en antivirus corporativos porque el ejecutable no tiene que
autoextraerse en una carpeta temporal.

```powershell
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1
```

El resultado queda en:

```text
dist\GeneradorIconos\GeneradorIconos.exe
```

## Recomendaciones para evitar falsos positivos

- Usa `--onedir` o el modo por defecto de PyInstaller, como hace `build_exe.ps1`.
- Evita `--onefile`, porque autoextrae archivos en tiempo de ejecucion y muchos antivirus lo miran con mas sospecha.
- Evita UPX. El script usa `--noupx`.
- Compila siempre desde un entorno virtual limpio.
- No descargues dependencias desde sitios no oficiales.
- Si la empresa tiene antivirus gestionado, pide a IT que permita la carpeta o el hash del ejecutable.
- Para distribucion interna seria, lo ideal es firmar el ejecutable con un certificado de codigo.

Ningun metodo puede garantizar que un antivirus no avise, pero estas practicas reducen bastante los falsos positivos.
