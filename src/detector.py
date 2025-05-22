import cv2
import numpy as np
import time

class Detector:

    """
    Clase para detectar objetos en imágenes o frames de video usando YOLOv4
    """ 
    def __init__(self, yolo_weights='models/yolov4-tiny.weights', yolo_cfg='models/yolov4-tiny.cfg', 
                 coco_names='models/coco.names', confidence_threshold=0.4, nms_threshold=0.4):
        """
        Inicializa el detector de objetos    
        Args:
            yolo_weights: Ruta al archivo de pesos de YOLOv4
            yolo_cfg: Ruta al archivo de configuración de YOLOv4
            coco_names: Ruta al archivo con las clases de COCO
            confidence_threshold: Umbral de confianza para detecciones
            nms_threshold: Umbral para supresión de no máximos
        """
        import os
        
        # Determinar la ruta base del proyecto
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Construir rutas absolutas si se proporcionan rutas relativas
        if not os.path.isabs(yolo_weights):
            yolo_weights = os.path.join(base_dir, yolo_weights)
        if not os.path.isabs(yolo_cfg):
            yolo_cfg = os.path.join(base_dir, yolo_cfg)
        if not os.path.isabs(coco_names):
            coco_names = os.path.join(base_dir, coco_names)
            
        # Cargar la red neuronal
        self.net = cv2.dnn.readNetFromDarknet(yolo_cfg, yolo_weights)
        
        # Utilizar CPU (más compatible en todos los sistemas)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        
        # Cargar las clases
        with open(coco_names, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
            
        # Obtener las capas de salida
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers().flatten()]
        
        # Mapeo de clases COCO a nuestras categorías
        self.class_mapping = {
            'car': 'vehiculo',
            'truck': 'vehiculo',
            'bus': 'vehiculo',
            'motorcycle': 'moto',
            'bicycle': 'moto',
            'person': 'peaton',
            'ambulance': 'emergencia',
            'police car': 'emergencia',
            'fire engine': 'emergencia'
        }
        
        # Umbral de confianza para las detecciones
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        
        # Lista de clases que nos interesan detectar (índices en COCO)
        self.target_classes = [2, 3, 5, 7, 0]  # car, motorcycle, bus, truck, person

    # Método para detectar objetos en un frame
    def detect(self, frame, roi=None):
        """
        Detecta objetos en un frame
        
        Args:
            frame: Imagen o frame donde detectar objetos
            roi: Región de interés (x, y, w, h) o None para usar todo el frame
            
        Returns:
            Lista de rectángulos (x, y, w, h) y lista de tipos de objetos
        """
        # Verificar que el frame es válido
        if frame is None or frame.size == 0:
            print("Frame inválido para detección")
            return [], [], 0
            
        if roi is not None:
            x, y, w, h = roi
            
            # Verificar que el ROI está dentro de los límites del frame
            frame_height, frame_width = frame.shape[:2]
            if x < 0 or y < 0 or x + w > frame_width or y + h > frame_height or w <= 0 or h <= 0:
                print(f"ROI inválido ({x},{y},{w},{h}) para un frame de {frame_width}x{frame_height}")
                roi_frame = frame
                x, y = 0, 0
            else:
                try:
                    roi_frame = frame[y:y+h, x:x+w]
                except Exception as e:
                    print(f"Error al extraer ROI: {e}")
                    roi_frame = frame
                    x, y = 0, 0
        else:
            roi_frame = frame
            x, y = 0, 0
        
        # Verificar que el roi_frame es válido
        if roi_frame is None or roi_frame.size == 0:
            print("ROI inválido, usando frame completo")
            roi_frame = frame
            x, y = 0, 0
          # Dimensiones del frame
        height, width, _ = roi_frame.shape
        
        # Preparar el blob y hacer la detección (tamaño reducido para mejor rendimiento)
        try:
            blob = cv2.dnn.blobFromImage(roi_frame, 1/255.0, (288, 288), swapRB=True, crop=False)
            self.net.setInput(blob)
            
            start_time = time.time()
            outputs = self.net.forward(self.output_layers)
            end_time = time.time()
        except Exception as e:
            print(f"Error en el procesamiento de la red neuronal: {e}")
            return [], [], 0
        
        # Procesar las salidas
        boxes = []
        confidences = []
        class_ids = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                # Filtrar por confianza y clases que nos interesan
                if confidence > self.confidence_threshold and class_id in self.target_classes:
                    # Convertir coordenadas de YOLO a coordenadas del frame
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w_det = int(detection[2] * width)
                    h_det = int(detection[3] * height)
                    
                    # Coordenadas de la esquina superior izquierda
                    x_det = int(center_x - w_det / 2)
                    y_det = int(center_y - h_det / 2)
                    
                    boxes.append([x_det, y_det, w_det, h_det])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
                    
        # Aplicar supresión de no máximos
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)
        
        # Preparar resultados
        result_boxes = []
        result_types = []
        
        if len(indices) > 0:
            for i in indices.flatten():
                # Ajustar las coordenadas si estamos usando ROI
                box = boxes[i]
                x_det, y_det, w_det, h_det = box
                
                # Ajustar coordenadas a la ROI
                if roi is not None:
                    x_det += x
                    y_det += y
                
                result_boxes.append((x_det, y_det, w_det, h_det))
                
                # Obtener el tipo de objeto
                class_name = self.classes[class_ids[i]]
                if class_name in self.class_mapping:
                    result_types.append(self.class_mapping[class_name])
                else:
                    # Por defecto, si no está en el mapping, es un vehículo
                    result_types.append('vehiculo')
                    
        return result_boxes, result_types, end_time - start_time
