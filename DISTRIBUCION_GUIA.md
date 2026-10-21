# 📦 Guía de Distribución de EcoSim

Para compartir **EcoSim** con tus compañeros de clase y profesor, tienes las siguientes opciones:

---

## 🌟 Método 1: Un Solo Archivo Ejecutable (.exe) — (¡EL MÁS FÁCIL!)
Tus compañeros **NO necesitan tener Python instalado** ni descomprimir carpetas. Solo reciben un único archivo `.exe` con el ícono de la mascota dorada con gafas de sol, hacen doble clic y juegan.

### Pasos:
1. En esta carpeta, haz doble clic en el archivo:
   `compilar_a_un_solo_exe.bat`
   *(O usa `compilar_a_exe.bat` y presiona ENTER para elegir la opción 1)*.
2. Espera aproximadamente 1 minuto a que PyInstaller finalice.
3. Al terminar, ve a la carpeta:
   `dist\`
4. Verás el archivo:
   `EcoSim.exe` (con el ícono de la mascota feliz de 8-bits).
5. **¡Listo!** Envía directamente ese archivo `EcoSim.exe` por Google Drive, correo, WhatsApp o USB.

---

## 📁 Método 2: Carpeta Ejecutable (.onedir)
Si prefieres que el juego cargue más rápido en computadoras antiguas:
1. Ejecuta `compilar_a_exe.bat` y escribe la opción `2`.
2. Generará la carpeta `dist\EcoSim\`.
3. Comprime esa carpeta en un `.zip` y compártela.

---

## 🐍 Método 3: Enviar el código fuente con Python
Si tus compañeros estudian programación o tienen Python instalado:
1. Comprime toda la carpeta del proyecto en un `.zip`.
2. Diles que ejecuten:
   - `instalar_dependencias.bat` (instala Pygame y Pillow en un clic).
   - `JUGAR.bat` (inicia el juego inmediatamente).

---

## 🎨 Ícono de la Mascota ("Lo haces bien")
El ícono de la aplicación y de la ventana del juego se encuentra en:
- `assets/icon.ico` (Formato icono para Windows con soporte multirresolución de 16x16 a 256x256).
- `assets/icon.png` (Versión PNG utilizada dentro de Pygame en la barra de tareas).
