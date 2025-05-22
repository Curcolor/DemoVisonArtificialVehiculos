#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilidades para el sistema de detección y seguimiento de vehículos.
"""

import os
import cv2
import numpy as np


def cargar_configuracion():
    """
    Carga la configuración desde un archivo o utiliza valores predeterminados.
    Returns:
        dict: Configuración del sistema
    """
    config = {
        'history': 200,
        'threshold': 30,
        'area_min': 800,
        'umbral': 254,
        'roi': None
    }
    
    # Si existe un archivo de configuración, cargarlo
    if os.path.exists('config.json'):
        import json
        try:
            with open('config.json', 'r') as f:
                stored_config = json.load(f)
                config.update(stored_config)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")
    
    return config


def guardar_configuracion(config):
    """
    Guarda la configuración en un archivo JSON
    Args:
        config (dict): Configuración a guardar
    """
    import json
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
        print("Configuración guardada correctamente")
    except Exception as e:
        print(f"Error al guardar configuración: {e}")


def aplicar_roi(frame, roi):
    """
    Aplica una región de interés (ROI) a un frame
    Args:
        frame: Frame a procesar
        roi: [x, y, w, h] coordenadas de la ROI

    Returns:
        Región de interés del frame
    """
    if roi is None:
        return frame
    
    x, y, w, h = roi
    if x < 0 or y < 0 or w <= 0 or h <= 0:
        return frame
    
    return frame[y:y+h, x:x+w]


def dibujar_contornos(frame, contornos, color=(0, 255, 0), grosor=2):
    """
    Dibuja contornos en un frame
    Args:
        frame: Frame donde dibujar
        contornos: Lista de contornos
        color: Color para dibujar (por defecto verde)
        grosor: Grosor de la línea

    Returns:
        Frame con los contornos dibujados
    """
    return cv2.drawContours(frame.copy(), contornos, -1, color, grosor)


def dibujar_informacion(frame, objetos, contadores, fps=0):
    """
    Dibuja información sobre los objetos detectados
    Args:
        frame: Frame donde dibujar
        objetos: Diccionario de objetos {id: (x, y)}
        contadores: Contadores por tipo de objeto
        fps: Frames por segundo actuales

    Returns:
        Frame con información dibujada
    """
    altura, _, _ = frame.shape
    
    # Dibujar contadores
    cv2.putText(frame, f"Vehículos: {contadores['vehiculo']}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Motos: {contadores['moto']}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
    cv2.putText(frame, f"Peatones: {contadores['peaton']}", (10, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(frame, f"Emergencia: {contadores['emergencia']}", (10, 120), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    # Dibujar FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, altura - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    return frame
