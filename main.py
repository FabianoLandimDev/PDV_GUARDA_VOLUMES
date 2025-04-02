from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.clock import Clock
from datetime import datetime
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#
#
#
# Nome_do _programa: PDV_GUARDA_VOLUMES
#
# site:https://github.com/FabianoLandimDev/PDV_GUARDA_VOLUMES.git
#
# Autor: Fabiano Landim <landimfabiano01@gmail.com>
#
# Manutenção: Fabiano Landim <landimfabiano01@gmail.com>
#
# ESCOPO:
# O Programa consiste em um Ponto de Venda (PDV), para utilização do colaboradores de uma Empresa específica, podendo ser adaptado para qualquer Empresa, modificando as linhas do código, estou utilizando a bilbioteca Kivy, para uma melhor experiência gráfica.
#
# Histórico:
#
# v1.0.0_2025-04-02, Fabiano Landim:
# - Versão Inicial do Programa.
#
#
##############################################################################################################################################################################
#
#
# Configuração do Banco de Dados...

def setup_database():
    conn = sqlite3.connect('pdv_guarda_volumes.db')
    cursor = conn.cursor()

    # Tabela para operadores...

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')

    # Tabela para clientes...

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

    # Adicionar a coluna "operador" se ela não existir...

    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN operador TEXT")
    except sqlite3.OperationalError:
        pass  # Coluna já existe

    # Inserir o administrador padrão (se ainda não existir)...

    cursor.execute("SELECT * FROM operadores WHERE nome='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO operadores (nome, senha, email) VALUES (?, ?, ?)", 
                       ("admin", "$148015%", "flpiratesofcaribbean@gmail.com"))

    conn.commit()
    conn.close()

# Função para enviar e-mail via Gmail...

def enviar_email(destinatario, corpo_email):
    try:
        # Configurações do remetente...

        remetente = "landimfabiano01@gmail.com"
        senha_app = "qnvczfebxisvmtjo"

        # Validar parâmetros...

        if not destinatario or not corpo_email:
            return "Erro: Destinatário ou corpo do e-mail inválido."

        # Criar a mensagem...

        msg = MIMEMultipart()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = "Relatório de Fechamento de Caixa"
        msg.attach(MIMEText(corpo_email, 'plain'))

        # Conectar ao servidor SMTP do Gmail...

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Habilitar TLS
        server.login(remetente, senha_app)

        # Enviar o e-mail...

        server.sendmail(remetente, destinatario, msg.as_string())
        server.quit()

        return True
    except smtplib.SMTPAuthenticationError:
        return "Erro: Falha na autenticação. Verifique seu e-mail e senha de app."
    except smtplib.SMTPConnectError:
        return "Erro: Não foi possível conectar ao servidor SMTP."
    except Exception as e:
        return f"Erro inesperado: {str(e)}"

