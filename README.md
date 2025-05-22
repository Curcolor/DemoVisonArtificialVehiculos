# Sistema de Detección y Seguimiento de Vehículos

Este Demo implementa un sistema de detección y seguimiento de vehículos (automóviles, camiones, buses), motos, peatones y vehículos de emergencia utilizando técnicas de visión artificial con OpenCV y Python.

## Características principales

- Detección de múltiples tipos de objetos en tiempo real
- Seguimiento de objetos con asignación de IDs únicos
- Conteo de objetos por categoría
- Definición de zonas de interés personalizables
- Interfaz gráfica para visualización de resultados

## Estructura del proyecto

El proyecto está organizado en las siguientes carpetas:

```
DemoVisonArtificialVehiculos/
│
├── src/                   # Código fuente principal
│   ├── detector.py        # Detector de objetos
│   ├── rastreador.py      # Rastreador de objetos
│   └── utils.py           # Utilidades y funciones auxiliares
│
├── models/                # Modelos pre-entrenados
│   ├── yolov4.weights
│   ├── yolov4.cfg
│   ├── yolov4-tiny.weights
│   ├── yolov4-tiny.cfg
│   └── coco.names
│
├── tools/                 # Herramientas auxiliares
│   ├── calibracion.py     # Herramienta de calibración
│   └── descargar_modelos.py  # Script para descargar modelos
│
├── docs/                  # Documentación
│   └── GUIA_USUARIO.md    # Guía detallada del usuario
│
├── scripts/               # Scripts para arranque fácil
│   └── iniciar.bat        # Script de inicio (Windows)
│
├── main.py                # Punto de entrada principal
├── START.bat              # Script de inicio rápido para Windows
└── requirements.txt       # Dependencias del proyecto
```

## Requisitos

- Python 3.7+
- OpenCV 4.5+
- NumPy

## Instalación rápida

En Windows, simplemente ejecute:

```
START.bat
```

Esto instalará todas las dependencias, descargará los modelos necesarios y le dará opciones para ejecutar el programa.

## Instalación manual

```bash
# Instalar dependencias
pip install -r requirements.txt

# Descargar modelos YOLO
python tools/descargar_modelos.py
```

## Uso

```bash
# Detección con cámara
python main.py --input 0

# Detección con archivo de video
python main.py --input ruta_del_video.mp4

# Guardar resultados
python main.py --input ruta_del_video.mp4 --output resultado.mp4

# Definir región de interés
python main.py --input ruta_del_video.mp4 --roi 100,100,500,300
```
