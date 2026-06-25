import tkinter as tk
from tkinter import messagebox, ttk
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime


# BACKEND - Modelos

class StatusAgendamento(Enum):
    PENDENTE = "Pendente"
    CONCLUIDO = "Concluído"
    CANCELADO = "Cancelado"

class FormaPagamento(ABC):
    @abstractmethod
    def processar_pagamento(self, valor: float) -> float:
        pass

class PagamentoPix(FormaPagamento):
    def processar_pagamento(self, valor: float) -> float:
        return valor * 0.95  # 5% de desconto

class PagamentoCartao(FormaPagamento):
    def processar_pagamento(self, valor: float) -> float:
        return valor  # Sem desconto

class Pessoa(ABC):
    def __init__(self, nome: str, telefone: str):
        self._nome = nome
        self._telefone = telefone

class Cliente(Pessoa):
    def __init__(self, nome: str, telefone: str):
        super().__init__(nome, telefone)
        self.pontos_fidelidade = 0

class Barbeiro(Pessoa):
    def __init__(self, nome: str, telefone: str):
        super().__init__(nome, telefone)

class Servico(ABC):
    def __init__(self, descricao: str, valor_base: float):
        self._descricao = descricao
        self._valor_base = valor_base
        
    @abstractmethod
    def calcular_preco(self) -> float:
        pass

class CorteCabelo(Servico):
    def __init__(self, usa_navalha: bool):
        super().__init__("Corte de Cabelo", 40.0)
        self.usa_navalha = usa_navalha

    def calcular_preco(self) -> float:
        return self._valor_base + (10.0 if self.usa_navalha else 0.0)

class TratamentoBarba(Servico):
    def __init__(self, toalha_quente: bool):
        super().__init__("Tratamento de Barba", 30.0)
        self.toalha_quente = toalha_quente

    def calcular_preco(self) -> float:
        return self._valor_base + (15.0 if self.toalha_quente else 0.0)

class GeradorRecibo:
    def imprimir(self, dados: str) -> str:
        return f"\n{'='*30}\nRECIBO DE ATENDIMENTO\n{'='*30}\n{dados}\n{'='*30}"

class Agendamento:
    def __init__(self, cliente: Cliente, barbeiro: Barbeiro, servico: Servico):
        self.cliente = cliente
        self.barbeiro = barbeiro
        self.servico = servico
        self.data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.status = StatusAgendamento.PENDENTE
        self.metodo_pagamento = None

    def finalizar_atendimento(self, pagamento: FormaPagamento, gerador_recibo: GeradorRecibo) -> str:
        self.status = StatusAgendamento.CONCLUIDO
        self.metodo_pagamento = pagamento
        valor_original = self.servico.calcular_preco()
        valor_final = self.metodo_pagamento.processar_pagamento(valor_original)
        
        self.cliente.pontos_fidelidade += 10
        fidelidade_msg = "\n* BÔNUS: Cliente ganhou 10 pontos!"
        
        dados_recibo = (
            f"Data: {self.data_hora}\n"
            f"Cliente: {self.cliente._nome}\n"
            f"Barbeiro: {self.barbeiro._nome}\n"
            f"Serviço: {self.servico._descricao}\n"
            f"Valor Final: R$ {valor_final:.2f}\n"
            f"Status: {self.status.value}"
            f"{fidelidade_msg}"
        )
        return gerador_recibo.imprimir(dados_recibo)

class Barbearia:
    def __init__(self, nome: str):
        self.nome = nome
        self.agendamentos = []
        self.clientes = []
        # Adicionados mais barbeiros
        self.barbeiros = [
            Barbeiro("Henrique", "61988888888"),
            Barbeiro("Gabriel", "61977777777"),
            Barbeiro("Bruno", "61966666666")
        ]

    def registrar_agendamento(self, agendamento: Agendamento):
        self.agendamentos.append(agendamento)


# FRONTEND Interface Gráfica


class AppPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Barbearia - Desk App II")
        self.geometry("550x650")
        
        self.barbearia = Barbearia("Barbearia do Dev")
        
        # Criação da barra de menu superior tradicional
        self.criar_menu_superior()
        
        # Painel de Botões de Navegação (Mais visíveis e centralizados)
        self.painel_botoes = tk.Frame(self, pady=10)
        self.painel_botoes.pack(fill=tk.X)
        
        btn_estilo = {"font": ("Arial", 11, "bold"), "bg": "#007BFF", "fg": "white", "padx": 10, "pady": 5}
        
        # CORREÇÃO: Usando padx ao invés de mx
        tk.Button(self.painel_botoes, text="Clientes", command=self.mostrar_clientes, **btn_estilo).pack(side=tk.LEFT, expand=True, padx=5)
        tk.Button(self.painel_botoes, text="Barbeiros", command=self.mostrar_barbeiros, **btn_estilo).pack(side=tk.LEFT, expand=True, padx=5)
        tk.Button(self.painel_botoes, text="Novo Agendamento", command=self.mostrar_agendamento, **btn_estilo).pack(side=tk.LEFT, expand=True, padx=5)
        
        # Separador visual
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=10, pady=5)
        
        # Container onde as telas vão ser trocadas
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
        tk.Label(self.container, text="Bem-vindo ao Sistema", font=("Arial", 18, "bold")).pack(pady=40)
        tk.Label(self.container, text="Selecione uma opção nos botões superiores ou no menu\npara navegar pelas funcionalidades do projeto.", justify="center", font=("Arial", 11)).pack()

    def mostrar_clientes(self):
        self.limpar_tela()
        tk.Label(self.container, text="Clientes Cadastrados", font=("Arial", 14, "bold")).pack(pady=10)
        
        lista = tk.Listbox(self.container, width=55, font=("Arial", 10))
        lista.pack(pady=10)
        for c in self.barbearia.clientes:
            lista.insert(tk.END, f" Nome: {c._nome} | Pontos Fidelidade: {c.pontos_fidelidade}")

    def mostrar_barbeiros(self):
        self.limpar_tela()
        tk.Label(self.container, text="Equipe de Barbeiros", font=("Arial", 14, "bold")).pack(pady=10)
        
        lista = tk.Listbox(self.container, width=55, font=("Arial", 10))
        lista.pack(pady=10)
        for b in self.barbearia.barbeiros:
            # Removido o campo de especialidade da exibição
            lista.insert(tk.END, f" Nome: {b._nome} | Telefone: {b._telefone}")

    def mostrar_agendamento(self):
        self.limpar_tela()
        tk.Label(self.container, text="Novo Agendamento", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Entrada Manual do Nome do Cliente
        tk.Label(self.container, text="Nome do Cliente:", font=("Arial", 10, "bold")).pack(pady=(5,0))
        self.entry_cliente = tk.Entry(self.container, width=40, font=("Arial", 10))
        self.entry_cliente.pack(pady=5)
        
        # Seleção de Barbeiro via Combobox
        tk.Label(self.container, text="Selecione o Barbeiro:", font=("Arial", 10, "bold")).pack(pady=(10,0))
        self.combo_barbeiro = ttk.Combobox(self.container, values=[b._nome for b in self.barbearia.barbeiros], state="readonly", width=37, font=("Arial", 10))
        if self.barbearia.barbeiros: 
            self.combo_barbeiro.current(0)
        self.combo_barbeiro.pack(pady=5)
        
        # Seleção de Serviço
        tk.Label(self.container, text="Serviço:", font=("Arial", 10, "bold")).pack(pady=(10,0))
        self.var_servico = tk.StringVar(value="corte")
        tk.Radiobutton(self.container, text="Corte Cabelo + Navalha (R$ 50)", variable=self.var_servico, value="corte", font=("Arial", 10)).pack()
        tk.Radiobutton(self.container, text="Barba + Toalha Quente (R$ 45)", variable=self.var_servico, value="barba", font=("Arial", 10)).pack()
        
        # Seleção de Pagamento
        tk.Label(self.container, text="Pagamento:", font=("Arial", 10, "bold")).pack(pady=(10,0))
        self.var_pagamento = tk.StringVar(value="pix")
        tk.Radiobutton(self.container, text="PIX (5% Desconto)", variable=self.var_pagamento, value="pix", font=("Arial", 10)).pack()
        tk.Radiobutton(self.container, text="Cartão (Normal)", variable=self.var_pagamento, value="cartao", font=("Arial", 10)).pack()
        
        # Botão Finalizar Atendimento
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
            
        # Procura se o cliente já existe na memória para manter o histórico de pontos
        cliente_atual = None
        for c in self.barbearia.clientes:
            if c._nome.lower() == nome_cliente.lower():
                cliente_atual = c
                break
        
        # Se for um cliente novo, cria o objeto e adiciona na lista da barbearia
        if not cliente_atual:
            cliente_atual = Cliente(nome_cliente, "000000000")
            self.barbearia.clientes.append(cliente_atual)
            
        barbeiro_selecionado = self.barbearia.barbeiros[idx_barbeiro]
        
        if self.var_servico.get() == "corte":
            servico = CorteCabelo(usa_navalha=True)
        else:
            servico = TratamentoBarba(toalha_quente=True)
            
        pagamento = PagamentoPix() if self.var_pagamento.get() == "pix" else PagamentoCartao()
        
        agendamento = Agendamento(cliente_atual, barbeiro_selecionado, servico)
        self.barbearia.registrar_agendamento(agendamento)
        
        gerador = GeradorRecibo()
        recibo = agendamento.finalizar_atendimento(pagamento, gerador)
        
        self.txt_recibo.delete(1.0, tk.END)
        self.txt_recibo.insert(tk.END, recibo)


if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()