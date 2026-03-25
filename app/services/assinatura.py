import os
import uuid
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
from zoneinfo import ZoneInfo
from app.utils.pdf_utils import criar_marca_dagua
from app.config import TEMP_DIR

def aplicar_assinatura(pdf_bytes, nome, tipo):

    if not pdf_bytes:
        raise ValueError("PDF inválido")

    uid = str(uuid.uuid4())

    entrada = os.path.join(TEMP_DIR, f"entrada_{uid}.pdf")
    marca = os.path.join(TEMP_DIR, f"marca_{uid}.pdf")
    saida = os.path.join(TEMP_DIR, f"saida_{uid}.pdf")

    try:
        # salvar PDF original
        with open(entrada, "wb") as f:
            f.write(pdf_bytes)

        # data/hora atual (corrigido para Brasil)
        data_hora = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M")

        # criar marca d'água
        criar_marca_dagua(nome, data_hora, tipo, marca)

        reader = PdfReader(entrada)
        watermark = PdfReader(marca)
        writer = PdfWriter()

        marca_page = watermark.pages[0]

        for page in reader.pages:
            page.merge_page(marca_page)
            writer.add_page(page)

        # salvar resultado
        with open(saida, "wb") as f:
            writer.write(f)

        # retornar bytes
        with open(saida, "rb") as f:
            return f.read()

    finally:
        # limpar arquivos temporários
        for file in [entrada, marca, saida]:
            if os.path.exists(file):
                os.remove(file)