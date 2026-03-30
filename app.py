import os
from flask import Flask, abort, render_template, request, redirect, url_for, session, flash
from models import db, bcrypt, Usuario, Carteira, Principal, Meta, Transferencia, Investimento, Grafico
from datetime import datetime
from decimal import Decimal
from functools import wraps 
from sqlalchemy import desc, func

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234' 

app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://neondb_owner:npg_wuOdPI0SlXs1@ep-crimson-hill-ac3il6gt-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 280

db.init_app(app)
bcrypt.init_app(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para ver esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# ROTAS DE AUTENTICAÇÃO E PERFIL
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_senha(senha):
            session['user_id'] = usuario.idUsuario
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('E-mail ou senha inválidos.', 'danger')
            
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        data_nasc_str = request.form.get('data_nascimento')
        
        if not nome or not email or not senha or not data_nasc_str:
            flash('Todos os campos são obrigatórios!', 'danger')
            return redirect(url_for('cadastro'))

        if Usuario.query.filter_by(email=email).first():
            flash('Este e-mail já está em uso.', 'warning')
            return redirect(url_for('cadastro'))

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            data_nasc=datetime.strptime(data_nasc_str, '%Y-%m-%d').date()
        )
        novo_usuario.set_senha(senha)
        db.session.add(novo_usuario)

        carteira_principal = Principal(nome="Carteira Principal", saldo=0.00, usuario=novo_usuario)
        db.session.add(carteira_principal)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça o login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    usuario = Usuario.query.get(session['user_id'])
    
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        data_nasc_str = request.form.get('data_nascimento')
        if data_nasc_str:
            usuario.data_nasc = datetime.strptime(data_nasc_str, '%Y-%m-%d').date()
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('perfil'))

    return render_template('perfil.html', usuario=usuario)

@app.route('/perfil/excluir', methods=['POST'])
@login_required
def excluir_conta():
    usuario = Usuario.query.get(session['user_id'])
    db.session.delete(usuario)
    db.session.commit()
    session.clear()
    flash('Conta excluída.', 'info')
    return redirect(url_for('login'))

@app.route('/alterar-senha', methods=['POST'])
@login_required
def alterar_senha():
    user_id = session['user_id']
    usuario = Usuario.query.get(user_id)
    
    senha_atual = request.form.get('senha_atual')
    nova_senha = request.form.get('nova_senha')
    confirma_senha = request.form.get('confirma_senha')

    if not usuario.check_senha(senha_atual):
        flash('Erro: Senha atual incorreta.', 'danger')
        return redirect(url_for('perfil')) 

    if nova_senha != confirma_senha:
        flash('Erro: A nova senha e a confirmação não coincidem.', 'danger')
        return redirect(url_for('perfil'))
        
    usuario.set_senha(nova_senha) 
    try:
        db.session.commit()
        flash('Sua senha foi alterada com sucesso!', 'success')
    except:
        db.session.rollback()
        flash('Erro ao salvar a nova senha.', 'danger')

    return redirect(url_for('perfil'))


# ==========================================
# ROTAS PRINCIPAIS (DASHBOARD E METAS)
# ==========================================
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    usuario = Usuario.query.get(user_id)
    carteira_principal = Principal.query.filter_by(idUsuario=user_id).first()
    
    # A MUDANÇA ESTÁ AQUI: Agora ele só busca metas onde concluida=False
    metas = Meta.query.filter_by(idUsuario=user_id, concluida=False).all()
    
    todas_carteiras = Carteira.query.filter_by(idUsuario=user_id).with_entities(Carteira.idCarteira).all()
    ids_carteiras = [c.idCarteira for c in todas_carteiras]
    extrato = []
    if ids_carteiras:
        extrato = Transferencia.query.filter(
            Transferencia.idCarteira.in_(ids_carteiras)
        ).order_by(desc(Transferencia.data)).limit(5).all()
    
    return render_template('dashboard.html', usuario=usuario, principal=carteira_principal, metas=metas, extrato=extrato)
@app.route('/metas')
@login_required
def metas():
    user_id = session['user_id']
    metas_ativas = Meta.query.filter_by(idUsuario=user_id, concluida=False).all()
    metas_concluidas = Meta.query.filter_by(idUsuario=user_id, concluida=True).all()
    
    return render_template('metas.html', metas=metas_ativas, concluidas=metas_concluidas)

@app.route('/criar-meta', methods=['GET', 'POST'])
@login_required
def criar_meta():
    if request.method == 'POST':
        descricao = request.form.get('descricao')
        valor_meta = request.form.get('valor_meta')
        valor_atual = request.form.get('valor_atual', 0)
        prazo_str = request.form.get('prazo')
        
        nova_meta = Meta(
            nome=descricao,
            saldo=valor_atual,
            idUsuario=session['user_id'],
            descricao=descricao,
            valorMeta=valor_meta,
            prazoEstipulado=datetime.strptime(prazo_str, '%Y-%m-%d').date() if prazo_str else None
        )
        db.session.add(nova_meta)
        db.session.commit()
        
        flash('Nova meta criada!', 'success')
        return redirect(url_for('metas'))
        
    return render_template('criar_meta.html')