# Tela de Login do Administrador
class AdminLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=50, spacing=10)

        # Título...

        self.title_label = Label(text="LOGIN DE ADMINISTRADOR", font_size=24, size_hint_y=None, height=50)
        self.layout.add_widget(self.title_label)

        # Campo Senha...

        self.senha_input = TextInput(hint_text="Senha do Admin", password=True, multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.senha_input)

        # Botão de Login...

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

        # Título...

        self.title_label = Label(text="ÁREA DE ADMINISTRAÇÃO", font_size=24, size_hint_y=None, height=50)
        self.layout.add_widget(self.title_label)

        # Campo Novo Operador...

        self.novo_operador_input = TextInput(hint_text="Novo Operador", multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.novo_operador_input)

        # Campo Nova Senha...

        self.nova_senha_input = TextInput(hint_text="Nova Senha", password=True, multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.nova_senha_input)

        # Campo E-mail...

        self.email_input = TextInput(hint_text="E-mail", multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.email_input)

        # Botão Cadastrar...

        self.cadastrar_button = Button(text="Cadastrar Novo Operador", size_hint_y=None, height=50)
        self.cadastrar_button.bind(on_press=self.cadastrar_operador)
        self.layout.add_widget(self.cadastrar_button)

        # Lista de Operadores...

        self.operadores_label = Label(text="Operadores Cadastrados:", font_size=16, size_hint_y=None, height=50)
        self.layout.add_widget(self.operadores_label)

        self.lista_operadores = Label(text="", font_size=14, size_hint_y=None, height=100)
        self.layout.add_widget(self.lista_operadores)

        # Campo para Excluir Operador...

        self.excluir_operador_input = TextInput(hint_text="Nome do Operador para Excluir", multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.excluir_operador_input)

        # Botão Excluir...

        self.excluir_button = Button(text="Excluir Operador", size_hint_y=None, height=50)
        self.excluir_button.bind(on_press=self.excluir_operador)
        self.layout.add_widget(self.excluir_button)

        # Botão Voltar...

        self.voltar_button = Button(text="Voltar ao Login", size_hint_y=None, height=50)
        self.voltar_button.bind(on_press=self.voltar_login)
        self.layout.add_widget(self.voltar_button)

        self.add_widget(self.layout)

    def cadastrar_operador(self, instance):
        operador = self.novo_operador_input.text.strip()
        senha = self.nova_senha_input.text.strip()
        email = self.email_input.text.strip()

        if not operador or not senha or not email:
            self.show_popup("Erro", "Preencha todos os campos!")
            return

        try:
            conn = sqlite3.connect('pdv_guarda_volumes.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO operadores (nome, senha, email) VALUES (?, ?, ?)", (operador, senha, email))
            conn.commit()
            conn.close()
            self.show_popup("Sucesso", "Operador cadastrado com sucesso!")
            self.novo_operador_input.text = ""
            self.nova_senha_input.text = ""
            self.email_input.text = ""
            self.atualizar_lista_operadores()
        except sqlite3.IntegrityError:
            self.show_popup("Erro", "Operador já existe!")

    def excluir_operador(self, instance):
        operador = self.excluir_operador_input.text.strip()

        if not operador:
            self.show_popup("Erro", "Informe o nome do operador a ser excluído!")
            return

        try:
            conn = sqlite3.connect('pdv_guarda_volumes.db')
            cursor = conn.cursor()
            #
            # Verificar se o operador tem registros associados
            #
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE operador=?", (operador,))
            count = cursor.fetchone()[0]
            if count > 0:
                self.show_popup("Erro", f"Operador '{operador}' possui registros de clientes e não pode ser excluído!")
                conn.close()
                return
            #
            # Excluir o operador
            #
            cursor.execute("DELETE FROM operadores WHERE nome=?", (operador,))
            conn.commit()
            conn.close()

            if cursor.rowcount > 0:
                self.show_popup("Sucesso", f"Operador '{operador}' excluído com sucesso!")
                self.excluir_operador_input.text = ""
                self.atualizar_lista_operadores()
            else:
                self.show_popup("Erro", "Operador não encontrado!")
        except Exception as e:
            self.show_popup("Erro", f"Erro inesperado: {str(e)}")

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

# Tela do PDV
class PDVScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.operador = ""
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Barra Superior
        self.header_layout = BoxLayout(size_hint_y=None, height=50)
        self.data_hora_label = Label(text="", color=(1, 0.5, 0, 1))
        self.nome_operador_label = Label(text=f"Operador: {self.operador}", color=(1, 1, 1, 1))
        self.titulo_label = Label(text="GUARDA VOLUMES AMD SERVICES", color=(0, 0.5, 0.5, 0.9))
        self.header_layout.add_widget(self.data_hora_label)
        self.header_layout.add_widget(self.nome_operador_label)
        self.header_layout.add_widget(self.titulo_label)
        self.layout.add_widget(self.header_layout)

        # Subtítulo
        self.subtitulo_label = Label(text="CADASTRO DE CLIENTE", font_size=36, size_hint_y=None, height=30)
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
        self.limpar_button = Button(text="Limpar Formulário")
        self.imprimir_button = Button(text="Imprimir Ticket")
        self.fechamento_caixa_button = Button(text="Fechamento de Caixa")
        self.calcular_button.bind(on_press=self.calcular_valor)
        self.cadastrar_button.bind(on_press=self.cadastrar_cliente)
        self.limpar_button.bind(on_press=self.limpar_formulario)
        self.imprimir_button.bind(on_press=self.imprimir_ticket)
        self.fechamento_caixa_button.bind(on_press=self.fechamento_caixa)
        self.botoes_layout.add_widget(self.calcular_button)
        self.botoes_layout.add_widget(self.cadastrar_button)
        self.botoes_layout.add_widget(self.limpar_button)
        self.botoes_layout.add_widget(self.imprimir_button)
        self.botoes_layout.add_widget(self.fechamento_caixa_button)
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
        self.show_popup("Impressão de Ticket", "Ticket impresso com sucesso!")

    def fechamento_caixa(self, instance):
        self.manager.current = "fechamento_screen"

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

        # Botão Enviar Relatório
        self.enviar_button = Button(text="Enviar Relatório por E-mail", size_hint_y=None, height=50)
        self.enviar_button.bind(on_press=self.enviar_relatorio)
        self.layout.add_widget(self.enviar_button)

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
            cursor.execute("SELECT SUM(valor) FROM clientes WHERE operador=?", (operador,))
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE operador=?", (operador,))
            quantidade_clientes = cursor.fetchone()[0]
            conn.close()

            resumo = f"Operador: {operador}\n"
            resumo += f"Total de Clientes: {quantidade_clientes}\n"
            resumo += f"Valor Total: R${total:.2f}" if total else "Valor Total: R$0.00"
            self.resumo_label.text = resumo
        except Exception as e:
            self.show_popup("Erro", f"Erro ao carregar resumo: {str(e)}")

    def enviar_relatorio(self, instance):
        operador = self.manager.get_screen("pdv_screen").operador

        if not operador:
            self.show_popup("Erro", "Operador não encontrado!")
            return

        try:
            conn = sqlite3.connect('pdv_guarda_volumes.db')
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM operadores WHERE nome=?", (operador,))
            resultado = cursor.fetchone()
            conn.close()

            if not resultado or not resultado[0]:
                self.show_popup("Erro", "E-mail do operador não encontrado!")
                return

            email_destino = resultado[0]
            corpo_email = self.resumo_label.text
            resultado_envio = enviar_email(email_destino, corpo_email)

            if resultado_envio is True:
                self.show_popup("Sucesso", "Relatório enviado com sucesso!")
            else:
                self.show_popup("Erro", resultado_envio)
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
        sm.add_widget(LoginScreen(name="login_screen"))
        sm.add_widget(AdminLoginScreen(name="admin_login_screen"))
        sm.add_widget(AdminScreen(name="admin_screen"))
        sm.add_widget(PDVScreen(name="pdv_screen"))
        sm.add_widget(FechamentoScreen(name="fechamento_screen"))

        # Inicializa a lista de operadores na tela de admin
        admin_screen = sm.get_screen("admin_screen")
        admin_screen.atualizar_lista_operadores()

        return sm

if __name__ == "__main__":
    PDVApp().run()