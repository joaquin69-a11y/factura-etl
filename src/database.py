import os
import sqlite3
from datetime import datetime

DB_DEFAULT = "data/factura_etl.db"


def inicializar_db(db_path: str = DB_DEFAULT) -> None:
    """Crea la base de datos SQLite y la tabla de auditoría si no existen."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS comprobantes_auditados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ruc TEXT NOT NULL,
                razon_social TEXT,
                serie_numero TEXT NOT NULL,
                fecha_emision TEXT,
                moneda TEXT,
                subtotal REAL,
                igv REAL,
                total REAL,
                tipo_cambio REAL,
                fuente_tc TEXT,
                total_pen REAL,
                estado TEXT,
                observaciones TEXT,
                fecha_procesamiento TEXT,
                UNIQUE(ruc, serie_numero)
            )
            """
        )


def existe_comprobante(ruc: str, serie_numero: str, db_path: str = DB_DEFAULT) -> bool:
    """Verifica si un comprobante (RUC + Serie-Número) ya fue registrado previamente."""
    inicializar_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT 1 FROM comprobantes_auditados WHERE ruc = ? AND serie_numero = ?",
            (ruc, serie_numero),
        )
        return cursor.fetchone() is not None


def guardar_comprobante(registro: dict, db_path: str = DB_DEFAULT) -> bool:
    """Inserta un comprobante validado en SQLite. Devuelve False si ya existía."""
    inicializar_db(db_path)
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT INTO comprobantes_auditados (
                    ruc, razon_social, serie_numero, fecha_emision, moneda,
                    subtotal, igv, total, tipo_cambio, fuente_tc,
                    total_pen, estado, observaciones, fecha_procesamiento
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    registro["ruc"],
                    registro["razon_social"],
                    registro["serie_numero"],
                    registro["fecha_emision"],
                    registro["moneda"],
                    registro["subtotal"],
                    registro["igv"],
                    registro["total"],
                    registro["tipo_cambio"],
                    registro["fuente_tc"],
                    registro["total_pen"],
                    registro["estado"],
                    registro["observaciones"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def obtener_historial(db_path: str = DB_DEFAULT) -> list[dict]:
    """Devuelve todos los comprobantes históricos almacenados en SQLite."""
    inicializar_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        filas = conn.execute(
            "SELECT * FROM comprobantes_auditados ORDER BY id DESC"
        ).fetchall()
        return [dict(fila) for fila in filas]


def limpiar_db(db_path: str = DB_DEFAULT) -> None:
    """Elimina los registros históricos (útil para reiniciar pruebas)."""
    if os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            conn.execute("DELETE FROM comprobantes_auditados")