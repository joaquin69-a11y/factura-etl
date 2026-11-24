# 📊 FacturaETL — Pipeline de Auditoría Tributaria y Conciliación Cambiaria

Sistema modular en Python que automatiza la extracción de datos desde comprobantes electrónicos en PDF, audita reglas tributarias (cálculo de IGV y consistencia de montos), previene el registro de documentos duplicados mediante persistencia en SQLite y realiza la conciliación cambiaria consultando el tipo de cambio oficial de SUNAT.

## 🎯 Problema que Resuelve
En procesos contables y de auditoría financiera, validar manualmente comprobantes emitidos en distintas monedas (`PEN` y `USD`), cruzar fechas de emisión con el tipo de cambio oficial diario y detectar errores de cálculo o facturas duplicadas consume tiempo operativo y es propenso a errores humanos. **FacturaETL** automatiza este flujo de extremo a extremo.

## 🚀 Arquitectura del Pipeline (ETL)

1. **Extracción (`src/extractor.py`):** Lectura estructurada de archivos PDF mediante `pdfplumber` y extracción de campos clave (`RUC`, `Razón Social`, `Serie-Número`, `Fecha`, `Moneda`, `Subtotal`, `IGV` y `Total`) usando expresiones regulares.
2. **Enriquecimiento Cambiario (`src/tipo_cambio.py`):** Consulta automática del tipo de cambio venta oficial de SUNAT según la fecha de emisión de cada comprobante, incorporando caché en memoria para evitar peticiones HTTP repetidas y un mecanismo de respaldo local (*fallback*).
3. **Transformación y Auditoría (`src/validador.py`):**
   - **Integridad de datos:** Verifica que ningún campo obligatorio sea nulo o ilegible.
   - **Auditoría tributaria:** Recalcula el IGV (18%) y la suma total (`Subtotal + IGV`), marcando como `OBSERVADO` cualquier comprobante con desviaciones.
   - **Control de duplicados:** Valida contra la base de datos que la combinación única `RUC + Serie-Número` no haya sido procesada previamente.
   - **Estandarización monetaria:** Convierte todos los importes a moneda nacional (`PEN`).
4. **Persistencia y Carga (`src/database.py` & Excel):** Almacena el historial de comprobantes aprobados en `SQLite3` y exporta un libro de Excel (`.xlsx`) con pestañas separadas para `Resumen`, `Validados` y `Observados`.
5. **Interfaz Web (`app.py`):** Tablero interactivo desarrollado en `Streamlit` para cargar lotes de PDFs, ejecutar el pipeline con un clic, inspeccionar la base de datos histórica y descargar el reporte auditado.

## 🛠️ Stack Tecnológico
- **Lenguaje:** Python 3
- **Extracción y Generación Documental:** `pdfplumber`, `fpdf2`
- **Procesamiento y Reportes:** `Pandas`, `OpenPyXL`
- **Integración y Persistencia:** `Requests` (API REST SUNAT), `SQLite3`
- **Interfaz de Usuario:** `Streamlit`

## 📂 Estructura del Proyecto
```text
factura-etl/
├── data/
│   ├── entrada/          # Comprobantes PDF a procesar
│   └── salida/           # Reportes Excel auditados (.xlsx)
├── src/
│   ├── __init__.py
│   ├── extractor.py      # Extracción de texto y parsing con Regex
│   ├── tipo_cambio.py    # Cliente API SUNAT con caché y fallback
│   ├── database.py       # Gestión de persistencia y unicidad en SQLite
│   └── validador.py      # Reglas de auditoría y exportación Excel
├── app.py                # Aplicación web interactiva en Streamlit
├── generar_muestras.py   # Generador de dataset PDF de prueba
├── requirements.txt      # Dependencias del entorno virtual
└── README.md             # Documentación técnica del proyecto
```

## ⚙️ Instalación y Ejecución Local

```bash
# 1. Clonar el repositorio
git clone [https://github.com/joaquin69-a11y/factura-etl.git](https://github.com/joaquin69-a11y/factura-etl.git)
cd factura-etl

# 2. Crear y activar el entorno virtual (Windows)
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Generar comprobantes PDF de prueba (incluye casos válidos, con error de IGV y duplicados)
python generar_muestras.py

# 5. Ejecutar la interfaz web
streamlit run app.py
```

*(Opcional: Para ejecutar únicamente el motor por consola sin interfaz gráfica, corre `python src/validador.py`).*