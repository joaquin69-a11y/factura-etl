import os
import sys
import pandas as pd

# Permite ejecutar el script tanto como módulo (src.validador) como directamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.extractor import procesar_carpeta
from src.tipo_cambio import obtener_tipo_cambio
from src.database import existe_comprobante, guardar_comprobante, DB_DEFAULT


def auditar_comprobante(registro: dict, db_path: str = DB_DEFAULT) -> dict:
    """Aplica reglas de negocio tributarias, control de duplicados y conversión cambiaria."""
    errores = []
    campos_requeridos = [
        "ruc", "razon_social", "serie_numero", "fecha_emision",
        "moneda", "subtotal", "igv", "total",
    ]

    for campo in campos_requeridos:
        if registro.get(campo) is None:
            errores.append(f"Campo faltante o ilegible: {campo}")

    subtotal = registro.get("subtotal") or 0.0
    igv = registro.get("igv") or 0.0
    total = registro.get("total") or 0.0
    moneda = registro.get("moneda") or "PEN"
    fecha = registro.get("fecha_emision") or ""

    if not errores:
        igv_esperado = round(subtotal * 0.18, 2)
        if abs(igv - igv_esperado) > 0.05:
            errores.append(
                f"IGV inconsistente: esperado {igv_esperado:.2f}, registrado {igv:.2f}"
            )

        total_esperado = round(subtotal + igv, 2)
        if abs(total - total_esperado) > 0.05:
            errores.append(
                f"Suma total incorrecta: esperado {total_esperado:.2f}, registrado {total:.2f}"
            )

        if existe_comprobante(registro["ruc"], registro["serie_numero"], db_path):
            errores.append("Comprobante duplicado (RUC + Serie ya registrados en BD)")

    tc, fuente_tc = obtener_tipo_cambio(fecha, moneda) if fecha else (1.0, "Sin fecha")
    subtotal_pen = round(subtotal * tc, 2)
    igv_pen = round(igv * tc, 2)
    total_pen = round(total * tc, 2)

    estado = "OBSERVADO" if errores else "VALIDADO"
    observaciones = " | ".join(errores) if errores else "OK - Cumple reglas tributarias"

    resultado = {
        **registro,
        "tipo_cambio": tc,
        "fuente_tc": fuente_tc,
        "subtotal_pen": subtotal_pen,
        "igv_pen": igv_pen,
        "total_pen": total_pen,
        "estado": estado,
        "observaciones": observaciones,
    }

    if estado == "VALIDADO":
        guardar_comprobante(resultado, db_path)

    return resultado


def exportar_excel(resultados: list[dict], ruta_salida: str = "data/salida/reporte_conciliacion.xlsx") -> str:
    """Genera un reporte Excel auditado con pestañas de Validados, Observados y Resumen."""
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    df = pd.DataFrame(resultados)

    df_validados = df[df["estado"] == "VALIDADO"].copy()
    df_observados = df[df["estado"] == "OBSERVADO"].copy()

    resumen_data = [
        {"Indicador": "Total comprobantes procesados", "Valor": len(df)},
        {"Indicador": "Comprobantes validados", "Valor": len(df_validados)},
        {"Indicador": "Comprobantes observados / rechazados", "Valor": len(df_observados)},
        {"Indicador": "Base imponible validada (PEN)", "Valor": round(df_validados["subtotal_pen"].sum(), 2) if not df_validados.empty else 0.0},
        {"Indicador": "IGV total validado (PEN)", "Valor": round(df_validados["igv_pen"].sum(), 2) if not df_validados.empty else 0.0},
        {"Indicador": "Monto total validado (PEN)", "Valor": round(df_validados["total_pen"].sum(), 2) if not df_validados.empty else 0.0},
    ]
    df_resumen = pd.DataFrame(resumen_data)

    with pd.ExcelWriter(ruta_salida, engine="openpyxl") as writer:
        df_resumen.to_excel(writer, sheet_name="Resumen", index=False)
        df_validados.to_excel(writer, sheet_name="Validados", index=False)
        df_observados.to_excel(writer, sheet_name="Observados", index=False)

        # Autoajustar ancho de columnas en todas las pestañas
        for hoja in writer.sheets.values():
            for col in hoja.columns:
                max_len = max(len(str(celda.value or "")) for celda in col)
                hoja.column_dimensions[col[0].column_letter].width = min(max_len + 4, 45)

    return ruta_salida


def ejecutar_pipeline(
    carpeta_entrada: str = "data/entrada",
    ruta_salida: str = "data/salida/reporte_conciliacion.xlsx",
    db_path: str = DB_DEFAULT,
) -> tuple[list[dict], str]:
    """Ejecuta el flujo ETL completo de principio a fin."""
    crudos = procesar_carpeta(carpeta_entrada)
    auditados = [auditar_comprobante(reg, db_path) for reg in crudos]
    archivo_excel = exportar_excel(auditados, ruta_salida) if auditados else ""
    return auditados, archivo_excel


if __name__ == "__main__":
    resultados, excel = ejecutar_pipeline()
    for r in resultados:
        print(f"[{r['estado']}] {r['archivo']} -> Total PEN: {r['total_pen']} | {r['observaciones']}")
    print("\nReporte Excel generado en:", excel)