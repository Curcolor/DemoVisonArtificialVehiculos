# Sistema de Detección y Seguimiento de Vehículos - Documentación

Bienvenido a la documentación del Sistema de Detección y Seguimiento de Vehículos.

## Índice de documentos

- [Guía de Usuario](GUIA_USUARIO.md) - Guía completa para el uso del sistema
- [Instalación Manual](INSTALACION_MANUAL.md) - Instrucciones para instalación manual

## Resumen del proyecto

Este sistema permite detectar y hacer seguimiento de vehículos (automóviles, camiones, buses), motos, peatones y vehículos de emergencia utilizando técnicas de visión artificial con OpenCV y YOLOv4.

## Inicio rápido

La forma más sencilla de comenzar es ejecutar el archivo `START.bat` en la carpeta principal del proyecto. Este script instalará las dependencias necesarias, descargará los modelos y le permitirá ejecutar las diferentes funciones del sistema.

## Estructura del proyecto

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
│   └── GUIA_USUARIO.md
│
├── scripts/               # Scripts para arranque fácil
│   └── iniciar.bat
│
├── main.py                # Punto de entrada principal
├── START.bat              # Script de inicio rápido para Windows
└── requirements.txt       # Dependencias del proyecto
```
