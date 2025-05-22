# Guía de Usuario - Sistema de Detección y Seguimiento de Vehículos

## Introducción

Este sistema permite detectar y hacer seguimiento de vehículos (automóviles, camiones, buses), motos, peatones y vehículos de emergencia utilizando técnicas de visión artificial. El programa utiliza dos enfoques diferentes para la detección:

1. **YOLOv4**: Un modelo de red neuronal convolucional que puede detectar y clasificar vehículos con alta precisión.
2. **Sustracción de Fondo**: Un método más simple que funciona bien cuando la cámara está estática.

## Estructura del proyecto

El proyecto se ha organizado en carpetas para facilitar su uso:

- **src/**: Contiene el código fuente principal
- **models/**: Almacena los modelos de YOLOv4
- **tools/**: Herramientas de calibración y utilidades
- **docs/**: Documentación del proyecto
- **scripts/**: Scripts de arranque y utilidades

## Requisitos

- Python 3.7 o superior
- Cámara web o archivo de video
- Windows, macOS o Linux

## Instalación rápida

En Windows, simplemente ejecute el archivo `START.bat` en la raíz del proyecto. Este script:
1. Instalará todas las dependencias necesarias
2. Descargará los modelos de YOLO automáticamente si no existen
3. Mostrará un menú para ejecutar las diferentes funciones del sistema

## Uso Básico

### Método 1: Usando el script de inicio rápido

1. Ejecute `START.bat` en la carpeta principal
2. Seleccione una opción del menú:
   - **Opción 1**: Detección en tiempo real (cámara)
   - **Opción 2**: Detección en archivo de video
   - **Opción 3**: Calibrar parámetros
   - **Opción 4**: Salir

### Método 2: Ejecución directa desde la línea de comandos

#### Iniciar con la cámara web

```bash
python main.py --input 0
```

#### Utilizar un archivo de video

```bash
python main.py --input ruta_del_video.mp4
```

#### Definir una región de interés (ROI)

```bash
python main.py --input ruta_del_video.mp4 --roi 100,100,500,300
```

Donde `100,100,500,300` representa `x,y,ancho,alto` de la región.

#### Guardar el resultado

```bash
python main.py --input ruta_del_video.mp4 --output resultado.mp4
```

## Calibración

El sistema incluye una herramienta de calibración que permite ajustar los parámetros para optimizar la detección:

### Método 1: Desde el menú de inicio

1. Ejecute `START.bat`
2. Seleccione la opción 3 (Calibrar parámetros)
3. Elija entre cámara o archivo de video

### Método 2: Ejecución directa

```bash
python tools/calibracion.py --input ruta_del_video.mp4
```

### Uso de la ventana de calibración:

1. Arrastre el ratón para seleccionar una región de interés (ROI)
2. Ajuste los parámetros con las barras deslizantes:
   - **History**: Historial para el sustractor de fondo (mayor valor: adaptación más lenta)
   - **Threshold**: Umbral para detección de cambios (menor valor: más sensible)
   - **Area Min**: Área mínima de los objetos a detectar (filtro de ruido)
   - **Umbral**: Valor para binarizar la máscara (mayor valor: menos sombras)
3. Presione 's' para guardar la configuración
4. Presione 'r' para restablecer la ROI
5. Presione 'q' para salir

## Parámetros Recomendados

- **Entorno controlado** (parqueadero, entrada residencial):
  - History: 100-200
  - Threshold: 20-30
  - Area Min: 500-1000

- **Entorno con mucho movimiento** (carretera, avenida):
  - History: 200-300
  - Threshold: 30-50
  - Area Min: 800-1500

## Teclas Durante la Ejecución

- **q**: Salir del programa
- **Esc**: Salir del programa

## Resolución de Problemas

- **Muchas falsas detecciones**: Aumente el valor de Area Min y Threshold
- **No detecta objetos**: Disminuya el valor de Threshold
- **Objetos se detectan intermitentemente**: Aumente el valor de History
- **Error al cargar YOLO**: Ejecute `python descargar_modelos.py` para descargar los archivos necesarios

## Consideraciones Importantes

1. La cámara debe estar **estática** para que la sustracción de fondo funcione correctamente.
2. Una buena iluminación mejora significativamente la detección.
3. Definir una región de interés adecuada mejora el rendimiento y precisión.
4. Para obtener mejores resultados, calibre los parámetros para su entorno específico.

## Recursos Adicionales

Para más información sobre los conceptos utilizados en este proyecto:
- [OpenCV Documentation](https://docs.opencv.org/4.5.0/)
- [YOLOv4 Paper](https://arxiv.org/abs/2004.10934)
- [Background Subtraction Methods](https://docs.opencv.org/4.5.0/d1/dc5/tutorial_background_subtraction.html)
