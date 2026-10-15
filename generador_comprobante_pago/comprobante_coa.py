"""
Comprobante Coa - aplicación sencilla para generar facturas PDF.

Instalación:
    python -m pip install --upgrade ttkbootstrap reportlab pypdf

Ejecución:
    python comprobante_coa.py

La aplicación genera el PDF con ReportLab. La plantilla PDF adjunta contiene
datos de ejemplo impresos, por lo que se reproduce su estructura (encabezado,
cliente, tabla de productos y total) sin conservar esos ejemplos en la factura.
"""

import os
import re
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from decimal import Decimal, InvalidOperation

import ttkbootstrap as ttk
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib.units import inch


CURSOS = ("Python básico", "Python intermedio")


def crear_pdf(ruta, nombre, fecha, productos):
    """Crea una factura con los datos del cliente y las compras acumuladas."""
    doc = SimpleDocTemplate(
        ruta, pagesize=letter,
        rightMargin=0.65 * inch, leftMargin=0.65 * inch,
        topMargin=0.60 * inch, bottomMargin=0.60 * inch
    )
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        name="TituloFactura", parent=estilos["Title"], fontSize=24,
        leading=28, alignment=TA_RIGHT, textColor=colors.HexColor("#243746"),
        spaceAfter=8
    ))
    estilos.add(ParagraphStyle(
        name="Etiqueta", parent=estilos["Normal"], fontSize=9,
        textColor=colors.HexColor("#5B6570"), leading=12
    ))
    estilos.add(ParagraphStyle(
        name="Valor", parent=estilos["Normal"], fontSize=11, leading=15
    ))
    estilos.add(ParagraphStyle(
        name="Total", parent=estilos["Normal"], fontSize=13,
        leading=16, alignment=TA_RIGHT, textColor=colors.HexColor("#243746")
    ))

    historia = []
    cabecera = Table(
        [[Paragraph("<b>COMPROBANTE COA</b>", estilos["Heading2"]),
          Paragraph("FACTURA", estilos["TituloFactura"])]],
        colWidths=[3.6 * inch, 3.0 * inch]
    )
    cabecera.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.2, colors.HexColor("#3B82A0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    historia.extend([cabecera, Spacer(1, 18)])

    fecha_emision = datetime.now().strftime("%d/%m/%Y")
    datos_cliente = Table([
        [Paragraph("CLIENTE", estilos["Etiqueta"]),
         Paragraph("FECHA DE PAGO", estilos["Etiqueta"]),
         Paragraph("FECHA DE EMISIÓN", estilos["Etiqueta"])],
        [Paragraph(nombre, estilos["Valor"]),
         Paragraph(fecha, estilos["Valor"]),
         Paragraph(fecha_emision, estilos["Valor"])],
    ], colWidths=[3.1 * inch, 1.7 * inch, 1.8 * inch])
    datos_cliente.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2F5F7")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D6DEE4")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
        ("TOPPADDING", (0, 1), (-1, 1), 3),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
    ]))
    historia.extend([datos_cliente, Spacer(1, 26)])

    filas = [["Curso / descripción", "Monto"]]
    total = Decimal("0.00")
    for producto in productos:
        monto = producto["monto"]
        total += monto
        filas.append([producto["curso"], f"$ {monto:,.2f}"])

    tabla = Table(filas, colWidths=[4.8 * inch, 1.8 * inch], repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243746")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D6DEE4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F6F8F9")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    historia.append(tabla)
    historia.append(Spacer(1, 12))
    total_tabla = Table(
        [["TOTAL", f"$ {total:,.2f}"]],
        colWidths=[4.8 * inch, 1.8 * inch]
    )
    total_tabla.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 13),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#243746")),
        ("LINEABOVE", (0, 0), (-1, -1), 1.2, colors.HexColor("#3B82A0")),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    historia.append(total_tabla)
    historia.append(Spacer(1, 35))
    historia.append(Paragraph(
        "Comprobante de pago emitido con la información proporcionada.",
        ParagraphStyle("Nota", parent=estilos["Normal"], fontSize=9,
                       textColor=colors.HexColor("#697681"), alignment=TA_CENTER)
    ))

    def pie_pagina(canvas, documento):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D6DEE4"))
        canvas.line(0.65 * inch, 0.45 * inch, letter[0] - 0.65 * inch, 0.45 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#697681"))
        canvas.drawRightString(letter[0] - 0.65 * inch, 0.27 * inch,
                               f"Página {documento.page}")
        canvas.restoreState()

    doc.build(historia, onFirstPage=pie_pagina, onLaterPages=pie_pagina)


class ComprobanteCoa:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Facturas - Comprobante Coa")
        self.root.geometry("980x800")
        self.root.minsize(850, 650)
        self.productos = []

        contenedor = ttk.Frame(root, padding=22)
        contenedor.pack(fill="both", expand=True)

        ttk.Label(
            contenedor, text="👤  Comprobante de pago",
            font=("Segoe UI", 24, "bold"), bootstyle="info"
        ).pack(pady=(24, 32))

        formulario = ttk.Labelframe(
            contenedor, text="Datos de la compra", padding=25, bootstyle="secondary"
        )
        formulario.pack(fill="x", padx=100)

        formulario.columnconfigure(0, weight=1)
        formulario.columnconfigure(1, weight=1)

        ttk.Label(formulario, text="Nombre").grid(
            row=0, column=0, sticky="w", padx=12, pady=(5, 7)
        )
        ttk.Label(formulario, text="Curso").grid(
            row=0, column=1, sticky="w", padx=12, pady=(5, 7)
        )
        self.nombre_var = tk.StringVar()
        self.curso_var = tk.StringVar()
        self.fecha_var = tk.StringVar()
        self.monto_var = tk.StringVar()

        self.nombre_entry = ttk.Entry(formulario, textvariable=self.nombre_var)
        self.nombre_entry.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 22), ipady=5)
        self.curso_combo = ttk.Combobox(
            formulario, textvariable=self.curso_var, values=CURSOS, state="readonly"
        )
        self.curso_combo.grid(row=1, column=1, sticky="ew", padx=12, pady=(0, 22), ipady=5)
        self.curso_combo.set("")

        ttk.Label(formulario, text="Fecha de pago (DD/MM/AAAA)").grid(
            row=2, column=0, sticky="w", padx=12, pady=(0, 7)
        )
        ttk.Label(formulario, text="Monto").grid(
            row=2, column=1, sticky="w", padx=12, pady=(0, 7)
        )
        self.fecha_entry = ttk.Entry(formulario, textvariable=self.fecha_var)
        self.fecha_entry.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 5), ipady=5)
        self.monto_entry = ttk.Entry(formulario, textvariable=self.monto_var)
        self.monto_entry.grid(row=3, column=1, sticky="ew", padx=12, pady=(0, 5), ipady=5)

        acciones = ttk.Frame(contenedor)
        acciones.pack(fill="x", padx=100, pady=20)
        ttk.Button(
            acciones, text="Guardar producto", bootstyle="success",
            command=self.guardar_producto
        ).pack(side="left", padx=(0, 10), ipadx=10, ipady=7)
        ttk.Button(
            acciones, text="Generar factura", bootstyle="primary",
            command=self.generar_factura
        ).pack(side="right", ipadx=18, ipady=7)

        resumen = ttk.Labelframe(
            contenedor, text="Productos guardados para esta factura", padding=12,
            bootstyle="secondary"
        )
        resumen.pack(fill="both", expand=True, padx=100, pady=(0, 8))
        columnas = ("curso", "monto")
        self.lista = ttk.Treeview(
            resumen, columns=columnas, show="headings", height=7, bootstyle="info"
        )
        self.lista.heading("curso", text="Curso")
        self.lista.heading("monto", text="Monto")
        self.lista.column("curso", width=500, anchor="w")
        self.lista.column("monto", width=180, anchor="e")
        self.lista.pack(fill="both", expand=True)
        self.estado_var = tk.StringVar(value="No hay productos guardados.")
        ttk.Label(resumen, textvariable=self.estado_var, bootstyle="secondary").pack(
            anchor="w", pady=(8, 0)
        )

        ttk.Label(
            contenedor,
            text="Guarda cada compra y genera una factura con los productos de esta sesión.",
            bootstyle="secondary"
        ).pack(pady=(5, 0))

    def leer_compra(self):
        nombre = self.nombre_var.get().strip()
        curso = self.curso_var.get().strip()
        fecha = self.fecha_var.get().strip()
        monto_texto = self.monto_var.get().strip()

        faltantes = []
        if not nombre:
            faltantes.append("nombre")
        if not curso:
            faltantes.append("curso")
        if not fecha:
            faltantes.append("fecha de pago")
        if not monto_texto:
            faltantes.append("monto")
        if faltantes:
            messagebox.showwarning(
                "Datos incompletos",
                "Completa estos campos antes de continuar: " + ", ".join(faltantes) + "."
            )
            return None

        try:
            fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")
            fecha_normalizada = fecha_obj.strftime("%d/%m/%Y")
        except ValueError:
            messagebox.showwarning(
                "Fecha incorrecta", "Usa una fecha válida con el formato DD/MM/AAAA."
            )
            return None

        try:
            monto = Decimal(monto_texto.replace(",", "").replace("$", "").strip())
            if not monto.is_finite() or monto <= 0:
                raise InvalidOperation
            monto = monto.quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            messagebox.showwarning(
                "Monto incorrecto", "Introduce un monto numérico mayor que cero, por ejemplo 125.50."
            )
            return None

        return {
            "nombre": nombre,
            "curso": curso,
            "fecha": fecha_normalizada,
            "monto": monto
        }

    def limpiar_campos(self):
        self.nombre_var.set("")
        self.curso_var.set("")
        self.fecha_var.set("")
        self.monto_var.set("")
        self.nombre_entry.focus_set()

    def actualizar_resumen(self):
        for elemento in self.lista.get_children():
            self.lista.delete(elemento)
        total = Decimal("0.00")
        for producto in self.productos:
            total += producto["monto"]
            self.lista.insert(
                "", "end",
                values=(producto["curso"], f"$ {producto['monto']:,.2f}")
            )
        if self.productos:
            self.estado_var.set(
                f"{len(self.productos)} producto(s) guardado(s) · Total: $ {total:,.2f}"
            )
        else:
            self.estado_var.set("No hay productos guardados.")

    def guardar_producto(self):
        compra = self.leer_compra()
        if compra is None:
            return
        # Todos los productos de una misma factura deben pertenecer al mismo cliente y fecha.
        if self.productos:
            primero = self.productos[0]
            if compra["nombre"].casefold() != primero["nombre"].casefold():
                messagebox.showwarning(
                    "Cliente diferente",
                    "Todos los productos de una factura deben tener el mismo nombre. "
                    "Genera la factura actual antes de empezar otra."
                )
                return
            if compra["fecha"] != primero["fecha"]:
                messagebox.showwarning(
                    "Fecha diferente",
                    "Todos los productos de una factura deben tener la misma fecha de pago."
                )
                return
        self.productos.append(compra)
        self.actualizar_resumen()
        self.limpiar_campos()

    def generar_factura(self):
        # Si hay campos actuales, deben contener una compra completa; nunca se ignoran campos a medias.
        campos_actuales = [
            self.nombre_var.get().strip(),
            self.curso_var.get().strip(),
            self.fecha_var.get().strip(),
            self.monto_var.get().strip()
        ]
        hay_algo_escrito = any(campos_actuales)
        productos_factura = list(self.productos)

        if hay_algo_escrito:
            compra_actual = self.leer_compra()
            if compra_actual is None:
                return
            if productos_factura:
                primero = productos_factura[0]
                if compra_actual["nombre"].casefold() != primero["nombre"].casefold():
                    messagebox.showwarning(
                        "Cliente diferente",
                        "La compra actual debe pertenecer al mismo cliente que los productos guardados."
                    )
                    return
                if compra_actual["fecha"] != primero["fecha"]:
                    messagebox.showwarning(
                        "Fecha diferente",
                        "La compra actual debe tener la misma fecha de pago que los productos guardados."
                    )
                    return
            productos_factura.append(compra_actual)

        if not productos_factura:
            messagebox.showwarning(
                "Factura vacía",
                "Completa una compra en los campos o guarda al menos un producto antes de generar."
            )
            return

        nombre = productos_factura[0]["nombre"]
        fecha = productos_factura[0]["fecha"]
        nombre_seguro = re.sub(r"[^A-Za-z0-9_-]+", "_", nombre).strip("_") or "Cliente"
        ruta_sugerida = f"Comprobante_{nombre_seguro}.pdf"
        ruta = filedialog.asksaveasfilename(
            title="Guardar factura PDF",
            defaultextension=".pdf",
            initialfile=ruta_sugerida,
            filetypes=[("Documento PDF", "*.pdf")]
        )
        if not ruta:
            return

        try:
            crear_pdf(ruta, nombre, fecha, productos_factura)
        except Exception as error:
            messagebox.showerror(
                "Error al generar PDF",
                f"No se pudo guardar la factura.\n\nDetalle: {error}"
            )
            return

        # Solo se limpian los productos después de crear correctamente el PDF.
        self.productos.clear()
        self.actualizar_resumen()
        self.limpiar_campos()
        messagebox.showinfo("Factura generada", f"La factura se guardó correctamente en:\n{ruta}")


if __name__ == "__main__":
    ventana = ttk.Window(themename="solar")
    aplicacion = ComprobanteCoa(ventana)
    ventana.mainloop()
