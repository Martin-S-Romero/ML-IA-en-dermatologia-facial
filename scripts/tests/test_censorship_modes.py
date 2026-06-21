import os
import sys
import warnings
import logging
import contextlib

# Suprimir warnings de TensorFlow Lite y Protobuf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # TensorFlow
os.environ['ABSL_LOG_MIN_LEVEL'] = '3'     # absl (TensorFlow Lite)
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('tensorflow_lite').setLevel(logging.ERROR)

# Suprimir warning de Protobuf
warnings.filterwarnings('ignore', message='SymbolDatabase.GetPrototype.*')

# Ajustar el path para que pueda importar módulos de la aplicación
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))

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

        # Redirigir stderr para suprimir warnings de TensorFlow
        with contextlib.redirect_stderr(open(os.devnull, 'w')):
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
