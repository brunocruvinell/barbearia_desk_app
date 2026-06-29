import tkinter as tk
from tkinter import messagebox, ttk
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
import sqlite3

# 1. BANCO DE DADOS (SQLite) 


class BancoDeDados:
    def __init__(self, nome_banco="barbearia.db"):
        self.conexao = sqlite3.connect(nome_banco)
        self.criar_tabelas()
        self.popular_barbeiros_iniciais()

    def criar_tabelas(self):
        cursor = self.conexao.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT,
                pontos_fidelidade INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS barbeiros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agendamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_nome TEXT,
                barbeiro_nome TEXT,
                servico TEXT,
                valor_final REAL,
                data_hora TEXT,
                status TEXT
            )
        ''')
        self.conexao.commit()

    def popular_barbeiros_iniciais(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM barbeiros")
        if cursor.fetchone()[0] == 0:
            barbeiros = [("Henrique", "61988888888"), ("Gabriel", "61977777777"), ("Bruno", "61966666666")]
            cursor.executemany("INSERT INTO barbeiros (nome, telefone) VALUES (?, ?)", barbeiros)
            self.conexao.commit()

    def obter_ou_criar_cliente(self, nome: str) -> dict:
        cursor = self.conexao.cursor()
        cursor.execute("SELECT id, nome, telefone, pontos_fidelidade FROM clientes WHERE nome LIKE ?", (nome,))
        cliente = cursor.fetchone()
        
        if not cliente:
            cursor.execute("INSERT INTO clientes (nome, telefone, pontos_fidelidade) VALUES (?, ?, ?)", (nome, "000000000", 0))
            self.conexao.commit()
            return {"id": cursor.lastrowid, "nome": nome, "pontos": 0}
        
        return {"id": cliente[0], "nome": cliente[1], "pontos": cliente[3]}

    def atualizar_pontos_cliente(self, cliente_id: int, novos_pontos: int):
        cursor = self.conexao.cursor()
        cursor.execute("UPDATE clientes SET pontos_fidelidade = ? WHERE id = ?", (novos_pontos, cliente_id))
        self.conexao.commit()

    def listar_barbeiros(self) -> list:
        cursor = self.conexao.cursor()
        cursor.execute("SELECT id, nome, telefone FROM barbeiros")
        return cursor.fetchall()

    def listar_clientes(self) -> list:
        cursor = self.conexao.cursor()
        cursor.execute("SELECT nome, pontos_fidelidade FROM clientes")
        return cursor.fetchall()

    def salvar_agendamento(self, cliente_nome, barbeiro_nome, servico, valor, data, status):
        cursor = self.conexao.cursor()
        cursor.execute('''
            INSERT INTO agendamentos (cliente_nome, barbeiro_nome, servico, valor_final, data_hora, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cliente_nome, barbeiro_nome, servico, valor, data, status))
        self.conexao.commit()

# 2. BACKEND 


class StatusAgendamento(Enum):
    PENDENTE = "Pendente"
    CONCLUIDO = "Concluído"

class FormaPagamento(ABC):
    @abstractmethod
    def processar_pagamento(self, valor: float) -> float: pass

class PagamentoPix(FormaPagamento):
    def processar_pagamento(self, valor: float) -> float: return valor * 0.95

class PagamentoCartao(FormaPagamento):
    def processar_pagamento(self, valor: float) -> float: return valor

class Servico(ABC):
    def __init__(self, descricao: str, valor_base: float):
        self.descricao = descricao
        self.valor_base = valor_base
        
    @abstractmethod
    def calcular_preco(self) -> float: pass

class CorteCabelo(Servico):
    def __init__(self, usa_navalha: bool):
        super().__init__("Corte de Cabelo", 40.0)
        self.usa_navalha = usa_navalha
    def calcular_preco(self) -> float:
        return self.valor_base + (10.0 if self.usa_navalha else 0.0)

class TratamentoBarba(Servico):
    def __init__(self, toalha_quente: bool):
        super().__init__("Tratamento de Barba", 30.0)
        self.toalha_quente = toalha_quente
    def calcular_preco(self) -> float:
        return self.valor_base + (15.0 if self.toalha_quente else 0.0)


