import os
import pandas as pd
import streamlit as st
from src.validador import ejecutar_pipeline
from src.database import obtener_historial, limpiar_db

st.set_page_config(
    page_title="FacturaETL | Auditoría y Conciliación Cambiaria",
    page_icon="📊",
    layout="wide",
)

st.title("📊 FacturaETL — Auditoría de Comprobantes y Tipo de Cambio")
st.caption("Pipeline automatizado de extracción PDF, validación tributaria (IGV), control de duplicados en SQLite y conciliación SUNAT.")

# --- Barra lateral: Carga de archivos y controles ---
with st.sidebar:
    st.header("1. Carga de Comprobantes")
    archivos_subidos = st.file_uploader(
        "Sube facturas en PDF (opcional)",
        type=["pdf"],
        accept_multiple_files=True,
    )
    if archivos_subidos:
        os.makedirs("data/entrada", exist_ok=True)
        for archivo in archivos_subidos:
            ruta_destino = os.path.join("data", "entrada", archivo.name)
            with open(ruta_destino, "wb") as f:
                f.write(archivo.getbuffer())
        st.success(f"{len(archivos_subidos)} archivo(s) guardados en data/entrada/")

    st.divider()
    st.header("2. Ejecución del Pipeline")
    ejecutar = st.button("🚀 Ejecutar Auditoría ETL", type="primary", use_container_width=True)

    st.divider()
    st.header("3. Mantenimiento (Demo)")
    if st.button("🗑️ Reiniciar Base de Datos SQLite", use_container_width=True):
        limpiar_db()
        st.session_state.pop("resultados", None)
        st.session_state.pop("excel_path", None)
        st.info("Base de datos limpia. Puedes volver a auditar el lote desde cero.")

# --- Ejecución del flujo ---
if ejecutar:
    with st.spinner("Extrayendo datos de PDFs, consultando tipo de cambio SUNAT y auditando..."):
        resultados, ruta_excel = ejecutar_pipeline()
        if not resultados:
            st.warning("No se encontraron archivos PDF en data/entrada/.")
        else:
            st.session_state["resultados"] = resultados
            st.session_state["excel_path"] = ruta_excel

# --- Visualización de resultados ---
if "resultados" in st.session_state and st.session_state["resultados"]:
    df = pd.DataFrame(st.session_state["resultados"])
    df_val = df[df["estado"] == "VALIDADO"]
    df_obs = df[df["estado"] == "OBSERVADO"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Procesados", len(df))
    col2.metric("Validados", len(df_val))
    col3.metric("Observados", len(df_obs))
    col4.metric("Total Validado (PEN)", f"S/ {df_val['total_pen'].sum():,.2f}")

    st.divider()

    tab_lote, tab_bd = st.tabs(["📋 Resultados del Lote Actual", "🗄️ Historial Persistido (SQLite)"])

    with tab_lote:
        columnas_vista = [
            "archivo", "estado", "ruc", "razon_social", "serie_numero",
            "fecha_emision", "moneda", "total", "tipo_cambio", "fuente_tc",
            "total_pen", "observaciones",
        ]
        st.dataframe(df[columnas_vista], use_container_width=True, hide_index=True)

        excel_path = st.session_state.get("excel_path", "")
        if excel_path and os.path.exists(excel_path):
            with open(excel_path, "rb") as f:
                st.download_button(
                    label="📥 Descargar Reporte Auditado (.xlsx)",
                    data=f.read(),
                    file_name="reporte_conciliacion.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

    with tab_bd:
        historial = obtener_historial()
        if historial:
            st.dataframe(pd.DataFrame(historial), use_container_width=True, hide_index=True)
        else:
            st.info("Aún no hay registros guardados en la base de datos.")
else:
    st.info("Haz clic en **🚀 Ejecutar Auditoría ETL** en el menú izquierdo para procesar los comprobantes de `data/entrada/`.")