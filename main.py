from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.clock import Clock
from datetime import datetime, timedelta
import sqlite3

# Configuração do Banco de Dados
def setup_database():
    conn = sqlite3.connect('pdv_guarda_volumes.db')
    cursor = conn.cursor()

    # Tabela para operadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')

    # Tabela para clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            rg TEXT NOT NULL,
            telefone TEXT,
            quantidade_volumes INTEGER NOT NULL,
            valor REAL NOT NULL,
            data_entrada TEXT NOT NULL,
            status TEXT DEFAULT 'ativo',
            operador TEXT
        )
    ''')

    # Tabela para logs de operadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs_operadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operador TEXT NOT NULL,
            horario_entrada TEXT NOT NULL,
            total_vendas REAL NOT NULL,
            horario_saida TEXT NOT NULL
        )
    ''')

    # Inserir o administrador padrão (se ainda não existir)
    cursor.execute("SELECT * FROM operadores WHERE nome='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO operadores (nome, senha, email) VALUES (?, ?, ?)", 
                       ("admin", "$148015%", "flpiratesofcaribbean@gmail.com"))

    conn.commit()
    conn.close()

# Função para registrar log de operador
def registrar_log_operador(operador, horario_entrada, total_vendas, horario_saida):
    try:
        conn = sqlite3.connect('pdv_guarda_volumes.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs_operadores (operador, horario_entrada, total_vendas, horario_saida)
            VALUES (?, ?, ?, ?)
        ''', (operador, horario_entrada, total_vendas, horario_saida))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao registrar log de operador: {str(e)}")

# Tela de Login
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=10)

        # Título
        self.title_label = Label(text="LOGIN PDV GUARDA VOLUMES", font_size=24, size_hint_y=None, height=50)
        self.layout.add_widget(self.title_label)

        # Campo Operador
        self.operador_input = TextInput(hint_text="Operador", multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.operador_input)

        # Campo Senha
        self.senha_input = TextInput(hint_text="Senha", password=True, multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.senha_input)

        # Botão de Login
        self.login_button = Button(text="Login", size_hint_y=None, height=50)
        self.login_button.bind(on_press=self.login)
        self.layout.add_widget(self.login_button)

        # Botão para Admin
        self.admin_button = Button(text="Acesso Admin", size_hint_y=None, height=50)
        self.admin_button.bind(on_press=self.go_to_admin)
        self.layout.add_widget(self.admin_button)

        self.add_widget(self.layout)

    def login(self, instance):
        operador = self.operador_input.text.strip()
        senha = self.senha_input.text.strip()

        if not operador or not senha:
            self.show_popup("Erro", "Preencha todos os campos!")
            return

        try:
            conn = sqlite3.connect('pdv_guarda_volumes.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM operadores WHERE nome=? AND senha=?", (operador, senha))
            result = cursor.fetchone()
            conn.close()

            if result:
                pdv_screen = self.manager.get_screen("pdv_screen")
                pdv_screen.operador = operador
                pdv_screen.horario_login = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # Salvar horário de login
                self.manager.current = "pdv_screen"
            else:
                self.show_popup("Erro", "Operador ou senha incorretos!")
        except Exception as e:
            self.show_popup("Erro", f"Erro inesperado: {str(e)}")

    def go_to_admin(self, instance):
        self.manager.current = "admin_login_screen"

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message, font_size=18)
        popup_button = Button(text="OK", size_hint=(1, 0.5))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        popup_button.bind(on_press=popup.dismiss)
        popup.open()

# Tela de Login do Administrador
class AdminLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=10)

        # Título
        self.title_label = Label(text="LOGIN DE ADMINISTRADOR", font_size=24, size_hint_y=None, height=50)
        self.layout.add_widget(self.title_label)

        # Campo Senha
        self.senha_input = TextInput(hint_text="Senha do Admin", password=True, multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.senha_input)

        # Botão de Login
        self.login_button = Button(text="Login como Admin", size_hint_y=None, height=50)
        self.login_button.bind(on_press=self.admin_login)
        self.layout.add_widget(self.login_button)

        self.add_widget(self.layout)

    def admin_login(self, instance):
        senha_admin = self.senha_input.text.strip()
        if senha_admin == "$148015%":  # Senha fixa para o admin
            self.manager.current = "admin_screen"
        else:
            self.show_popup("Erro", "Senha de administrador incorreta!")

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message, font_size=18)
        popup_button = Button(text="OK", size_hint=(1, 0.5))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        popup_button.bind(on_press=popup.dismiss)
        popup.open()

# Tela de Administração
class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=10)

        # Título
        self.title_label = Label(text="ÁREA DE ADMINISTRAÇÃO", font_size=24, size_hint_y=None, height=50)
        self.layout.add_widget(self.title_label)

        # Campo Novo Operador
        self.novo_operador_input = TextInput(hint_text="Novo Operador", multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.novo_operador_input)

        # Campo Nova Senha
        self.nova_senha_input = TextInput(hint_text="Nova Senha", password=True, multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.nova_senha_input)

        # Botão Cadastrar
        self.cadastrar_button = Button(text="Cadastrar Novo Operador", size_hint_y=None, height=50)
        self.cadastrar_button.bind(on_press=self.cadastrar_operador)
        self.layout.add_widget(self.cadastrar_button)

        # Lista de Operadores
        self.operadores_label = Label(text="Operadores Cadastrados:", font_size=16, size_hint_y=None, height=50)
        self.layout.add_widget(self.operadores_label)
        self.lista_operadores = Label(text="", font_size=14, size_hint_y=None, height=100)
        self.layout.add_widget(self.lista_operadores)

        # Botão Voltar
        self.voltar_button = Button(text="Voltar ao Login", size_hint_y=None, height=50)
        self.voltar_button.bind(on_press=self.voltar_login)
        self.layout.add_widget(self.voltar_button)

        self.add_widget(self.layout)

    def cadastrar_operador(self, instance):
        operador = self.novo_operador_input.text.strip()
        senha = self.nova_senha_input.text.strip()

        if not operador or not senha:
            self.show_popup("Erro", "Preencha todos os campos!")
            return

        try:
            conn = sqlite3.connect('pdv_guarda_volumes.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO operadores (nome, senha, email) VALUES (?, ?, ?)", 
                           (operador, senha, "email@example.com"))  # Adicione um e-mail padrão
            conn.commit()
            conn.close()
            self.show_popup("Sucesso", "Operador cadastrado com sucesso!")
            self.novo_operador_input.text = ""
            self.nova_senha_input.text = ""
            self.atualizar_lista_operadores()
        except sqlite3.IntegrityError:
            self.show_popup("Erro", "Operador já existe!")

    def atualizar_lista_operadores(self):
        try:
            conn = sqlite3.connect('pdv_guarda_volumes.db')
            cursor = conn.cursor()
            cursor.execute("SELECT nome FROM operadores")
            operadores = cursor.fetchall()
            conn.close()
            lista = "\n".join([op[0] for op in operadores])
            self.lista_operadores.text = lista
        except Exception as e:
            self.show_popup("Erro", f"Erro ao listar operadores: {str(e)}")

    def voltar_login(self, instance):
        self.manager.current = "login_screen"

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message, font_size=18)
        popup_button = Button(text="OK", size_hint=(1, 0.5))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        popup_button.bind(on_press=popup.dismiss)
        popup.open()

# Tela do PDV
class PDVScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.operador = ""
        self.horario_login = ""
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Barra Superior
        self.header_layout = BoxLayout(size_hint_y=None, height=50)
        self.data_hora_label = Label(text="", color=(1, 0.5, 0, 1))  # Laranja escuro
        self.nome_operador_label = Label(text=f"Operador: {self.operador}", color=(1, 1, 1, 1))  # Branco gelo
        self.titulo_label = Label(text="GUARDA VOLUMES AMD SERVICES", color=(0, 0, 0.5, 1))  # Azul aeronáutico
        self.header_layout.add_widget(self.data_hora_label)
        self.header_layout.add_widget(self.nome_operador_label)
        self.header_layout.add_widget(self.titulo_label)
        self.layout.add_widget(self.header_layout)

        # Subtítulo
        self.subtitulo_label = Label(text="CADASTRO DE CLIENTE", font_size=18, size_hint_y=None, height=30)
        self.layout.add_widget(self.subtitulo_label)

        # Formulário
        self.form_layout = BoxLayout(orientation='vertical', spacing=10)
        self.nome_cliente_input = TextInput(hint_text="Nome do Cliente", multiline=False, size_hint_y=None, height=40)
        self.rg_input = TextInput(hint_text="RG", multiline=False, size_hint_y=None, height=40)
        self.telefone_input = TextInput(hint_text="Telefone", multiline=False, size_hint_y=None, height=40)
        self.quantidade_volumes_input = TextInput(hint_text="Quantidade de Volumes", multiline=False, size_hint_y=None, height=40)
        self.valor_label = Label(text="Valor: R$0.00", font_size=16, size_hint_y=None, height=30)
        self.form_layout.add_widget(self.nome_cliente_input)
        self.form_layout.add_widget(self.rg_input)
        self.form_layout.add_widget(self.telefone_input)
        self.form_layout.add_widget(self.quantidade_volumes_input)
        self.form_layout.add_widget(self.valor_label)
        self.layout.add_widget(self.form_layout)

        # Botões
        self.botoes_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        self.calcular_button = Button(text="Calcular Valor")
        self.cadastrar_button = Button(text="Cadastrar Cliente")
        self.limpar_button = Button(text="Limpar Tela")
        self.imprimir_button = Button(text="Imprimir Ticket")
        self.fechamento_caixa_button = Button(text="Fechamento")
        self.logout_button = Button(text="Logout")
        self.calcular_button.bind(on_press=self.calcular_valor)
        self.cadastrar_button.bind(on_press=self.cadastrar_cliente)
        self.limpar_button.bind(on_press=self.limpar_formulario)
        self.imprimir_button.bind(on_press=self.imprimir_ticket)
        self.fechamento_caixa_button.bind(on_press=self.fechamento_caixa)
        self.logout_button.bind(on_press=self.logout)
        self.botoes_layout.add_widget(self.calcular_button)
        self.botoes_layout.add_widget(self.cadastrar_button)
        self.botoes_layout.add_widget(self.limpar_button)
        self.botoes_layout.add_widget(self.imprimir_button)
        self.verificar_prazo_button = Button(text="Verificar Prazo de Cliente", size_hint_y=None, height=50)
        self.verificar_prazo_button.bind(on_press=self.go_to_verificar_prazo)
        self.botoes_layout.add_widget(self.verificar_prazo_button)
        self.botoes_layout.add_widget(self.fechamento_caixa_button)
        self.botoes_layout.add_widget(self.logout_button)
        self.layout.add_widget(self.botoes_layout)

        self.add_widget(self.layout)

        # Atualização do Relógio
        Clock.schedule_interval(self.atualizar_relogio, 1)

    def atualizar_relogio(self, dt):
        self.data_hora_label.text = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.nome_operador_label.text = f"Operador: {self.operador}"

    def calcular_valor(self, instance):
        try:
            quantidade = int(self.quantidade_volumes_input.text.strip())
            valor = quantidade * 9.00
            self.valor_label.text = f"Valor: R${valor:.2f}"
        except ValueError:
            self.show_popup("Erro", "Insira uma quantidade válida!")

    def cadastrar_cliente(self, instance):
        nome = self.nome_cliente_input.text.strip()
        rg = self.rg_input.text.strip()
        telefone = self.telefone_input.text.strip()
        quantidade = self.quantidade_volumes_input.text.strip()
        valor = self.valor_label.text.split(" ")[1]

        if not nome or not rg or not quantidade:
            self.show_popup("Erro", "Preencha todos os campos obrigatórios!")
            return

        try:
            quantidade = int(quantidade)
            valor = float(valor.replace("R$", ""))
        except ValueError:
            self.show_popup("Erro", "Quantidade ou valor inválidos!")
            return

        try:
            conn = sqlite3.connect('pdv_guarda_volumes.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clientes (nome, rg, telefone, quantidade_volumes, valor, data_entrada, operador)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nome, rg, telefone, quantidade, valor, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), self.operador))
            conn.commit()
            conn.close()
            self.show_popup("Sucesso", "Cliente cadastrado com sucesso!")
            self.limpar_formulario(None)
        except Exception as e:
            self.show_popup("Erro", str(e))

    def limpar_formulario(self, instance):
        self.nome_cliente_input.text = ""
        self.rg_input.text = ""
        self.telefone_input.text = ""
        self.quantidade_volumes_input.text = ""
        self.valor_label.text = "Valor: R$0.00"

    def imprimir_ticket(self, instance):
        conn = sqlite3.connect('pdv_guarda_volumes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM clientes WHERE operador=?", (self.operador,))
        ultimo_id = cursor.fetchone()[0]
        conn.close()

        if not ultimo_id:
            self.show_popup("Erro", "Nenhum cliente encontrado para imprimir o ticket!")
            return

        ticket = f"""
        TICKET DE SERVIÇO
        -----------------
        ID do Cliente: {ultimo_id}
        Data e Hora: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        Nome: {self.nome_cliente_input.text.strip()}
        RG: {self.rg_input.text.strip()}
        Telefone: {self.telefone_input.text.strip()}
        Quantidade de Volumes: {self.quantidade_volumes_input.text.strip()}
        Valor Pago: {self.valor_label.text}
        -----------------
        Obrigado por utilizar nossos serviços!
        """
        self.show_popup("Ticket Impresso", ticket)

    def fechamento_caixa(self, instance):
        self.manager.current = "fechamento_screen"

    def logout(self, instance):
        try:
            conn = sqlite3.connect('pdv_guarda_volumes.db')
            cursor = conn.cursor()

            # Calcular total de vendas do operador
            cursor.execute("SELECT SUM(valor) FROM clientes WHERE operador=? AND data_entrada LIKE ?", 
                           (self.operador, f"{datetime.now().strftime('%d/%m/%Y')}%"))
            total_vendas = cursor.fetchone()[0] or 0.0

            # Registrar log de operador
            registrar_log_operador(
                operador=self.operador,
                horario_entrada=self.horario_login,
                total_vendas=total_vendas,
                horario_saida=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            )

            conn.close()

            # Limpar dados do operador
            self.operador = ""
            self.horario_login = ""
            self.manager.current = "login_screen"
        except Exception as e:
            self.show_popup("Erro", f"Erro ao realizar logout: {str(e)}")

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message, font_size=18)
        popup_button = Button(text="OK", size_hint=(1, 0.5))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        popup_button.bind(on_press=popup.dismiss)
        popup.open()

# Tela de Fechamento de Caixa
class FechamentoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=10)

        # Título
        self.title_label = Label(text="FECHAMENTO DE CAIXA", font_size=24, size_hint_y=None, height=50)
        self.layout.add_widget(self.title_label)

        # Resumo
        self.resumo_label = Label(text="", font_size=18, size_hint_y=None, height=200)
        self.layout.add_widget(self.resumo_label)

        # Botão Voltar
        self.voltar_button = Button(text="Voltar ao PDV", size_hint_y=None, height=50)
        self.voltar_button.bind(on_press=self.voltar_pdv)
        self.layout.add_widget(self.voltar_button)

        self.add_widget(self.layout)

    def on_pre_enter(self):
        operador = self.manager.get_screen("pdv_screen").operador
        self.carregar_resumo(operador)

    def carregar_resumo(self, operador):
        try:
            conn = sqlite3.connect('pdv_guarda_volumes.db')
            cursor = conn.cursor()

            # Total de vendas do operador no dia
            cursor.execute("SELECT SUM(valor) FROM clientes WHERE operador=? AND data_entrada LIKE ?", 
                           (operador, f"{datetime.now().strftime('%d/%m/%Y')}%"))
            total = cursor.fetchone()[0] or 0.0

            # Total de clientes atendidos pelo operador no dia
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE operador=? AND data_entrada LIKE ?", 
                           (operador, f"{datetime.now().strftime('%d/%m/%Y')}%"))
            quantidade_clientes = cursor.fetchone()[0]

            conn.close()

            resumo = f"Operador: {operador}\n"
            resumo += f"Total de Clientes: {quantidade_clientes}\n"
            resumo += f"Valor Total: R${total:.2f}"
            self.resumo_label.text = resumo
        except Exception as e:
            self.show_popup("Erro", f"Erro ao carregar resumo: {str(e)}")

    def voltar_pdv(self, instance):
        self.manager.current = "pdv_screen"

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message, font_size=18)
        popup_button = Button(text="OK", size_hint=(1, 0.5))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        popup_button.bind(on_press=popup.dismiss)
        popup.open()

# Função para calcular o valor total com base no tempo excedido
def calcular_valor_excedente(data_entrada, valor_inicial):
    try:
        # Converter a data de entrada para um objeto datetime
        data_entrada_obj = datetime.strptime(data_entrada, "%d/%m/%Y %H:%M:%S")
        # Obter a data e hora atual
        agora = datetime.now()
        # Calcular a diferença entre a data atual e a data de entrada
        diferenca = agora - data_entrada_obj

        # Verificar se o cliente está dentro do prazo inicial de 12 horas
        if diferenca <= timedelta(hours=12):
            return valor_inicial  # Dentro do prazo, retorna o valor inicial

        # Calcular o número de intervalos de 12 horas excedidos
        horas_excedidas = diferenca.total_seconds() / 3600  # Total de horas excedidas
        intervalos_excedidos = int(horas_excedidas // 12) + (1 if horas_excedidas % 12 != 0 else 0)

        # Calcular o valor total
        valor_total = valor_inicial * (intervalos_excedidos + 1)
        return valor_total
    except Exception as e:
        print(f"Erro ao calcular valor excedente: {str(e)}")
        return None

# Tela de Verificação de Prazo
class VerificarPrazoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=10)
        
        # Título
        self.title_label = Label(text="VERIFICAR PRAZO DE CLIENTE", font_size=24, size_hint_y=None, height=50)
        self.layout.add_widget(self.title_label)
        
        # Campo ID do Cliente
        self.id_cliente_input = TextInput(hint_text="ID do Cliente", multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.id_cliente_input)
        
        # Botão de Verificação
        self.verificar_button = Button(text="Verificar Prazo", size_hint_y=None, height=50)
        self.verificar_button.bind(on_press=self.verificar_prazo)
        self.layout.add_widget(self.verificar_button)
        
        # Resultado da Verificação
        self.resultado_label = Label(text="", font_size=18, size_hint_y=None, height=100)
        self.layout.add_widget(self.resultado_label)
        
        # Botão Voltar
        self.voltar_button = Button(text="Voltar ao PDV", size_hint_y=None, height=50)
        self.voltar_button.bind(on_press=self.voltar_pdv)
        self.layout.add_widget(self.voltar_button)
        
        self.add_widget(self.layout)

    def verificar_prazo(self, instance):
        id_cliente = self.id_cliente_input.text.strip()
        if not id_cliente.isdigit():
            self.show_popup("Erro", "Insira um ID de cliente válido!")
            return
        
        try:
            conn = sqlite3.connect('pdv_guarda_volumes.db')
            cursor = conn.cursor()
            cursor.execute("SELECT data_entrada, valor FROM clientes WHERE id=?", (id_cliente,))
            resultado = cursor.fetchone()
            conn.close()
            
            if not resultado:
                self.show_popup("Erro", "Cliente não encontrado!")
                return
            
            data_entrada, valor_inicial = resultado
            valor_total = calcular_valor_excedente(data_entrada, valor_inicial)
            
            if valor_total is None:
                self.resultado_label.text = "Erro ao calcular o valor excedente."
            elif valor_total == valor_inicial:
                self.resultado_label.text = f"Cliente dentro do prazo. Valor a pagar: R${valor_total:.2f}"
            else:
                self.resultado_label.text = f"Cliente excedeu o prazo. Valor a pagar: R${valor_total:.2f}"
        except Exception as e:
            self.show_popup("Erro", f"Erro inesperado: {str(e)}")

    def voltar_pdv(self, instance):
        self.manager.current = "pdv_screen"

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message, font_size=18)
        popup_button = Button(text="OK", size_hint=(1, 0.5))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)
        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        popup_button.bind(on_press=popup.dismiss)
        popup.open()

# Gerenciador de Telas
class PDVApp(App):
    def build(self):
        setup_database()
        sm = ScreenManager()
        # Adicionar telas ao gerenciador de telas
        sm.add_widget(LoginScreen(name="login_screen"))
        sm.add_widget(AdminLoginScreen(name="admin_login_screen"))
        sm.add_widget(AdminScreen(name="admin_screen"))
        sm.add_widget(PDVScreen(name="pdv_screen"))
        sm.add_widget(FechamentoScreen(name="fechamento_screen"))
        sm.add_widget(VerificarPrazoScreen(name="verificar_prazo_screen"))
        return sm

if __name__ == "__main__":
    PDVApp().run()