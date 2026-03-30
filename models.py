from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import relationship

db = SQLAlchemy()
bcrypt = Bcrypt()

class Usuario(db.Model):
    __tablename__ = 'usuario'
    idUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    data_nasc = db.Column(db.Date, nullable=False)
    
    carteiras = relationship('Carteira', back_populates='usuario', cascade="all, delete-orphan")

    def set_senha(self, senha_texto):
        self.senha = bcrypt.generate_password_hash(senha_texto).decode('utf-8')

    def check_senha(self, senha_texto):
        return bcrypt.check_password_hash(self.senha, senha_texto)


class Carteira(db.Model):
    __tablename__ = 'carteira'
    
    idCarteira = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    tipoCarteira = db.Column(db.String(50), nullable=False)
    saldo = db.Column(db.Numeric(15, 2), nullable=False, default=0.00)
    
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)
    
    usuario = relationship('Usuario', back_populates='carteiras')
    transferencias = relationship('Transferencia', back_populates='carteira', cascade="all, delete-orphan")
    graficos = relationship('Grafico', back_populates='carteira', cascade="all, delete-orphan")
    investimentos = relationship('Investimento', back_populates='carteira', cascade="all, delete-orphan")

    __mapper_args__ = {
        'polymorphic_on': tipoCarteira,
        'polymorphic_identity': 'carteira_base'
    }

    def adicionarEntrada(self, valor):
        self.saldo += valor

    def adicionarSaida(self, valor):
        if self.saldo >= valor:
            self.saldo -= valor
            return True
        return False

    def calcularSaldo(self):
        return self.saldo

class Principal(Carteira):
    __tablename__ = 'principal'
  
    idPrincipal = db.Column(db.Integer, db.ForeignKey('carteira.idCarteira'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'Principal'
    }
    
    def transferirParaMeta(self, meta_obj, valor):
        if self.adicionarSaida(valor):
            meta_obj.adicionarEntrada(valor)
            return True
        return False

class Meta(Carteira):
    __tablename__ = 'meta'
    
    idMeta = db.Column(db.Integer, db.ForeignKey('carteira.idCarteira'), primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    valorMeta = db.Column(db.Numeric(15, 2), nullable=False)
    prazoEstipulado = db.Column(db.Date, nullable=True)

    concluida = db.Column(db.Boolean, default=False)
    
    __mapper_args__ = {
        'polymorphic_identity': 'Meta'
    }

    def calcularProgresso(self):
        if self.valorMeta > 0:
            return (self.saldo / self.valorMeta) * 100
        return 0
    
    def calcularTempoEstimado(self):
        return "Not implemented"

class Transferencia(db.Model):
    __tablename__ = 'transferencia'
    
    idTransacao = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Numeric(15, 2), nullable=False)
    tipoTransferencia = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(255), nullable=False)
    
    idCarteira = db.Column(db.Integer, db.ForeignKey('carteira.idCarteira'), nullable=False)
    
    carteira = relationship('Carteira', back_populates='transferencias')
    

class Investimento(db.Model):
    __tablename__ = 'investimento'
    
    idInvestimento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipoInvestimento = db.Column(db.String(255), nullable=False)
    rentabilidade = db.Column(db.Float(10), nullable=False)
    
    idCarteira = db.Column(db.Integer, db.ForeignKey('carteira.idCarteira'), nullable=False)
    
    carteira = relationship('Carteira', back_populates='investimentos')


class Grafico(db.Model):
    __tablename__ = 'grafico'
    
    idRelatorio = db.Column(db.Integer, primary_key=True, autoincrement=True)
    periodo = db.Column(db.Date, nullable=False)
    tipoRelatorio = db.Column(db.String(255), nullable=False)
    
    idCarteira = db.Column(db.Integer, db.ForeignKey('carteira.idCarteira'), nullable=False)
    
    carteira = relationship('Carteira', back_populates='graficos')

