import cv2
import numpy as np
import argparse
import os
import time
import sys

# Añadir la ruta de src al path para importar los módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.detector import Detector
from src.rastreador import Rastreador
from src.utils import cargar_configuracion, aplicar_roi, dibujar_informacion

# Comprobar si existen los archivos de YOLO
models_dir = os.path.join(os.path.dirname(__file__), 'models')
yolo_tiny_exists = (
    os.path.exists(os.path.join(models_dir, 'yolov4-tiny.weights')) and 
    os.path.exists(os.path.join(models_dir, 'yolov4-tiny.cfg')) and 
    os.path.exists(os.path.join(models_dir, 'coco.names'))
)
    
yolo_full_exists = (
    os.path.exists(os.path.join(models_dir, 'yolov4.weights')) and 
    os.path.exists(os.path.join(models_dir, 'yolov4.cfg')) and 
    os.path.exists(os.path.join(models_dir, 'coco.names'))
)

def main():
    # Parsear argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Sistema de detección y seguimiento de vehículos')
    parser.add_argument('--input', type=str, default='0', help='Ruta al video de entrada o ID de la cámara (por defecto: 0)')
    parser.add_argument('--output', type=str, default='', help='Ruta para guardar el video de salida (opcional)')
    parser.add_argument('--roi', type=str, default='', help='Región de interés en formato x,y,w,h (opcional)')
    parser.add_argument('--show', type=bool, default=True, help='Mostrar video en tiempo real')
    parser.add_argument('--modelo', type=str, choices=['tiny', 'full', 'auto'], default='auto', 
                        help='Modelo a utilizar: tiny (más rápido), full (más preciso) o auto (detectar automáticamente)')
    args = parser.parse_args()
    
    # Inicializar detector según la elección del usuario y la disponibilidad de los modelos
    detector = None
    sustractor_fondo = None
    
    if args.modelo == 'tiny' and yolo_tiny_exists:
        print("Usando YOLOv4-tiny para detección (equilibrio entre velocidad y precisión)")
        detector = Detector(yolo_weights='models/yolov4-tiny.weights', yolo_cfg='models/yolov4-tiny.cfg', coco_names='models/coco.names')
    elif args.modelo == 'full' and yolo_full_exists:
        print("Usando YOLOv4 para detección (más preciso pero más lento)")
        detector = Detector(yolo_weights='models/yolov4.weights', yolo_cfg='models/yolov4.cfg', coco_names='models/coco.names')
    elif args.modelo == 'auto':
        # Modo automático - elegir el mejor modelo disponible
        if yolo_tiny_exists:
            print("Modo automático: Usando YOLOv4-tiny para detección (equilibrio entre velocidad y precisión)")
            detector = Detector(yolo_weights='models/yolov4-tiny.weights', yolo_cfg='models/yolov4-tiny.cfg', coco_names='models/coco.names')
        elif yolo_full_exists:
            print("Modo automático: Usando YOLOv4 para detección (más preciso pero más lento)")
            detector = Detector(yolo_weights='models/yolov4.weights', yolo_cfg='models/yolov4.cfg', coco_names='models/coco.names')
        else:
            print("No se encontraron archivos de YOLO. Usando detección por sustracción de fondo.")
            sustractor_fondo = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=30, detectShadows=True)
    else:
        # Si el modelo elegido no está disponible
        print(f"El modelo {args.modelo} no está disponible. Usando detección por sustracción de fondo.")
        sustractor_fondo = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=30, detectShadows=True)

    # Cargar el video
    if args.input.isdigit():
        cap = cv2.VideoCapture(int(args.input))
    else:
        cap = cv2.VideoCapture(args.input)
    
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
    fps = int(cap.get(cv2.CAP_PROP_FPS))
      # Configurar el escritor de video si se especificó output
    out = None
    if args.output:
        # Usar MP4V codec que es más compatible con formato mp4
        try:
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            # Crear el escritor de video
            out = cv2.VideoWriter(args.output, fourcc, fps, (width, height))
        except Exception as e:
            print(f"Error al crear el escritor de video: {e}")
            print("Usando XVID como alternativa")
            # Usar XVID codec como alternativa
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(args.output, fourcc, fps, (width, height))
      # El detector y sustractor de fondo ya se inicializaron según los argumentos del usuario
    
    rastreador = Rastreador()
    
    # Definir región de interés si se proporciona
    roi = None
    if args.roi:
        try:
            x, y, w, h = map(int, args.roi.split(','))
            roi = (x, y, w, h)
        except:
            print("Error en el formato de ROI. Debe ser x,y,w,h")
    
    # Variables para el rendimiento
    frame_count = 0
    total_fps = 0
    start_time = time.time()
    
    # Colores para cada tipo de objeto
    colores = {
        'vehiculo': (0, 255, 0),     # Verde
        'moto': (0, 165, 255),       # Naranja
        'peaton': (0, 0, 255),       # Rojo
        'emergencia': (255, 0, 0)    # Azul
    }
    
    # Procesar el video
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Fin del video o error en la captura")
            break
            
    # Cambiar tamaño para mejorar rendimiento (ventana más pequeña)
        if width > 640:
            frame = cv2.resize(frame, (640, 360))
            width, height = 640, 360
            
        # Crear una copia para dibujar
        frame_dibujo = frame.copy()
        
        # Aplicar ROI si está definida
        if roi:
            x, y, w, h = roi
            cv2.rectangle(frame_dibujo, (x, y), (x+w, y+h), (255, 0, 0), 2)
            zona_interes = frame[y:y+h, x:x+w]
        else:
            zona_interes = frame
        
        # Detectar objetos
        if detector:
            # Usando YOLO
            boxes, tipos, tiempo_deteccion = detector.detect(frame, roi)
        else:
            # Usando sustracción de fondo
            mascara = sustractor_fondo.apply(zona_interes)
            
            # Aplicar umbral para eliminar sombras (valores grises)
            _, mascara = cv2.threshold(mascara, 254, 255, cv2.THRESH_BINARY)
            
            # Encontrar contornos
            contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrar contornos por área
            boxes = []
            tipos = []
            for contorno in contornos:
                area = cv2.contourArea(contorno)
                if area > 800:  # Filtrar por área mínima
                    x, y, w, h = cv2.boundingRect(contorno)
                    # Ajustar coordenadas si se está usando ROI
                    if roi:
                        x += roi[0]
                        y += roi[1]
                    boxes.append((x, y, w, h))
                    # Por defecto asumimos que es un vehículo
                    tipos.append('vehiculo')
        
        # Actualizar el rastreador
        objetos_con_ids = rastreador.actualizar(boxes, tipos)
        
        # Dibujar los objetos rastreados
        for obj_id, x, y, w, h, tipo in objetos_con_ids:
            # Dibujar rectángulo
            color = colores.get(tipo, (0, 255, 0))  # Verde por defecto
            cv2.rectangle(frame_dibujo, (x, y), (x+w, y+h), color, 2)
            
            # Dibujar ID y tipo
            texto = f"ID: {obj_id} - {tipo.capitalize()}"
            cv2.putText(frame_dibujo, texto, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Dibujar contadores en la esquina superior izquierda
        contadores = rastreador.get_contadores()
        y_pos = 30
        for tipo, contador in contadores.items():
            texto = f"{tipo.capitalize()}: {contador}"
            color = colores.get(tipo, (0, 255, 0))
            cv2.putText(frame_dibujo, texto, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_pos += 30
        
        # Calcular FPS
        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time
        total_fps += fps
        
        # Mostrar FPS
        cv2.putText(frame_dibujo, f"FPS: {fps:.2f}", (width - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Guardar frame si se especificó output
        if out:
            out.write(frame_dibujo)
            
        # Mostrar frame
        if args.show:
            # Mostrar también la máscara si estamos usando sustracción de fondo
            if not detector and roi:
                cv2.imshow("Mascara", mascara)
                
            cv2.imshow("Deteccion de Vehiculos", frame_dibujo)
              # Salir con 'q' o ESC
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 27 es el código ASCII de ESC
                break
                
            # Mostrar FPS en la consola para monitoreo de rendimiento
            if frame_count % 10 == 0:
                print(f"\rFPS: {fps:.2f}", end="")
    
    # Liberar recursos
    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()
    
    # Mostrar estadísticas finales
    print(f"Procesamiento finalizado")
    print(f"Tiempo total: {elapsed_time:.2f} segundos")
    print(f"Frames procesados: {frame_count}")
    print(f"FPS promedio: {total_fps/frame_count:.2f}")
    print(f"Conteo de objetos:")
    for tipo, contador in rastreador.get_contadores().items():
        print(f"  {tipo.capitalize()}: {contador}")

if __name__ == "__main__":
    main()
