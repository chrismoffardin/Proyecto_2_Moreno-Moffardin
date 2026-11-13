"""
fotoapp.py - Módulo de procesamiento de imágenes para redes sociales
Proyecto 2 - Parte 1: Procesamiento de Imágenes
Programación Python Avanzada 2026

Funciones:
- cargar_imagen(): Carga imagen desde ruta local o URL
- cargar_imagen_sistema(): Carga y guarda en variables globales (Función 1)
- redimensionar_para_red(): Redimensiona para redes sociales (contain/fit)
- ajustar_contraste(): Ecualización de histograma
- aplicar_filtro(): Aplica uno de los 9 filtros de Pillow
- detectar_bordes(): Detecta bordes con 2 técnicas (Pillow + Canny)
- menu_principal(): Menú interactivo de la aplicación
"""

from PIL import Image, ImageOps, ImageFilter
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import os
import cv2
import numpy as np
import sys

# ============================================================
# CONFIGURACIÓN DE CARPETAS
# ============================================================
MAX_DIMENSION = 1500  # Límite de resolución para procesamiento rápido
CARPETA_ORIGINAL = "fotos_originales"
CARPETA_MEJORADA = "fotos_mejoradas"
CARPETA_RESULTADOS = "resultados"

for carpeta in [CARPETA_ORIGINAL, CARPETA_MEJORADA, CARPETA_RESULTADOS]:
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

# ============================================================
# DIMENSIONES RECOMENDADAS PARA REDES SOCIALES (2026)
# ============================================================
DIMENSIONES_REDES = {
    "youtube": (1280, 720),  # Thumbnail estándar
    "instagram": (1080, 1080),  # Post cuadrado
    "twitter": (1200, 675),  # Post con link
    "facebook": (1200, 630)  # Post compartido
}

# ============================================================
# DICCIONARIO DE LOS 9 FILTROS DE PILLOW
# ============================================================
FILTROS_PILLOW = {
    "blur": ImageFilter.BLUR,
    "contour": ImageFilter.CONTOUR,
    "detail": ImageFilter.DETAIL,
    "edge_enhance": ImageFilter.EDGE_ENHANCE,
    "edge_enhance_more": ImageFilter.EDGE_ENHANCE_MORE,
    "emboss": ImageFilter.EMBOSS,
    "find_edges": ImageFilter.FIND_EDGES,
    "sharpen": ImageFilter.SHARPEN,
    "smooth": ImageFilter.SMOOTH
}

# ============================================================
# VARIABLES GLOBALES DE ESTADO
# ============================================================
_imagen_actual = None
_ruta_actual = None

# ============================================================
# FUNCIONES AUXILIARES DE CARGA
# ============================================================
def cargar_imagen(ruta_o_url):
    """
    Carga una imagen desde ruta local o URL.

    Parámetros:
    -----------
    ruta_o_url : str
        Ruta local del archivo o URL de la imagen

    Retorna:
    --------
    PIL.Image.Image
        Imagen en modo RGB

    Excepciones:
    ------------
    ValueError
        Si la ruta/URL es inválida o la imagen no se puede cargar
    """
    try:
        if str(ruta_o_url).startswith(('http://', 'https://')):
            respuesta = requests.get(ruta_o_url, timeout=10)
            respuesta.raise_for_status()
            imagen = Image.open(BytesIO(respuesta.content))
        else:
            if not os.path.exists(ruta_o_url):
                raise FileNotFoundError(f"La ruta '{ruta_o_url}' no existe")
            imagen = Image.open(ruta_o_url)

        if imagen.mode != 'RGB':
            imagen = imagen.convert('RGB')

        ancho, alto = imagen.size  # Redimensionar si excede MAX_DIMENSION (optimización)
        if max(ancho, alto) > MAX_DIMENSION:
            escala = MAX_DIMENSION / max(ancho, alto)
            nueva_dimension = (int(ancho * escala), int(alto * escala))
            imagen = imagen.resize(nueva_dimension, Image.Resampling.LANCZOS)
        return imagen
    except Exception as e:
        raise ValueError(f"Error al cargar la imagen: {str(e)}")


