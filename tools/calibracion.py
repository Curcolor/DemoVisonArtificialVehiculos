import cv2
import numpy as np
import argparse
import os
import time
import sys
import json

# Añadir la ruta principal al path para importar desde src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils import cargar_configuracion, guardar_configuracion, aplicar_roi

def main():
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Calibración del sistema de detección')
    parser.add_argument('--input', type=str, default='0', help='Ruta al video de entrada o ID de la cámara (por defecto: 0)')
    args = parser.parse_args()
    
    # Cargar configuración existente si hay
    config = cargar_configuracion()
    
    # Cargar el video
    if args.input.isdigit():
        cap = cv2.VideoCapture(int(args.input))
    else:
        cap = cv2.VideoCapture(args.input)
    
    # Comprobar que se ha abierto correctamente
    if not cap.isOpened():
        print("Error al abrir la fuente de video")
        return
    
    # Obtener dimensiones del video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Cambiar tamaño si es necesario
    if width > 1280:
        width = 1280
        height = 720
        
    # Crear una ventana para los controles
    cv2.namedWindow('Calibracion')
    
    # Crear controles deslizantes
    cv2.createTrackbar('History', 'Calibracion', 200, 500, lambda x: None)
    cv2.createTrackbar('Threshold', 'Calibracion', 30, 100, lambda x: None)
    cv2.createTrackbar('Area Min', 'Calibracion', 800, 5000, lambda x: None)
    cv2.createTrackbar('Umbral', 'Calibracion', 254, 255, lambda x: None)
    
    # Variable para guardar la ROI seleccionada
    roi_seleccionada = False
    roi = [0, 0, width, height]  # [x, y, w, h]
    
    # Función para manejar eventos del mouse
    def seleccionar_roi(event, x, y, flags, param):
        nonlocal roi, roi_seleccionada
        
        if event == cv2.EVENT_LBUTTONDOWN:
            roi = [x, y, 0, 0]
            roi_seleccionada = False
            
        elif event == cv2.EVENT_LBUTTONUP:
            roi[2] = x - roi[0]
            roi[3] = y - roi[1]
            roi_seleccionada = True
    
    # Asociar la función al evento del mouse
    cv2.setMouseCallback('Calibracion', seleccionar_roi)
    
    print("Instrucciones:")
    print("1. Arrastre el ratón para seleccionar una región de interés (ROI)")
    print("2. Ajuste los parámetros con las barras deslizantes")
    print("3. Presione 's' para guardar la configuración")
    print("4. Presione 'r' para restablecer la ROI")
    print("5. Presione 'q' para salir")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Fin del video o error en la captura")
            break
            
        # Cambiar tamaño si es necesario
        if width != int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)):
            frame = cv2.resize(frame, (width, height))
            
        # Crear una copia para dibujar
        frame_dibujo = frame.copy()
        
        # Dibujar la ROI seleccionada
        if roi_seleccionada:
            cv2.rectangle(frame_dibujo, (roi[0], roi[1]), (roi[0] + roi[2], roi[1] + roi[3]), (0, 255, 0), 2)
            roi_recorte = frame[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
            
            # Obtener valores de los controles
            history = cv2.getTrackbarPos('History', 'Calibracion')
            threshold = cv2.getTrackbarPos('Threshold', 'Calibracion')
            area_min = cv2.getTrackbarPos('Area Min', 'Calibracion')
            umbral = cv2.getTrackbarPos('Umbral', 'Calibracion')
            
            # Crear el sustractor de fondo
            sustractor_fondo = cv2.createBackgroundSubtractorMOG2(history=history, varThreshold=threshold, detectShadows=True)
            
            # Aplicar sustractor de fondo a la ROI
            mascara = sustractor_fondo.apply(roi_recorte)
            
            # Aplicar umbral para eliminar sombras (valores grises)
            _, mascara_umbral = cv2.threshold(mascara, umbral, 255, cv2.THRESH_BINARY)
            
            # Encontrar contornos
            contornos, _ = cv2.findContours(mascara_umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Dibujar contornos que superan el área mínima
            for contorno in contornos:
                area = cv2.contourArea(contorno)
                if area > area_min:
                    x, y, w, h = cv2.boundingRect(contorno)
                    cv2.rectangle(roi_recorte, (x, y), (x+w, y+h), (0, 0, 255), 2)
            
            # Mostrar la máscara
            mascara_color = cv2.cvtColor(mascara_umbral, cv2.COLOR_GRAY2BGR)
            
            # Mostrar máscaras y ROI en la ventana de calibración
            altura_combinada = frame_dibujo.shape[0]
            ancho_combinado = frame_dibujo.shape[1] + mascara_color.shape[1]
            imagen_combinada = np.zeros((altura_combinada, ancho_combinado, 3), dtype=np.uint8)
            
            # Colocar las imágenes en la imagen combinada
            imagen_combinada[0:frame_dibujo.shape[0], 0:frame_dibujo.shape[1]] = frame_dibujo
            imagen_combinada[0:mascara_color.shape[0], frame_dibujo.shape[1]:] = mascara_color
            
            # Mostrar la imagen combinada
            cv2.imshow('Calibracion', imagen_combinada)
            
            # Mostrar información en la consola
            print(f"\rHistoria: {history}, Umbral: {threshold}, Área mín: {area_min}, Umbral máscara: {umbral}, ROI: {roi}", end="")
            
        else:
            cv2.imshow('Calibracion', frame_dibujo)
        
        # Procesar teclas
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            roi = [0, 0, width, height]
            roi_seleccionada = False
        elif key == ord('s'):
            # Guardar la configuración en un archivo
            configuracion = {
                'roi': roi,
                'history': cv2.getTrackbarPos('History', 'Calibracion'),
                'threshold': cv2.getTrackbarPos('Threshold', 'Calibracion'),
                'area_min': cv2.getTrackbarPos('Area Min', 'Calibracion'),
                'umbral': cv2.getTrackbarPos('Umbral', 'Calibracion')
            }
            
            # Guardar en un archivo de texto
            with open('configuracion.txt', 'w') as f:
                f.write(f"ROI={roi[0]},{roi[1]},{roi[2]},{roi[3]}\n")
                f.write(f"HISTORY={configuracion['history']}\n")
                f.write(f"THRESHOLD={configuracion['threshold']}\n")
                f.write(f"AREA_MIN={configuracion['area_min']}\n")
                f.write(f"UMBRAL={configuracion['umbral']}\n")
                
            print(f"\nConfiguración guardada en 'configuracion.txt'")
            print(f"Para usar esta configuración, ejecute:")
            print(f"python main.py --input {args.input} --roi {roi[0]},{roi[1]},{roi[2]},{roi[3]}")
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
