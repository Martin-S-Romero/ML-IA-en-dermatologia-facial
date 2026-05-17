import os
import sys

# Ajustar el path para que pueda importar módulos de la aplicación
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.face_censor import FaceCensor

IMAGE_PATH = r"c:\Users\Sheen\Downloads\Tesis 2.0\image\test_imagen798x1200.jpg"

def test_censorship_modes():
    print("--- INICIANDO PRUEBAS DE MODOS DE CENSURA (Unit Test Interno) ---")
    
    if not os.path.exists(IMAGE_PATH):
        print(f"[ERROR] No se encuentra la imagen: {IMAGE_PATH}")
        return
        
    modes = ["blur", "pixelate", "black"]
    
    for mode in modes:
        print(f"\n[*] Probando modo: {mode.upper()}")
        output_path = f"test_output_{mode}.jpg"
        
        # Instanciar el censor para el modo específico
        censor = FaceCensor(mode=mode, blur_strength=55, pixel_size=10, expand=15)
        
        try:
            result = censor.process_image(IMAGE_PATH, output_path)
            if result is not None:
                print(f"    [EXITO] Censura '{mode}' aplicada correctamente. Guardada en: {output_path}")
                # Limpiar la imagen generada para no ensuciar el directorio
                os.remove(output_path)
            else:
                print(f"    [ERROR] Falló la censura '{mode}'. ¿Rostro no detectado?")
        except Exception as e:
            print(f"    [ERROR] Excepción durante '{mode}': {e}")
            
    print("\n--- PRUEBAS FINALIZADAS ---")

if __name__ == "__main__":
    test_censorship_modes()
