from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# Configuração básica da aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clientes.db'  # Banco de dados SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'b9c2d0e691341d6c23c30740f5c232c0'

# Inicialização do banco de dados
db = SQLAlchemy(app)

# Modelo do Cliente
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID único
    nome = db.Column(db.String(100), nullable=False)  # Nome do cliente
    email = db.Column(db.String(100),  nullable=True)  # Email não obrigatório
    telefone = db.Column(db.String(20), nullable=False)  # Telefone
    rota = db.Column(db.String(50), nullable=False)  # Rota associada
    descricao = db.Column(db.Text, nullable=True)  # Descrição adicional

# Página inicial
@app.route('/')
def index():
    return render_template('index.html')  # Página inicial (frontend)

# Página de cadastro de cliente (Criação e Edição)
@app.route('/cadastro', methods=['GET', 'POST'])
@app.route('/cadastro/<int:id>', methods=['GET', 'POST'])
def cadastro(id=None):
    cliente = None
    if id:  # Se um ID for passado, estamos editando
        cliente = Cliente.query.get_or_404(id)

    if request.method == 'POST':
        # Recebendo dados do formulário
        nome = request.form['nome']
        email = request.form.get('email')
        email = email if email else ''  # Converte string vazia em None
        telefone = request.form['telefone']
        rota = request.form['rota']
        descricao = request.form.get('descricao')  # Descrição opcional

        if cliente:  # Atualização de cliente existente
            cliente.nome = nome
            cliente.email = email
            cliente.telefone = telefone
            cliente.rota = rota
            cliente.descricao = descricao
            try:
                db.session.commit()
                flash('Cliente atualizado com sucesso!', 'success')  # Mensagem de sucesso
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao atualizar no banco de dados: {e}", 'danger')  # Mensagem de erro
        else:  # Criação de novo cliente
            novo_cliente = Cliente(nome=nome, email=email, telefone=telefone, rota=rota, descricao=descricao)
            try:
                db.session.add(novo_cliente)
                db.session.commit()
                flash('Cadastro realizado com sucesso!', 'success')  # Mensagem de sucesso
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao salvar no banco de dados: {e}", 'danger')  # Mensagem de erro

        return redirect(url_for('cadastro'))  # Redireciona para a própria página

    return render_template(
        'cadastro.html',
        cliente=cliente,
        campos={"nome": "Nome", "email": "Email", "telefone": "Telefone", "rota": "Rota", "descricao": "Descrição"}
    )

# Página para listar clientes com filtros
@app.route('/clientes', methods=['GET'])
def clientes():
    # Recebe o parâmetro de pesquisa unificada
    search = request.args.get('search', '').strip().lower()

    # Monta a consulta com filtros em múltiplos campos
    query = Cliente.query
    if search:
        query = query.filter(
            db.or_(
                Cliente.nome.ilike(f"%{search}%"),  # Busca por nome
                Cliente.telefone.ilike(f"%{search}%"),  # Busca por telefone
                Cliente.rota.ilike(f"%{search}%")  # Busca por rota
            )
        )
    clientes = query.order_by(Cliente.id.desc()).all()
    
    return render_template('clientes.html', clientes=clientes)

# Filtro Jinja para formatar telefone
@app.template_filter()
def formatar_telefone(telefone):
    """Aplica uma máscara ao telefone no formato (XX) XXXX-XXXX ou (XX) XXXXX-XXXX"""
    telefone = ''.join(filter(str.isdigit, telefone))  # Remove caracteres não numéricos

    if len(telefone) == 10:  # Formato com 10 dígitos: (XX) XXXX-XXXX
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    elif len(telefone) == 11:  # Formato com 11 dígitos: (XX) XXXXX-XXXX
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    else:
        return telefone  # Retorna sem máscara se o tamanho for inválido


# Filtro Jinja para validar telefone
@app.template_filter()
def validar_telefone(telefone):
    """Valida e retorna o número de telefone apenas com números, incluindo o DDD."""
    telefone = ''.join(filter(str.isdigit, telefone))  # Remove caracteres não numéricos
    if len(telefone) == 10:  # Telefones fixos com DDD
        return f"{telefone[:2]}{telefone[2:]}"
    elif len(telefone) == 11:  # Telefones móveis com DDD
        return f"{telefone[:2]}{telefone[2:]}"
    return None  # Retorna None para números inválidos



# Rota para excluir cliente
@app.route('/excluir/<int:id>', methods=['POST'])
def excluir_cliente(id):
    cliente = Cliente.query.get_or_404(id)  # Busca o cliente pelo ID
    db.session.delete(cliente)  # Remove o cliente do banco de dados
    db.session.commit()
    return redirect(url_for('clientes'))  # Redireciona para a lista de clientes

# Inicializa o banco de dados na primeira execução
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)