def cargar_imagen_sistema(ruta_o_url):
    """
    Carga la imagen y la guarda en las variables globales del sistema.
    Es la "Función 1" obligatoria antes de cualquier otra operación.
    """
    global _imagen_actual, _ruta_actual
    _imagen_actual = cargar_imagen(ruta_o_url)
    _ruta_actual = ruta_o_url
    print(f"\n✅ Imagen cargada: {_imagen_actual.size[0]}x{_imagen_actual.size[1]}")


def mostrar_y_guardar(fig, nombre_archivo):
    """
    Muestra la figura con plt.show() (estándar de clase) y la guarda.
    Espera que el usuario presione ENTER para volver al menú.
    """
    plt.show()

    ruta_guardado = os.path.join(CARPETA_RESULTADOS, nombre_archivo)
    fig.savefig(ruta_guardado, dpi=72, bbox_inches='tight')
    print(f"💾 Guardada en: {ruta_guardado}")

    input("\n⏎  [ Presione ENTER para volver al menú ]  ⏎\n")

    plt.close(fig)

# ============================================================
# FUNCIÓN 1: REDIMENSIONAR PARA REDES SOCIALES
# ============================================================
def redimensionar_para_red(red_social, modo="contain"):
    """
    Redimensiona la imagen al tamaño recomendado para una red social.

    Parámetros:
    -----------
    red_social : str
        'youtube', 'instagram', 'twitter' o 'facebook'
    modo : str
        'contain' (mantiene toda la imagen con bordes negros) o
        'fit' (recorta para llenar el tamaño exacto)
    """
    global _imagen_actual, _ruta_actual

    if _imagen_actual is None:
        raise ValueError("No hay imagen cargada.")

    red_social = red_social.lower().strip()
    if red_social not in DIMENSIONES_REDES:
        raise ValueError(f"Red no válida. Opciones: {list(DIMENSIONES_REDES.keys())}")

    ancho_obj, alto_obj = DIMENSIONES_REDES[red_social]
    ancho_orig, alto_orig = _imagen_actual.size

    if modo == "fit":
        # Recorta la imagen para llenar el tamaño exacto (como hacen las redes)
        imagen_resultado = ImageOps.fit(
            _imagen_actual, (ancho_obj, alto_obj),
            method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)
        )
        info = "RECORTADA (fit)"
    else:
        # Mantiene toda la imagen visible, agrega bordes negros
        imagen_reducida = ImageOps.contain(
            _imagen_actual, (ancho_obj, alto_obj),
            method=Image.Resampling.LANCZOS
        )
        lienzo = Image.new("RGB", (ancho_obj, alto_obj), (0, 0, 0))
        pos_x = (ancho_obj - imagen_reducida.size[0]) // 2
        pos_y = (alto_obj - imagen_reducida.size[1]) // 2
        lienzo.paste(imagen_reducida, (pos_x, pos_y))
        imagen_resultado = lienzo
        info = "COMPLETA (bordes negros)"

    # Crear figura comparativa
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].imshow(_imagen_actual)
    axes[0].set_title(f'Original\n{ancho_orig}x{alto_orig}', fontweight='bold')
    axes[0].axis('off')
    axes[1].imshow(imagen_resultado)
    axes[1].set_title(f'{red_social.upper()} ({info})\n{ancho_obj}x{alto_obj}', fontweight='bold')
    axes[1].axis('off')
    plt.tight_layout()

    nombre_base = os.path.splitext(os.path.basename(_ruta_actual))[0]
    mostrar_y_guardar(fig, f"redim_{red_social}_{modo}_{nombre_base}.png")

    _imagen_actual = imagen_resultado


