import tkinter as tk
from tkinter import messagebox
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

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


# Herança e Polimorfismo
class Pessoa(ABC):
    def __init__(self, nome: str, telefone: str):
        self._nome = nome
        self._telefone = telefone

# HERANÇA: Cliente herda de Pessoa
class Cliente(Pessoa):
    def __init__(self, nome: str, telefone: str):
        super().__init__(nome, telefone)
        self.pontos_fidelidade = 0

# HERANÇA: Barbeiro herda de Pessoa
class Barbeiro(Pessoa):
    def __init__(self, nome: str, telefone: str, especialidade: str):
        super().__init__(nome, telefone)
        self.especialidade = especialidade

class Servico(ABC):
    def __init__(self, descricao: str, valor_base: float):
        self._descricao = descricao
        self._valor_base = valor_base
        
    @abstractmethod
    def calcular_preco(self) -> float:
        pass

# HERANÇA E POLIMORFISMO: CorteCabelo sobrescreve calcular_preco
class CorteCabelo(Servico):
    def __init__(self, usa_navalha: bool):
        super().__init__("Corte de Cabelo", 40.0)
        self.usa_navalha = usa_navalha

    def calcular_preco(self) -> float:
        return self._valor_base + (10.0 if self.usa_navalha else 0.0)

# HERANÇA E POLIMORFISMO: TratamentoBarba sobrescreve calcular_preco
class TratamentoBarba(Servico):
    def __init__(self, toalha_quente: bool):
        super().__init__("Tratamento de Barba", 30.0)
        self.toalha_quente = toalha_quente

    def calcular_preco(self) -> float:
        return self._valor_base + (15.0 if self.toalha_quente else 0.0)

# DEPENDÊNCIA: Agendamento usa essa classe em um momento específico
class GeradorRecibo:
    def imprimir(self, dados: str) -> str:
        return f"\n{'='*30}\nRECIBO DE ATENDIMENTO\n{'='*30}\n{dados}\n{'='*30}"

# (Composição e Associação)

class Agendamento:
    # ASSOCIAÇÃO: Agendamento conhece Cliente, Barbeiro e Servico
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
        
        # POLIMORFISMO: O python sabe chamar o cálculo certo dependendo do serviço
        valor_original = self.servico.calcular_preco()
        
        # STRATEGY: Calcula o valor final dependendo se é PIX ou Cartão
        valor_final = self.metodo_pagamento.processar_pagamento(valor_original)
        
        # Lógica de fidelidade
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
        
        # DEPENDÊNCIA: Usando o gerador
        return gerador_recibo.imprimir(dados_recibo)

# COMPOSIÇÃO: Barbearia gerencia os agendamentos
class Barbearia:
    def __init__(self, nome: str):
        self.nome = nome
        self.agendamentos = []

    def registrar_agendamento(self, agendamento: Agendamento):
        self.agendamentos.append(agendamento)


# 4. INTERFACE GRÁFICA (Desktop App - Tkinter)

class AppBarbearia:
    def __init__(self, root):
        self.root = root
        self.root.title("Barbearia Desk App I")
        self.root.geometry("400x550")
        
        # Dados iniciais para demonstração
        self.barbearia = Barbearia("Barbearia do Dev")
        self.barbeiro_demo = Barbeiro("João Silva", "11999999999", "Fade")
        
        # UI Elements
        tk.Label(root, text="Novo Agendamento", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(root, text="Nome do Cliente:").pack()
        self.entry_cliente = tk.Entry(root, width=40)
        self.entry_cliente.pack(pady=5)
        
        tk.Label(root, text="Selecione o Serviço:").pack()
        self.var_servico = tk.StringVar(value="corte")
        tk.Radiobutton(root, text="Corte Cabelo + Navalha (R$ 50)", variable=self.var_servico, value="corte").pack()
        tk.Radiobutton(root, text="Barba + Toalha Quente (R$ 45)", variable=self.var_servico, value="barba").pack()
        
        tk.Label(root, text="Forma de Pagamento:").pack(pady=(10,0))
        self.var_pagamento = tk.StringVar(value="pix")
        tk.Radiobutton(root, text="PIX (5% Desconto)", variable=self.var_pagamento, value="pix").pack()
        tk.Radiobutton(root, text="Cartão (Valor Normal)", variable=self.var_pagamento, value="cartao").pack()
        
        self.btn_finalizar = tk.Button(root, text="FINALIZAR ATENDIMENTO", bg="green", fg="white", font=("Arial", 12, "bold"), command=self.finalizar)
        self.btn_finalizar.pack(pady=20)
        
        self.txt_recibo = tk.Text(root, height=10, width=45)
        self.txt_recibo.pack()

    def finalizar(self):
        nome_cliente = self.entry_cliente.get()
        if not nome_cliente:
            messagebox.showwarning("Aviso", "Preencha o nome do cliente!")
            return
            
        cliente = Cliente(nome_cliente, "000000000")
        
        # Define Serviço
        if self.var_servico.get() == "corte":
            servico = CorteCabelo(usa_navalha=True)
        else:
            servico = TratamentoBarba(toalha_quente=True)
            
        # Define Pagamento
        pagamento = PagamentoPix() if self.var_pagamento.get() == "pix" else PagamentoCartao()
        
        # Realiza as operações de OO
        agendamento = Agendamento(cliente, self.barbeiro_demo, servico)
        self.barbearia.registrar_agendamento(agendamento)
        
        gerador = GeradorRecibo()
        recibo = agendamento.finalizar_atendimento(pagamento, gerador)
        
        # Mostra na tela
        self.txt_recibo.delete(1.0, tk.END)
        self.txt_recibo.insert(tk.END, recibo)


if __name__ == "__main__":
    janela = tk.Tk()
    app = AppBarbearia(janela)
    janela.mainloop()