# 3. FRONTEND (Tkinter Integrado ao Banco)

class AppPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Barbearia - Desk App III (Com SQLite)")
        self.geometry("550x650")
        
        # Inicia a conexão com o banco de dados
        self.db = BancoDeDados()
        
        self.criar_menu_superior()
        
        self.painel_botoes = tk.Frame(self, pady=10)
        self.painel_botoes.pack(fill=tk.X)
        
        btn_estilo = {"font": ("Arial", 11, "bold"), "bg": "#007BFF", "fg": "white", "padx": 10, "pady": 5}
        
        tk.Button(self.painel_botoes, text="Clientes", command=self.mostrar_clientes, **btn_estilo).pack(side=tk.LEFT, expand=True, padx=5)
        tk.Button(self.painel_botoes, text="Barbeiros", command=self.mostrar_barbeiros, **btn_estilo).pack(side=tk.LEFT, expand=True, padx=5)
        tk.Button(self.painel_botoes, text="Novo Agendamento", command=self.mostrar_agendamento, **btn_estilo).pack(side=tk.LEFT, expand=True, padx=5)
        
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=10, pady=5)
        
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.mostrar_home()

    def criar_menu_superior(self):
        barra_menu = tk.Menu(self)
        
        menu_cadastros = tk.Menu(barra_menu, tearoff=0)
        menu_cadastros.add_command(label="Clientes", command=self.mostrar_clientes)
        menu_cadastros.add_command(label="Barbeiros", command=self.mostrar_barbeiros)
        barra_menu.add_cascade(label="Cadastros", menu=menu_cadastros)
        
        menu_atendimentos = tk.Menu(barra_menu, tearoff=0)
        menu_atendimentos.add_command(label="Novo Agendamento", command=self.mostrar_agendamento)
        barra_menu.add_cascade(label="Atendimentos", menu=menu_atendimentos)
        
        menu_sistema = tk.Menu(barra_menu, tearoff=0)
        menu_sistema.add_command(label="Sair", command=self.quit)
        barra_menu.add_cascade(label="Sistema", menu=menu_sistema)
        
        self.config(menu=barra_menu)

    def limpar_tela(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def mostrar_home(self):
        self.limpar_tela()
        tk.Label(self.container, text="Bem-vindo ao Sistema (Nível 3)", font=("Arial", 18, "bold")).pack(pady=40)
        tk.Label(self.container, text="Os dados agora são salvos de forma permanente\nno banco de dados SQLite.", justify="center", font=("Arial", 11)).pack()

    def mostrar_clientes(self):
        self.limpar_tela()
        tk.Label(self.container, text="Clientes Cadastrados", font=("Arial", 14, "bold")).pack(pady=10)
        
        lista = tk.Listbox(self.container, width=55, font=("Arial", 10))
        lista.pack(pady=10)
        
        # Puxa os dados direto do BANCO DE DADOS
        clientes = self.db.listar_clientes()
        if not clientes:
            lista.insert(tk.END, " Nenhum cliente cadastrado ainda.")
        else:
            for nome, pontos in clientes:
                lista.insert(tk.END, f" Nome: {nome} | Pontos Fidelidade: {pontos}")

    def mostrar_barbeiros(self):
        self.limpar_tela()
        tk.Label(self.container, text="Equipe de Barbeiros", font=("Arial", 14, "bold")).pack(pady=10)
        
        lista = tk.Listbox(self.container, width=55, font=("Arial", 10))
        lista.pack(pady=10)
        
        # Puxa os dados direto do BANCO DE DADOS
        barbeiros = self.db.listar_barbeiros()
        for b_id, nome, telefone in barbeiros:
            lista.insert(tk.END, f" Nome: {nome} | Telefone: {telefone}")

    def mostrar_agendamento(self):
        self.limpar_tela()
        tk.Label(self.container, text="Novo Agendamento", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Label(self.container, text="Nome do Cliente:", font=("Arial", 10, "bold")).pack(pady=(5,0))
        self.entry_cliente = tk.Entry(self.container, width=40, font=("Arial", 10))
        self.entry_cliente.pack(pady=5)
        
        tk.Label(self.container, text="Selecione o Barbeiro:", font=("Arial", 10, "bold")).pack(pady=(10,0))
        
        # Preenche o combobox puxando do BANCO DE DADOS
        self.barbeiros_db = self.db.listar_barbeiros()
        nomes_barbeiros = [b[1] for b in self.barbeiros_db]
        
        self.combo_barbeiro = ttk.Combobox(self.container, values=nomes_barbeiros, state="readonly", width=37, font=("Arial", 10))
        if nomes_barbeiros: 
            self.combo_barbeiro.current(0)
        self.combo_barbeiro.pack(pady=5)
        
        tk.Label(self.container, text="Serviço:", font=("Arial", 10, "bold")).pack(pady=(10,0))
        self.var_servico = tk.StringVar(value="corte")
        tk.Radiobutton(self.container, text="Corte Cabelo + Navalha (R$ 50)", variable=self.var_servico, value="corte", font=("Arial", 10)).pack()
        tk.Radiobutton(self.container, text="Barba + Toalha Quente (R$ 45)", variable=self.var_servico, value="barba", font=("Arial", 10)).pack()
        
        tk.Label(self.container, text="Pagamento:", font=("Arial", 10, "bold")).pack(pady=(10,0))
        self.var_pagamento = tk.StringVar(value="pix")
        tk.Radiobutton(self.container, text="PIX (5% Desconto)", variable=self.var_pagamento, value="pix", font=("Arial", 10)).pack()
        tk.Radiobutton(self.container, text="Cartão (Normal)", variable=self.var_pagamento, value="cartao", font=("Arial", 10)).pack()
        
        tk.Button(self.container, text="FINALIZAR ATENDIMENTO", bg="#28A745", fg="white", font=("Arial", 11, "bold"), width=30, command=self.processar_agendamento).pack(pady=20)
        
        self.txt_recibo = tk.Text(self.container, height=10, width=55, font=("Courier", 9))
        self.txt_recibo.pack()

    def processar_agendamento(self):
        nome_cliente = self.entry_cliente.get().strip()
        if not nome_cliente:
            messagebox.showwarning("Aviso", "Por favor, digite o nome do cliente!")
            return
            
        idx_barbeiro = self.combo_barbeiro.current()
        if idx_barbeiro == -1:
            messagebox.showwarning("Aviso", "Selecione um barbeiro!")
            return
            
        nome_barbeiro = self.barbeiros_db[idx_barbeiro][1]
        
        # Regras de Negócio e Cálculos
        servico = CorteCabelo(usa_navalha=True) if self.var_servico.get() == "corte" else TratamentoBarba(toalha_quente=True)
        pagamento = PagamentoPix() if self.var_pagamento.get() == "pix" else PagamentoCartao()
        
        valor_original = servico.calcular_preco()
        valor_final = pagamento.processar_pagamento(valor_original)
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        

        # INTERAÇÃO COM O BANCO DE DADOS
        
        # 1. Pega o cliente no banco ou cria um novo
        dados_cliente = self.db.obter_ou_criar_cliente(nome_cliente)
        
        # 2. Atualiza a pontuação
        novos_pontos = dados_cliente["pontos"] + 10
        self.db.atualizar_pontos_cliente(dados_cliente["id"], novos_pontos)
        
        # 3. Salva o agendamento no histórico
        self.db.salvar_agendamento(dados_cliente["nome"], nome_barbeiro, servico.descricao, valor_final, data_hora, StatusAgendamento.CONCLUIDO.value)
        
        # Gera o recibo na tela
        recibo = (
            f"\n{'='*30}\nRECIBO DE ATENDIMENTO\n{'='*30}\n"
            f"Data: {data_hora}\n"
            f"Cliente: {dados_cliente['nome']}\n"
            f"Barbeiro: {nome_barbeiro}\n"
            f"Serviço: {servico.descricao}\n"
            f"Valor Final: R$ {valor_final:.2f}\n"
            f"Status: {StatusAgendamento.CONCLUIDO.value}\n"
            f"\n* BÔNUS: Cliente ganhou 10 pontos!\n(Total acumulado: {novos_pontos})\n"
            f"{'='*30}"
        )
        
        self.txt_recibo.delete(1.0, tk.END)
        self.txt_recibo.insert(tk.END, recibo)


if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()