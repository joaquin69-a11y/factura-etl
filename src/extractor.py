import os
import re
import pdfplumber


def extraer_datos_pdf(ruta_pdf: str) -> dict:
    """Extrae los campos clave de un comprobante PDF mediante expresiones regulares."""
    texto_completo = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            texto_completo += (pagina.extract_text() or "") + "\n"

    patrones = {
        "ruc": r"RUC Emisor:\s*(\d{11})",
        "razon_social": r"Razon Social:\s*(.+)",
        "serie_numero": r"Serie-Numero:\s*([A-Z0-9]+-\d+)",
        "fecha_emision": r"Fecha Emision:\s*(\d{4}-\d{2}-\d{2})",
        "moneda": r"Moneda:\s*(PEN|USD)",
        "subtotal": r"Subtotal:\s*([\d.]+)",
        "igv": r"IGV \(18%\):\s*([\d.]+)",
        "total": r"Total:\s*([\d.]+)",
    }

    datos = {"archivo": os.path.basename(ruta_pdf)}

    for campo, patron in patrones.items():
        coincidencia = re.search(patron, texto_completo)
        valor = coincidencia.group(1).strip() if coincidencia else None
        if campo in ("subtotal", "igv", "total") and valor is not None:
            valor = float(valor)
        datos[campo] = valor

    return datos


def procesar_carpeta(carpeta_entrada: str = "data/entrada") -> list[dict]:
    """Recorre todos los PDFs de la carpeta indicada y devuelve una lista de registros."""
    registros = []
    if not os.path.exists(carpeta_entrada):
        return registros

    for nombre_archivo in sorted(os.listdir(carpeta_entrada)):
        if nombre_archivo.lower().endswith(".pdf"):
            ruta = os.path.join(carpeta_entrada, nombre_archivo)
            registros.append(extraer_datos_pdf(ruta))

    return registros


if __name__ == "__main__":
    for registro in procesar_carpeta():
        print(registro)