# ============================================================
# FUNCIÓN 2: AJUSTAR CONTRASTE POR HISTOGRAMA
# ============================================================
def ajustar_contraste():
    """
    Ajusta el contraste mediante ecualización de histograma.
    Muestra original vs. ecualizada y sus histogramas.
    """
    if _imagen_actual is None:
        raise ValueError("No hay imagen cargada.")

    imagen_ecualizada = ImageOps.equalize(_imagen_actual)
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    axes[0, 0].imshow(_imagen_actual)
    axes[0, 0].set_title('Original', fontweight='bold')
    axes[0, 0].axis('off')
    axes[0, 1].imshow(imagen_ecualizada)
    axes[0, 1].set_title('Ecualizada', fontweight='bold')
    axes[0, 1].axis('off')

    # Convertir PIL a numpy array para usar .ravel()
    arr_orig = np.array(_imagen_actual.convert('L'))
    arr_ecua = np.array(imagen_ecualizada.convert('L'))

    axes[1, 0].hist(arr_orig.ravel(), bins=256, range=[0, 256], color='gray', alpha=0.7)
    axes[1, 0].set_title('Histograma Original')
    axes[1, 0].set_xlim([0, 256])
    axes[1, 1].hist(arr_ecua.ravel(), bins=256, range=[0, 256], color='gray', alpha=0.7)
    axes[1, 1].set_title('Histograma Ecualizado')
    axes[1, 1].set_xlim([0, 256])

    plt.tight_layout()

    nombre_base = os.path.splitext(os.path.basename(_ruta_actual))[0]
    mostrar_y_guardar(fig, f"contraste_{nombre_base}.png")


# ============================================================
# FUNCIÓN 3: APLICAR FILTROS DE PILLOW
# ============================================================
def aplicar_filtro(nombre_filtro):
    """
    Aplica uno de los 9 filtros de Pillow a la imagen.

    Parámetros:
    -----------
    nombre_filtro : str
        Nombre del filtro (blur, contour, detail, etc.)
    """
    if _imagen_actual is None:
        raise ValueError("No hay imagen cargada.")

    nombre_filtro = nombre_filtro.lower().strip()
    if nombre_filtro not in FILTROS_PILLOW:
        raise ValueError(f"Filtro no válido. Opciones: {list(FILTROS_PILLOW.keys())}")

    imagen_filtrada = _imagen_actual.filter(FILTROS_PILLOW[nombre_filtro])

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].imshow(_imagen_actual)
    axes[0].set_title('Original', fontweight='bold')
    axes[0].axis('off')
    axes[1].imshow(imagen_filtrada)
    axes[1].set_title(f'Filtro: {nombre_filtro.upper()}', fontweight='bold')
    axes[1].axis('off')
    plt.tight_layout()

    nombre_base = os.path.splitext(os.path.basename(_ruta_actual))[0]
    mostrar_y_guardar(fig, f"filtro_{nombre_filtro}_{nombre_base}.png")


# ============================================================
# FUNCIÓN 4: DETECTAR BORDES (2 TÉCNICAS)
# ============================================================
def detectar_bordes():
    """
    Detecta bordes usando 2 técnicas:
    1. Pillow FIND_EDGES
    2. OpenCV Canny
    """
    if _imagen_actual is None:
        raise ValueError("No hay imagen cargada.")

    # Técnica 1: Pillow
    bordes_pillow = _imagen_actual.filter(ImageFilter.FIND_EDGES)

    # Técnica 2: OpenCV Canny
    img_np = np.array(_imagen_actual)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    img_gris = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    bordes_canny_np = cv2.Canny(img_gris, 100, 200)
    bordes_canny = Image.fromarray(bordes_canny_np)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(_imagen_actual)
    axes[0].set_title('Original', fontweight='bold')
    axes[0].axis('off')
    axes[1].imshow(bordes_pillow)
    axes[1].set_title('Pillow FIND_EDGES', fontweight='bold')
    axes[1].axis('off')
    axes[2].imshow(bordes_canny, cmap='gray')
    axes[2].set_title('OpenCV Canny', fontweight='bold')
    axes[2].axis('off')
    plt.tight_layout()

    nombre_base = os.path.splitext(os.path.basename(_ruta_actual))[0]
    mostrar_y_guardar(fig, f"bordes_{nombre_base}.png")


