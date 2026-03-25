from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.services.assinatura import aplicar_assinatura
import base64
from fastapi.responses import Response

app = FastAPI()


# ==============================
# HEALTH CHECK (IMPORTANTE)
# ==============================
@app.get("/health")
def health():
    return {"status": "ok"}


# ==============================
# ASSINATURA DO COLABORADOR
# ==============================
@app.post("/assinar-colaborador/{folha_id}")
def assinar_colaborador(folha_id: int, db: Session = Depends(get_db)):

    result = db.execute(text("""
        SELECT anexo, colaborador_nome
        FROM dbo.rh_folha_ponto
        WHERE folha_ponto_id = :id
    """), {"id": folha_id}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    pdf_bytes = result[0]
    nome = result[1]

    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Registro sem PDF")

    pdf_assinado = aplicar_assinatura(pdf_bytes, nome, "colaborador")

    db.execute(text("""
        UPDATE dbo.rh_folha_ponto
        SET 
            anexo = :pdf,
            status = 'ASSINADO_COLAB'
        WHERE folha_ponto_id = :id
    """), {
        "pdf": pdf_assinado,
        "id": folha_id
    })

    db.commit()

    return {
        "status": "assinado pelo colaborador",
        "folha_id": folha_id
    }


# ==============================
# ASSINATURA DO GESTOR
# ==============================
@app.post("/assinar-gestor/{folha_id}")
def assinar_gestor(folha_id: int, db: Session = Depends(get_db)):

    result = db.execute(text("""
        SELECT anexo, gestor_nome
        FROM dbo.rh_folha_ponto
        WHERE folha_ponto_id = :id
    """), {"id": folha_id}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    pdf_bytes = result[0]
    nome = result[1]

    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Registro sem PDF")

    pdf_assinado = aplicar_assinatura(pdf_bytes, nome, "gestor")

    db.execute(text("""
        UPDATE dbo.rh_folha_ponto
        SET 
            anexo = :pdf,
            status = 'ASSINADO_GESTOR',
            data_aprovacao = GETDATE()
        WHERE folha_ponto_id = :id
    """), {
        "pdf": pdf_assinado,
        "id": folha_id
    })

    db.commit()

    return {
        "status": "assinado pelo gestor",
        "folha_id": folha_id
    }


# ==============================
# OBTER PDF (BASE64)
# ==============================
@app.get("/obter-pdf/{folha_id}")
def obter_pdf(folha_id: int, db: Session = Depends(get_db)):

    result = db.execute(text("""
        SELECT anexo
        FROM dbo.rh_folha_ponto
        WHERE folha_ponto_id = :id
    """), {"id": folha_id}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    pdf_bytes = result[0]

    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="PDF vazio")

    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    return {
        "folha_id": folha_id,
        "arquivo_base64": pdf_base64
    }


# ==============================
# DOWNLOAD DIRETO
# ==============================
@app.get("/download-pdf/{folha_id}")
def download_pdf(folha_id: int, db: Session = Depends(get_db)):

    result = db.execute(text("""
        SELECT anexo
        FROM dbo.rh_folha_ponto
        WHERE folha_ponto_id = :id
    """), {"id": folha_id}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    pdf_bytes = result[0]

    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="PDF vazio")

    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=folha_{folha_id}.pdf"}
    )