from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Configuração básica da aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clientes.db'  # Banco de dados SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do banco de dados
db = SQLAlchemy(app)

# Modelo do Cliente
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # ID único
    nome = db.Column(db.String(100), nullable=False)  # Nome do cliente
    email = db.Column(db.String(100), unique=True, nullable=True)  # Email não obrigatório
    telefone = db.Column(db.String(20), nullable=False)  # Telefone
    rota = db.Column(db.String(50), nullable=False)  # Rota associada
    descricao = db.Column(db.Text, nullable=True)  # Descrição adicional

# Página inicial
@app.route('/')
def index():
    return render_template('index.html')  # Página inicial (frontend)

# Página de cadastro de cliente
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Recebendo dados do formulário
        nome = request.form['nome']
        email = request.form.get('email')
        email = email if email else None  # Converte string vazia em None
        telefone = request.form['telefone']
        rota = request.form['rota']
        descricao = request.form.get('descricao')  # Descrição opcional

        # Adicionando cliente ao banco de dados
        novo_cliente = Cliente(nome=nome, email=email, telefone=telefone, rota=rota, descricao=descricao)
        try:
            db.session.add(novo_cliente)
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Reverte a transação em caso de erro
            return f"Erro ao salvar no banco de dados: {e}"

        return redirect(url_for('clientes'))  # Redireciona para a página de clientes

    return render_template('cadastro.html', campos={"nome": "Nome", "email": "Email", "telefone": "Telefone", "rota": "Rota", "descricao": "Descrição"})

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
    clientes = query.all()  # Executa a consulta

    return render_template('clientes.html', clientes=clientes)


# Inicializa o banco de dados na primeira execução
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)
