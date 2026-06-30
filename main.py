from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()

engine = create_engine("sqlite:///produtos.db")
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class ProdutoDB(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    preco = Column(Float)

Base.metadata.create_all(bind=engine)

class Produto(BaseModel):
    nome: str
    preco: float

@app.get("/")
def inicio():
    return {"mensagem": "API Marketplace com banco de dados funcionando!"}

@app.post("/produtos")
def criar_produto(produto: Produto):
    db = SessionLocal()

    novo_produto = ProdutoDB(
        nome=produto.nome,
        preco=produto.preco
    )

    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    db.close()

    return novo_produto

@app.get("/produtos")
def listar_produtos():
    db = SessionLocal()
    produtos = db.query(ProdutoDB).all()
    db.close()
    return produtos
@app.get("/produtos/{produto_id}")
def buscar_produto(produto_id: int):
    db = SessionLocal()
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    db.close()

    if produto:
        return produto

    return {"erro": "Produto não encontrado"}
@app.delete("/produtos/{produto_id}")
def excluir_produto(produto_id: int):
    db = SessionLocal()
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()

    if produto:
        db.delete(produto)
        db.commit()
        db.close()
        return {"mensagem": "Produto excluído com sucesso!"}

    db.close()
    return {"erro": "Produto não encontrado"}
@app.put("/produtos/{produto_id}")
def atualizar_produto(produto_id: int, produto: Produto):
    db = SessionLocal()

    produto_db = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()

    if produto_db:
        produto_db.nome = produto.nome
        produto_db.preco = produto.preco

        db.commit()
        db.refresh(produto_db)
        db.close()

        return {
            "mensagem": "Produto atualizado com sucesso!",
            "produto": produto_db
        }

    db.close()
    return {"erro": "Produto não encontrado"}