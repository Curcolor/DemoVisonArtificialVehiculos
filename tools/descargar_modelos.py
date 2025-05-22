import os
import requests
import sys
import time

def descargar_archivo(url, destino):
    """
    Descarga un archivo mostrando una barra de progreso
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        tamaño_total = int(response.headers.get('content-length', 0))
        bytes_descargados = 0
        
        # Asegúrese de que el directorio de destino exista
        os.makedirs(os.path.dirname(os.path.abspath(destino)), exist_ok=True)
        
        print(f"Descargando {destino}...")
        
        with open(destino, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    bytes_descargados += len(chunk)
                    
                    # Mostrar progreso
                    porcentaje = (bytes_descargados / tamaño_total) * 100
                    barra = '█' * int(porcentaje / 2) + '-' * (50 - int(porcentaje / 2))
                    sys.stdout.write(f"\r|{barra}| {porcentaje:.1f}% ({bytes_descargados/1048576:.1f}/{tamaño_total/1048576:.1f} MB)")
                    sys.stdout.flush()
        
        print(f"\nDescarga completada: {destino}")
        return True
    except Exception as e:
        print(f"\nError al descargar {destino}: {e}")
        return False

def main():
    print("Descargando archivos necesarios para YOLO...")
    
    # Directorio para guardar los modelos
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
    os.makedirs(models_dir, exist_ok=True)
    
    # URLs de los archivos a descargar
    # Para modelos más pequeños y rápidos, podríamos usar YOLOv4-tiny
    urls = {
        "yolov4.cfg": "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg",
        "yolov4.weights": "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights",
        "coco.names": "https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names",
        "yolov4-tiny.cfg": "https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg",
        "yolov4-tiny.weights": "https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights"
    }
    
    for nombre_archivo, url in urls.items():
        ruta_destino = os.path.join(models_dir, nombre_archivo)
        if not os.path.exists(ruta_destino):
            exito = descargar_archivo(url, ruta_destino)
            if not exito:
                print(f"No se pudo descargar {nombre_archivo}. Verifique su conexión a Internet e inténtelo de nuevo.")
            time.sleep(1)  # Pequeña pausa entre descargas
        else:
            print(f"El archivo {nombre_archivo} ya existe en {ruta_destino}. Omitiendo descarga.")

    print("\nTodos los archivos necesarios están disponibles.")
    print("\nEl sistema está listo para ejecutar. Puede ejecutar:")
    print("python main.py --input 0  # Para usar la cámara")
    print("python main.py --input ruta_del_video.mp4  # Para usar un archivo de video")
    print("python main.py --input ruta_del_video.mp4 --roi 100,100,500,300  # Para definir una región de interés")
    print("\nO simplemente ejecute el script de inicio:")
    print("scripts/iniciar.bat  # En Windows")

if __name__ == "__main__":
    main()
