from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

MM_TO_PT = 2.83465

def mm_to_pt(mm):
    return mm * MM_TO_PT


def criar_marca_dagua(nome, data_hora, tipo, output):
    c = canvas.Canvas(output, pagesize=A4)

    # dimensões da área da assinatura
    largura_box_mm = 70
    altura_box_mm = 18

    # posição Y (top → bottom) + ajuste
    y_mm = 297 - 264 - altura_box_mm

    # posição X (cada tipo mantém seu lado)
    if tipo == "colaborador":
        x_mm = 130
    else:
        x_mm = 8

    # converter
    x = mm_to_pt(x_mm)
    y = mm_to_pt(y_mm)

    largura_box = mm_to_pt(largura_box_mm)

    # limitar nome
    nome = nome[:60]

    # =========================
    # LINHA DE ASSINATURA
    # =========================
    c.setLineWidth(1)
    c.line(x, y + 20, x + largura_box, y + 20)

    # =========================
    # NOME (destaque)
    # =========================
    c.setFont("Helvetica-Bold", 12)

    nome_width = c.stringWidth(nome, "Helvetica-Bold", 12)
    nome_x = x + (largura_box - nome_width) / 2

    c.drawString(nome_x, y + 5, nome)

    # =========================
    # DATA (menor e discreta)
    # =========================
    c.setFont("Helvetica", 9)

    data_width = c.stringWidth(data_hora, "Helvetica", 9)
    data_x = x + (largura_box - data_width) / 2

    c.drawString(data_x, y - 5, data_hora)

    c.save()