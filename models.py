from sqlalchemy import Column, String, Numeric, Integer, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base

class Produto(Base):
    __tablename__ = "produtos"

    id_produto = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(Text, nullable=False)
    plataforma = Column(Text, nullable=False)
    pais = Column(Text, nullable=False)
    nicho = Column(Text)
    preco = Column(Numeric)
    comissao_percentual = Column(Numeric)
    comissao_valor = Column(Numeric)
    link_venda = Column(Text)
    link_afiliado = Column(Text)
    moeda = Column(Text)
    ativo = Column(Boolean)
    data_criacao = Column(TIMESTAMP)
    data_atualizacao = Column(TIMESTAMP)

class MetricasPlataforma(Base):
    __tablename__ = "metricas_plataforma"

    id_metrica = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_produto = Column(UUID(as_uuid=True), ForeignKey("produtos.id_produto"))

    epc = Column(Numeric)
    cvr = Column(Numeric)
    refund = Column(Numeric)
    vendas_7d = Column(Integer)
    vendas_30d = Column(Integer)
    gravidade = Column(Numeric)
    tickets_suporte = Column(Integer)

    data_atualizacao = Column(TIMESTAMP)

class MetricasInteligentes(Base):
    __tablename__ = "metricas_inteligentes"

    id_inteligencia = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_produto = Column(UUID(as_uuid=True), ForeignKey("produtos.id_produto"))

    score_lucratividade = Column(Numeric)
    score_estabilidade = Column(Numeric)
    score_tendencia = Column(Numeric)
    score_risco = Column(Numeric)
    score_global_final = Column(Numeric)

    selo_recomendacao = Column(Text)
    data_atualizacao = Column(TIMESTAMP)