# ============================================================
# MENÚ SECUNDARIO (OPERACIONES)
# ============================================================
def menu_secundario():
    """
    Menú de operaciones sobre la imagen cargada.
    Valida que haya imagen antes de cada operación.
    """
    global _imagen_actual, _ruta_actual

    while True:
        print("\n" + "-" * 30)
        print(" MENÚ DE OPERACIONES")
        print("-" * 30)
        print("1. Redimensionar red social")
        print("2. Ajustar contraste")
        print("3. Aplicar filtro")
        print("4. Detectar bordes")
        print("5. Volver al inicio")
        print("0. Salir")
        print("-" * 30)

        opcion = input("Opción: ").strip()

        try:
            if opcion == "1":
                if _imagen_actual is None:
                    print("⚠️ Cargue una imagen primero.")
                    continue
                print("\nRedes:")
                lista_redes = list(DIMENSIONES_REDES.keys())
                for i, red in enumerate(lista_redes, 1):
                    print(f" {i}. {red}")

                sel = input("Red (1-4): ").strip()
                if sel in ["1", "2", "3", "4"]:
                    red = lista_redes[int(sel) - 1]
                    print("\nModo:")
                    print(" 1. contain (bordes negros)")
                    print(" 2. fit (recortar)")
                    sel_modo = input("Modo (1-2): ").strip()
                    # Validación estricta del modo
                    if sel_modo == "1":
                        modo = "contain"
                    elif sel_modo == "2":
                        modo = "fit"
                    else:
                        print("❌ Modo inválido. Debe ser 1 o 2.")
                        continue
                    redimensionar_para_red(red, modo)
                else:
                    print("❌ Número de red inválido.")

            elif opcion == "2":
                if _imagen_actual is None:
                    print("⚠️ Cargue una imagen primero.")
                    continue
                ajustar_contraste()

            elif opcion == "3":
                if _imagen_actual is None:
                    print("⚠️ Cargue una imagen primero.")
                    continue
                print("\nFiltros:")
                lista_filtros = list(FILTROS_PILLOW.keys())
                for i, f in enumerate(lista_filtros, 1):
                    print(f" {i}. {f}")
                sel = input("Filtro (1-9): ").strip()
                if sel.isdigit() and 1 <= int(sel) <= 9:
                    aplicar_filtro(lista_filtros[int(sel) - 1])
                else:
                    print("❌ Número de filtro inválido.")

            elif opcion == "4":
                if _imagen_actual is None:
                    print("⚠️ Cargue una imagen primero.")
                    continue
                detectar_bordes()

            elif opcion == "5":
                break

            elif opcion == "0":
                print("👋 ¡Hasta luego!")
                sys.exit()

            else:
                print("❌ Opción no válida.")

        except Exception as e:
            print(f"❌ Error: {str(e)}")


# ============================================================
# MENÚ PRINCIPAL
# ============================================================
def menu_principal():
    """
    Menú principal de la aplicación.
    Opción 1 (cargar) es obligatoria antes de cualquier operación.
    """
    global _imagen_actual, _ruta_actual

    while True:
        print("\n" + "-" * 30)
        print(" 📸 FOTOAPP")
        print("-" * 30)
        if _imagen_actual is not None:
            print(f"✓ {os.path.basename(_ruta_actual)}")
        else:
            print("✗ Sin imagen")

        print("\n1. Cargar imagen")
        print("2. Operaciones")
        print("0. Salir")
        print("-" * 30)

        opcion = input("Opción: ").strip()

        if opcion == "1":
            ruta = input("Ruta/URL: ").strip()
            if ruta:
                try:
                    cargar_imagen_sistema(ruta)
                except Exception as e:
                    print(f"❌ Error: {str(e)}")
            else:
                print("❌ Ingrese una ruta.")

        elif opcion == "2":
            if _imagen_actual is None:
                print("⚠️ Cargue una imagen primero (opción 1).")
            else:
                menu_secundario()

        elif opcion == "0":
            print("👋 ¡Hasta luego!")
            break

        else:
            print("❌ Opción no válida.")


# ============================================================
# INICIO
# ============================================================
if __name__ == "__main__":
    menu_principal()