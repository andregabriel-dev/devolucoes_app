import os
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file
from config import Config
from models import db, Usuario, Devolucao
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename

# --- RELATÓRIO EM PDF (SOMENTE GERENTE) ---
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session: return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*perfis):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('perfil') not in perfis:
                flash("Acesso restrito.")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- ROTAS DE ACESSO ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(email=request.form['email']).first()
        if user and user.check_senha(request.form['senha']):
            session.update({'user_id': user.id, 'perfil': user.perfil, 'nome': user.nome})
            return redirect(url_for('dashboard'))
        flash("Email ou senha inválidos.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    busca = request.args.get('q', '')
    
    query = Devolucao.query

    if session['perfil'] == 'vendedor':
        query = query.filter(Devolucao.vendedor_id == session['user_id'])

    if busca:
        query = query.filter(
            (Devolucao.cliente.ilike(f'%{busca}%')) | 
            (Devolucao.nf_cliente.ilike(f'%{busca}%')) | 
            (Devolucao.nf_interna.ilike(f'%{busca}%'))
        )

    devolucoes = query.order_by(Devolucao.data_criacao.desc()).all()
    
    return render_template('dashboard.html', devolucoes=devolucoes, busca=busca)

# --- FLUXO DE DEVOLUÇÃO ---
@app.route('/nova', methods=['GET', 'POST'])
@login_required
@roles_required('vendedor', 'conferente', 'gerente')
def nova_devolucao():
    if request.method == 'POST':
        f = request.files.get('pdf_nota')
        fname = secure_filename(f.filename) if f and f.filename != '' else None
        if fname: f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        
        nova = Devolucao(
            cliente=request.form['cliente'], nf_cliente=request.form['nf_cliente'],
            nf_interna=request.form['nf_interna'], valor=float(request.form['valor']),
            motivo=request.form['motivo'], pdf_nota=fname, vendedor_id=session['user_id']
        )
        db.session.add(nova); db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('nova_devolucao.html')

@app.route('/conferir_nota/<int:id>')
@roles_required('conferente', 'gerente')
def conferir_nota(id):
    d = Devolucao.query.get_or_404(id)
    d.status, d.conferido_por, d.data_conferencia = "aguardando_aprovacao", session['nome'], datetime.now()
    db.session.commit(); return redirect(url_for('dashboard'))

@app.route('/aprovar_envio/<int:id>')
@roles_required('gerente')
def aprovar_envio(id):
    d = Devolucao.query.get_or_404(id)
    d.status, d.aprovado_por, d.data_aprovacao = "em_transito", session['nome'], datetime.now()
    db.session.commit(); return redirect(url_for('dashboard'))

@app.route('/receber_mercadoria/<int:id>')
@roles_required('vendedor', 'conferente', 'gerente')
def receber_mercadoria(id):
    d = Devolucao.query.get_or_404(id)
    d.status = "entregue_fiscal"
    d.recebido_por = session['nome']
    d.data_recebimento = datetime.now()
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/baixar_boleto/<int:id>')
@roles_required('financeiro')
def baixar_boleto(id):
    d = Devolucao.query.get_or_404(id)
    d.status, d.baixado_por, d.data_baixa = "finalizado_pago", session['nome'], datetime.now()
    db.session.commit(); return redirect(url_for('dashboard'))

# --- USUÁRIOS ---
@app.route('/usuarios')
@roles_required('gerente')
def listar_usuarios():
    return render_template('usuario.html', usuarios=Usuario.query.all())

@app.route('/usuarios/novo', methods=['GET', 'POST'])
@roles_required('gerente')
def novo_usuario():
    if request.method == 'POST':
        u = Usuario(nome=request.form['nome'], email=request.form['email'], perfil=request.form['perfil'])
        u.set_senha(request.form['senha'])
        db.session.add(u); db.session.commit()
        return redirect(url_for('listar_usuarios'))
    return render_template('novo_usuario.html')

@app.route('/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@roles_required('gerente')
def editar_usuario(id):
    u = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        u.nome, u.email, u.perfil = request.form['nome'], request.form['email'], request.form['perfil']
        if request.form.get('senha'): u.set_senha(request.form['senha'])
        db.session.commit(); return redirect(url_for('listar_usuarios'))
    return render_template('editar_usuario.html', u=u)

# --- RELATÓRIO EM PDF (SOMENTE GERENTE) ---
@app.route('/relatorio', methods=['GET', 'POST'])
@login_required
@roles_required('gerente')
def relatorio():
    if request.method == 'POST':
        data_inicio = request.form.get('data_inicio')
        data_fim = request.form.get('data_fim')
        
        if data_inicio and data_fim:
            return redirect(url_for('gerar_relatorio_pdf', 
                                  data_inicio=data_inicio, 
                                  data_fim=data_fim))
    
    return render_template('relatorio.html')

@app.route('/relatorio/pdf')
@login_required
@roles_required('gerente')
def gerar_relatorio_pdf():
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    if not data_inicio_str or not data_fim_str:
        flash("Selecione as datas inicial e final.")
        return redirect(url_for('relatorio'))
    
    data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
    data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
    data_fim = data_fim.replace(hour=23, minute=59, second=59)
    
    devolucoes = Devolucao.query.filter(
        Devolucao.data_criacao >= data_inicio,
        Devolucao.data_criacao <= data_fim
    ).order_by(Devolucao.data_criacao.desc()).all()
    
    total_valor = sum(d.valor for d in devolucoes if d.valor)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=1
    )
    
    elements = []
    
    elements.append(Paragraph("MIC - Relatório de Devoluções", title_style))
    elements.append(Paragraph(f"<b>Período:</b> {data_inicio_str} até {data_fim_str}", styles['Normal']))
    elements.append(Paragraph(f"<b>Total de registros:</b> {len(devolucoes)}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    data = [['Data Entrada', 'Cliente', 'Vendedor', 'NF Cliente', 'NF Interna', 'Status', 'Valor']]
    
    for d in devolucoes:
        vendedor_nome = d.vendedor.nome if d.vendedor else '-'
        data.append([
            d.data_criacao.strftime('%d/%m/%Y'),
            d.cliente[:30] if d.cliente else '-',
            vendedor_nome[:20],
            d.nf_cliente or '-',
            d.nf_interna or '-',
            d.status.replace('_', ' ').title()[:15],
            f"R$ {d.valor:.2f}" if d.valor else "R$ 0.00"
        ])
    
    table = Table(data, colWidths=[3*cm, 5*cm, 3.5*cm, 3*cm, 3*cm, 3.5*cm, 2.5*cm])
    
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4f7f6')])
    ])
    table.setStyle(table_style)
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    total_style = ParagraphStyle(
        'Total',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#27ae60'),
        alignment=2
    )
    elements.append(Paragraph(f"<b>Valor Total no Período: R$ {total_valor:.2f}</b>", total_style))
    
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    agora = datetime.now().strftime('%d/%m/%Y às %H:%M')
    elements.append(Paragraph(f"Relatório gerado em {agora} | Sistema MIC", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    
    nome_arquivo = f"relatorio_devolucoes_{data_inicio_str}_a_{data_fim_str}.pdf"
    
    return send_file(buffer, 
                     download_name=nome_arquivo,
                     as_attachment=True,
                     mimetype='application/pdf')

# --- Bloco de Auto-Setup para o Render ---
def inicializar_usuarios():
    usuarios_fixos = [
        {"nome": "André", "email": "andre.oliveira@mic.ind.br", "perfil": "gerente"},
        {"nome": "Eloah", "email": "eloah@mic.ind.br", "perfil": "gerente"},
        {"nome": "Andrea Financeiro", "email": "andrea.santos@mic.ind.br", "perfil": "financeiro"},
        {"nome": "Marinete", "email": "marinete.goncalves@mic.ind.br", "perfil": "conferente"},
        {"nome": "Renata", "email": "renata.caetano@mic.ind.br", "perfil": "vendedor"},
        {"nome": "Luan", "email": "luan.costa@mic.ind.br", "perfil": "vendedor"},
        {"nome": "Talita", "email": "talita.stevanelli@mic.ind.br", "perfil": "vendedor"},
        {"nome": "Kevilly", "email": "kevvilly.dantas@mic.ind.br", "perfil": "vendedor"},
        {"nome": "Viviane", "email": "viviane.santos@mic.ind.br", "perfil": "vendedor"},
        {"nome": "Francielle", "email": "francielle.oliveira@mic.ind.br", "perfil": "vendedor"}
    ]

    with app.app_context():
        db.create_all()
        
        for dado in usuarios_fixos:
            if not Usuario.query.filter_by(email=dado["email"]).first():
                novo_u = Usuario(nome=dado["nome"], email=dado["email"], perfil=dado["perfil"])
                novo_u.set_senha("Mic@2026")
                db.session.add(novo_u)
        
        db.session.commit()
        print(">>> Sistema MIC: Usuários verificados/criados com sucesso!")

# --- Inicialização do Servidor ---
if __name__ == "__main__":
    inicializar_usuarios()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)