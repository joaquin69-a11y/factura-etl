import os
from fpdf import FPDF

os.makedirs("data/entrada", exist_ok=True)

comprobantes = [
    {
        "archivo": "factura_01.pdf",
        "ruc": "20601234567",
        "empresa": "TECH SOLUTIONS PERU S.A.C.",
        "serie": "F001-0000101",
        "fecha": "2026-11-10",
        "moneda": "USD",
        "subtotal": 1000.00,
        "igv": 180.00,
        "total": 1180.00,
    },
    {
        "archivo": "factura_02.pdf",
        "ruc": "20519876543",
        "empresa": "LOGISTICA ANDINA S.A.",
        "serie": "F001-0000452",
        "fecha": "2026-11-12",
        "moneda": "PEN",
        "subtotal": 2500.00,
        "igv": 450.00,
        "total": 2950.00,
    },
    {
        "archivo": "factura_03.pdf",
        "ruc": "20481122334",
        "empresa": "CLOUD SERVICES LATAM E.I.R.L.",
        "serie": "E001-0000089",
        "fecha": "2026-11-15",
        "moneda": "USD",
        "subtotal": 500.00,
        "igv": 90.00,
        "total": 590.00,
    },
    {
        # Error intencional de IGV para probar el motor de auditoria
        "archivo": "factura_04_error.pdf",
        "ruc": "20609988776",
        "empresa": "SUMINISTROS INDUSTRIALES S.A.C.",
        "serie": "F002-0000310",
        "fecha": "2026-11-18",
        "moneda": "PEN",
        "subtotal": 1000.00,
        "igv": 150.00,
        "total": 1150.00,
    },
    {
        # Duplicado intencional de factura_01 para probar control de duplicados
        "archivo": "factura_05_duplicada.pdf",
        "ruc": "20601234567",
        "empresa": "TECH SOLUTIONS PERU S.A.C.",
        "serie": "F001-0000101",
        "fecha": "2026-11-10",
        "moneda": "USD",
        "subtotal": 1000.00,
        "igv": 180.00,
        "total": 1180.00,
    },
]

for comp in comprobantes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "FACTURA ELECTRONICA", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", size=11)
    lineas = [
        f"RUC Emisor: {comp['ruc']}",
        f"Razon Social: {comp['empresa']}",
        f"Serie-Numero: {comp['serie']}",
        f"Fecha Emision: {comp['fecha']}",
        f"Moneda: {comp['moneda']}",
        f"Subtotal: {comp['subtotal']:.2f}",
        f"IGV (18%): {comp['igv']:.2f}",
        f"Total: {comp['total']:.2f}",
    ]
    for linea in lineas:
        pdf.cell(0, 8, linea, new_x="LMARGIN", new_y="NEXT")

    ruta = os.path.join("data", "entrada", comp["archivo"])
    pdf.output(ruta)

print("5 comprobantes PDF generados correctamente en data/entrada/")