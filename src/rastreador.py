import math
import cv2
import numpy as np

class Rastreador:
    def __init__(self):
        # Almacena los centros de los objetos detectados, con format: {id: (x, y)}
        self.centro_puntos = {}
        # Contador para asignar IDs únicos a cada objeto
        self.id_contador = 1
        # Diccionario para almacenar el tipo de cada objeto
        self.objeto_tipos = {}
        # Contadores por tipo de objeto
        self.contadores = {'vehiculo': 0, 'moto': 0, 'peaton': 0, 'emergencia': 0}
        # Lista para almacenar los IDs que ya no están en escena
        self.ids_desaparecidos = []
        # Umbral de distancia para considerar que un objeto es el mismo
        self.distancia_umbral = 25
        # Contador para frames sin detección
        self.frames_sin_deteccion = {}
        # Número máximo de frames para mantener un objeto
        self.max_frames_sin_deteccion = 15

    def actualizar(self, objetos_rect, tipos_objetos):
        """
        Actualiza las posiciones de los objetos detectados y asigna IDs
        
        Args:
            objetos_rect: Lista de rectángulos de objetos detectados [(x, y, w, h), ...]
            tipos_objetos: Lista de tipos correspondientes a cada objeto ['vehiculo', 'moto', ...]
        
        Returns:
            Lista de objetos con sus IDs e información [(id, x, y, w, h, tipo), ...]
        """
        # Lista para almacenar objetos con su información
        objetos_bbox_ids = []
        
        # Obtener el centro de los nuevos objetos detectados
        for i, rect in enumerate(objetos_rect):
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            
            # Verificar si el objeto ya fue detectado
            objeto_detectado = False
            
            # Comprobar con los objetos que ya estamos siguiendo
            for obj_id, pt in self.centro_puntos.items():
                # Calcular distancia entre el nuevo punto y los existentes
                dist = math.hypot(cx - pt[0], cy - pt[1])
                
                # Si la distancia es menor al umbral, actualizamos la posición
                if dist < self.distancia_umbral:
                    self.centro_puntos[obj_id] = (cx, cy)
                    # Reiniciar el contador de frames sin detección
                    self.frames_sin_deteccion[obj_id] = 0
                    # Añadir a la lista de objetos con sus IDs
                    objetos_bbox_ids.append((obj_id, x, y, w, h, self.objeto_tipos[obj_id]))
                    objeto_detectado = True
                    break
            
            # Si es un nuevo objeto, asignamos un nuevo ID
            if not objeto_detectado:
                self.centro_puntos[self.id_contador] = (cx, cy)
                self.objeto_tipos[self.id_contador] = tipos_objetos[i]
                self.frames_sin_deteccion[self.id_contador] = 0
                self.contadores[tipos_objetos[i]] += 1
                objetos_bbox_ids.append((self.id_contador, x, y, w, h, tipos_objetos[i]))
                self.id_contador += 1
                
        # Actualizar contador de frames sin detección para objetos no vistos
        ids_para_eliminar = []
        for obj_id in self.centro_puntos.keys():
            # Si el objeto no fue incluido en la lista actual
            if not any(obj_id == bbox_id for bbox_id, *_ in objetos_bbox_ids):
                self.frames_sin_deteccion[obj_id] += 1
                # Si supera el umbral, lo marcamos para eliminar
                if self.frames_sin_deteccion[obj_id] >= self.max_frames_sin_deteccion:
                    ids_para_eliminar.append(obj_id)
        
        # Eliminar objetos que llevan demasiado tiempo sin ser detectados
        for obj_id in ids_para_eliminar:
            self.centro_puntos.pop(obj_id, None)
            self.objeto_tipos.pop(obj_id, None)
            self.frames_sin_deteccion.pop(obj_id, None)
            self.ids_desaparecidos.append(obj_id)
                
        return objetos_bbox_ids
    
    def get_contadores(self):
        """
        Retorna los contadores actuales de cada tipo de objeto
        """
        return self.contadores