@app.route('/meta/<int:meta_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_meta(meta_id):
    meta = Meta.query.get_or_404(meta_id)
    if meta.idUsuario != session['user_id']:
        abort(403) 

    if request.method == 'POST':
        meta.descricao = request.form.get('descricao')
        meta.valorMeta = request.form.get('valor_meta')
        prazo_str = request.form.get('prazo')
        meta.nome = meta.descricao 
        
        if prazo_str:
            meta.prazoEstipulado = datetime.strptime(prazo_str, '%Y-%m-%d').date()
        else:
            meta.prazoEstipulado = None 
        
        db.session.commit()
        flash('Meta atualizada!', 'success')
        return redirect(url_for('metas'))

    return render_template('editar_meta.html', meta=meta)

@app.route('/meta/<int:meta_id>/excluir', methods=['POST'])
@login_required
def excluir_meta(meta_id):
    meta = Meta.query.get_or_404(meta_id)
    if meta.idUsuario != session['user_id']:
        abort(403)
        
    principal = Principal.query.filter_by(idUsuario=session['user_id']).first()
    
    if principal and meta.saldo > 0:
        principal.saldo += meta.saldo
        flash(f'R$ {meta.saldo} devolvidos para a Carteira Principal.', 'info')
 
    db.session.delete(meta)
    db.session.commit()
    flash('Meta excluída!', 'success')
    return redirect(url_for('metas'))

@app.route('/meta/<int:meta_id>/finalizar', methods=['POST'])
@login_required
def finalizar_meta(meta_id):
    meta = Meta.query.get_or_404(meta_id)
    if meta.idUsuario != session['user_id']:
        abort(403)
    
    # Só permite finalizar se o valor foi atingido
    if meta.saldo >= meta.valorMeta:
        meta.concluida = True
        db.session.commit()
        flash(f'Parabéns! A meta "{meta.descricao}" foi concluída com sucesso! 🎉', 'success')
    else:
        flash('Você ainda não atingiu o valor total desta meta.', 'warning')
        
    return redirect(url_for('metas'))


# ==========================================
# ROTAS DE MOVIMENTAÇÕES
# ==========================================
@app.route('/movimentacoes', methods=['GET'])
@login_required
def transferir_form():
    user_id = session['user_id']
    usuario = Usuario.query.get(user_id)
    
    todas_carteiras = Carteira.query.filter_by(idUsuario=user_id).all()
    
   
    carteiras_ativas = []
    for c in todas_carteiras:
        # Se for uma Meta e estiver concluída, ele pula e não adiciona na lista
        if c.tipoCarteira == 'Meta' and getattr(c, 'concluida', False):
            continue
        carteiras_ativas.append(c)
        

    return render_template('transferir.html', carteiras=carteiras_ativas, usuario=usuario)


@app.route('/movimentacoes/adicionar-renda', methods=['POST'])
@login_required
def adicionar_renda():
    id_carteira_destino = request.form.get('id_carteira_destino')
    valor = Decimal(request.form.get('valor'))
    
    if valor <= 0:
        flash('Erro: O valor deve ser maior que zero.', 'danger')
        return redirect(url_for('transferir_form'))

    data_str = request.form.get('data')
    categoria = request.form.get('categoria')
    data = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else datetime.now().date()
    
    carteira = Carteira.query.get_or_404(id_carteira_destino)
    if carteira.idUsuario != session['user_id']:
        abort(403)
        
    carteira.adicionarEntrada(valor)
    
    nova_transferencia = Transferencia(
        data=data,
        valor=valor,
        tipoTransferencia='Entrada',
        categoria=categoria,
        idCarteira=carteira.idCarteira
    )
    db.session.add(nova_transferencia)
    db.session.commit()
    
    flash(f'R$ {valor} adicionados à carteira "{carteira.nome}"!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/movimentacoes/transferir-saldo', methods=['POST'])
@login_required
def transferir_saldo():
    id_origem = request.form.get('id_carteira_origem')
    id_destino = request.form.get('id_carteira_destino')
    valor = Decimal(request.form.get('valor'))
    
    if valor <= 0:
        flash('Erro: O valor da transferência deve ser maior que zero.', 'danger')
        return redirect(url_for('transferir_form'))

    data_str = request.form.get('data')
    data = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else datetime.now().date()
    
    if id_origem == id_destino:
        flash('Origem e destino iguais.', 'danger')
        return redirect(url_for('transferir_form'))

    origem = Carteira.query.get_or_404(id_origem)
    destino = Carteira.query.get_or_404(id_destino)
    
    if origem.idUsuario != session['user_id'] or destino.idUsuario != session['user_id']:
        abort(403)
   
    if not origem.adicionarSaida(valor):
        flash('Saldo insuficiente.', 'danger')
        return redirect(url_for('transferir_form'))
        
    destino.adicionarEntrada(valor)
    
    log_saida = Transferencia(
        data=data,
        valor=(-valor), 
        tipoTransferencia='Transferência Saída',
        categoria=f'Para {destino.nome}',
        idCarteira=origem.idCarteira
    )
    
    log_entrada = Transferencia(
        data=data,
        valor=valor,
        tipoTransferencia='Transferência Entrada',
        categoria=f'De {origem.nome}',
        idCarteira=destino.idCarteira
    )
    db.session.add_all([log_saida, log_entrada])
    db.session.commit()
    
    flash('Transferência realizada!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/movimentacoes/adicionar-despesa', methods=['POST'])
@login_required
def adicionar_despesa():
    id_carteira_origem = request.form.get('id_carteira_origem')
    valor = Decimal(request.form.get('valor'))
    
    if valor <= 0:
        flash('Erro: O valor da despesa deve ser maior que zero.', 'danger')
        return redirect(url_for('transferir_form'))

    data_str = request.form.get('data')
    categoria = request.form.get('categoria')
    data = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else datetime.now().date()
    
    carteira = Carteira.query.get_or_404(id_carteira_origem)
    if carteira.idUsuario != session['user_id']:
        abort(403)
        
    
    if not carteira.adicionarSaida(valor):
        flash('Saldo insuficiente para registrar esta despesa.', 'danger')
        return redirect(url_for('transferir_form'))
    
   
    nova_transferencia = Transferencia(
        data=data,
        valor=(-valor),
        tipoTransferencia='Saída',
        categoria=categoria,
        idCarteira=carteira.idCarteira
    )
    db.session.add(nova_transferencia)
    db.session.commit()
    
    flash(f'Despesa de R$ {valor} registrada na carteira "{carteira.nome}".', 'success')
    return redirect(url_for('dashboard'))


# ==========================================
# ROTAS DE INVESTIMENTOS E GRÁFICOS
# ==========================================
@app.route('/investimentos', methods=['GET', 'POST'])
@login_required
def investimentos():
    user_id = session['user_id']
    principal = Principal.query.filter_by(idUsuario=user_id).first()
    
    saldo_principal = principal.saldo if principal else Decimal('0.00')
    valor_simulado = saldo_principal
    
    if request.method == 'POST':
        valor_input = request.form.get('valor_simulacao')
        if valor_input and float(valor_input) > 0:
            valor_simulado = Decimal(valor_input)
        else:
            flash('Insira um valor válido maior que zero para simular.', 'warning')
            valor_simulado = saldo_principal

    mercado = {
        'selic': {'taxa': '10,75%', 'valor': valor_simulado * Decimal('1.1075')},
        'cdi': {'taxa': '10,65%', 'valor': valor_simulado * Decimal('1.1065')},
        'poupanca': {'taxa': '6,17%', 'valor': valor_simulado * Decimal('1.0617')}
    }
    
    return render_template('Investimentos.html', saldo=saldo_principal, valor_simulado=valor_simulado, mercado=mercado)

@app.route('/graficos')
@login_required
def graficos():
    user_id = session['user_id']
    usuario = Usuario.query.get(user_id)
    lista_metas = Meta.query.filter_by(idUsuario=user_id).all()
    
    todas_carteiras = Carteira.query.filter_by(idUsuario=user_id).with_entities(Carteira.idCarteira).all()
    ids_carteiras = [c.idCarteira for c in todas_carteiras]
    
    total_entradas = 0
    total_saidas = 0
    movimentacoes = []

    if ids_carteiras:
        total_entradas = db.session.query(func.sum(Transferencia.valor)).filter(
            Transferencia.idCarteira.in_(ids_carteiras),
            Transferencia.valor > 0 
        ).scalar() or 0
        
        total_saidas_db = db.session.query(func.sum(Transferencia.valor)).filter(
            Transferencia.idCarteira.in_(ids_carteiras),
            Transferencia.valor < 0
        ).scalar() or 0
        total_saidas = abs(total_saidas_db)

        movimentacoes = Transferencia.query.filter(
            Transferencia.idCarteira.in_(ids_carteiras)
        ).order_by(Transferencia.data.asc()).limit(20).all()

    nomes_metas = [m.descricao for m in lista_metas]
    valores_alcancados = [float(m.saldo) for m in lista_metas]
    valores_alvo = [float(m.valorMeta) for m in lista_metas]
    
    datas_mov = [m.data.strftime('%d/%m') for m in movimentacoes]
    valores_mov = [float(m.valor) for m in movimentacoes]

    return render_template('graficos.html',
                           usuario=usuario,
                           grafico_financas={'entradas': float(total_entradas), 'saidas': float(total_saidas)},
                           grafico_metas={'nomes': nomes_metas, 'atuais': valores_alcancados, 'alvos': valores_alvo},
                           grafico_evolucao={'labels': datas_mov, 'data': valores_mov})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)