"""
==================================================
ProteinCost — Calculadora Inteligente de Custo por Grama de Proteína
==================================================
Disciplina: Matemática Computacional Aplicada
Área: Saúde
Tecnologias: Python 3, CustomTkinter

Objetivo:
    Comparar alimentos proteicos e identificar o de menor custo por grama
    de proteína, aplicando funções matemáticas, lógica booleana e estruturas
    de dados nativas do Python.

Autores: [Seu Nome]
Data: 2025
==================================================
"""

# ── Importações ────────────────────────────────────────────────────────────────
import customtkinter as ctk           # Interface gráfica moderna
from tkinter import messagebox        # Caixas de diálogo nativas
import tkinter as tk
from math_engine import (             # Módulo de lógica matemática
    calcular_proteina_total,
    calcular_custo_por_grama,
    calcular_media_custo,
    ordenar_por_custo,
    formatar_moeda,
    formatar_grama,
)
from ui_components import (           # Módulo de componentes visuais
    TabelaAlimentos,
    PainelRanking,
    FormularioEntrada,
    BarraStatus,
)

# ── Configuração global do tema ────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ── Paleta de cores do projeto ─────────────────────────────────────────────────
# Definidas como constantes para facilitar manutenção e coesão visual
CORES = {
    "verde_escuro":  "#2D6A4F",
    "verde_medio":   "#40916C",
    "verde_claro":   "#95D5B2",
    "verde_palido":  "#B7E4C7",
    "branco":        "#FFFFFF",
    "preto_suave":   "#1B4332",
    "fundo_escuro":  "#0D1F16",
    "fundo_card":    "#1A3826",
    "texto_claro":   "#D8F3DC",
    "amarelo":       "#FFD60A",
    "vermelho":      "#FF4D6D",
    "cinza_suave":   "#52796F",
}


# ==============================================================================
# CLASSE PRINCIPAL DA APLICAÇÃO
# ==============================================================================
class ProteinCostApp(ctk.CTk):
    """
    Classe principal que gerencia toda a interface e lógica da aplicação.

    MATEMÁTICA APLICADA:
    - Encapsula listas de dicionários (estrutura de dados)
    - Chama funções matemáticas do módulo math_engine
    - Aplica ordenação e comparação (álgebra de conjuntos)
    """

    def __init__(self):
        super().__init__()

        # ── Configuração da janela principal ──────────────────────────────────
        self.title("ProteinCost — Calculadora de Custo Proteico")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(fg_color=CORES["fundo_escuro"])

        # ── Estrutura de dados principal ──────────────────────────────────────
        # MATEMÁTICA: Lista de dicionários — estrutura de conjunto ordenado
        # Cada alimento é representado como um vetor de atributos:
        # { nome, preco, peso_total, proteina_por_100g, proteina_total, custo_por_grama }
        self.alimentos: list[dict] = []

        # ── Construção da interface ────────────────────────────────────────────
        self._construir_interface()

        # ── Atalho de teclado F1 para o manual ────────────────────────────────
        self.bind("<F1>", lambda e: self._abrir_manual())

    # ──────────────────────────────────────────────────────────────────────────
    # CONSTRUÇÃO DA INTERFACE
    # ──────────────────────────────────────────────────────────────────────────
    def _construir_interface(self):
        """Monta todos os painéis e widgets da interface principal."""

        # Configurar grid responsivo
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # ── Cabeçalho ─────────────────────────────────────────────────────────
        self._criar_cabecalho()

        # ── Painel esquerdo (formulário + botões) ──────────────────────────────
        self.painel_esquerdo = ctk.CTkFrame(
            self,
            fg_color=CORES["fundo_card"],
            corner_radius=16,
        )
        self.painel_esquerdo.grid(
            row=1, column=0, padx=(16, 8), pady=(8, 8), sticky="nsew"
        )
        self.painel_esquerdo.grid_rowconfigure(1, weight=1)
        self.painel_esquerdo.grid_columnconfigure(0, weight=1)

        # ── Painel direito (tabela + ranking) ─────────────────────────────────
        self.painel_direito = ctk.CTkFrame(
            self,
            fg_color=CORES["fundo_card"],
            corner_radius=16,
        )
        self.painel_direito.grid(
            row=1, column=1, padx=(8, 16), pady=(8, 8), sticky="nsew"
        )
        self.painel_direito.grid_rowconfigure(0, weight=3)
        self.painel_direito.grid_rowconfigure(1, weight=1)
        self.painel_direito.grid_columnconfigure(0, weight=1)

        # ── Componentes internos ───────────────────────────────────────────────
        self.formulario = FormularioEntrada(
            self.painel_esquerdo,
            cores=CORES,
            callback_adicionar=self._adicionar_alimento,
        )
        self.formulario.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")

        self._criar_botoes_acao()

        self.tabela = TabelaAlimentos(
            self.painel_direito,
            cores=CORES,
            callback_remover=self._remover_alimento,
        )
        self.tabela.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="nsew")

        self.painel_ranking = PainelRanking(
            self.painel_direito,
            cores=CORES,
        )
        self.painel_ranking.grid(row=1, column=0, padx=16, pady=(8, 16), sticky="nsew")

        # ── Barra de status ────────────────────────────────────────────────────
        self.barra_status = BarraStatus(self, cores=CORES)
        self.barra_status.grid(
            row=2, column=0, columnspan=2, padx=16, pady=(0, 8), sticky="ew"
        )

    def _criar_cabecalho(self):
        """Cria o cabeçalho visual do sistema com título e botão de manual."""
        frame_header = ctk.CTkFrame(
            self,
            fg_color=CORES["verde_escuro"],
            corner_radius=12,
            height=72,
        )
        frame_header.grid(row=0, column=0, columnspan=2, padx=16, pady=(16, 0), sticky="ew")
        frame_header.grid_propagate(False)
        frame_header.grid_columnconfigure(1, weight=1)

        # Ícone decorativo
        label_icone = ctk.CTkLabel(
            frame_header,
            text="🥩",
            font=ctk.CTkFont(size=32),
            fg_color="transparent",
        )
        label_icone.grid(row=0, column=0, padx=(20, 8), pady=12)

        # Título principal
        frame_titulos = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_titulos.grid(row=0, column=1, sticky="w", pady=8)

        ctk.CTkLabel(
            frame_titulos,
            text="ProteinCost",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=CORES["verde_claro"],
            fg_color="transparent",
        ).pack(anchor="w")

        ctk.CTkLabel(
            frame_titulos,
            text="Calculadora Inteligente de Custo por Grama de Proteína",
            font=ctk.CTkFont(size=11),
            text_color=CORES["texto_claro"],
            fg_color="transparent",
        ).pack(anchor="w")

        # Botões do cabeçalho
        frame_btns_header = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_btns_header.grid(row=0, column=2, padx=16, pady=12)

        ctk.CTkButton(
            frame_btns_header,
            text="📖  Manual  F1",
            width=130,
            height=36,
            fg_color=CORES["verde_medio"],
            hover_color=CORES["verde_claro"],
            text_color=CORES["preto_suave"],
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=8,
            command=self._abrir_manual,
        ).pack()

    def _criar_botoes_acao(self):
        """Cria o painel com os botões de ação principais."""
        frame_botoes = ctk.CTkFrame(
            self.painel_esquerdo,
            fg_color="transparent",
        )
        frame_botoes.grid(row=1, column=0, padx=16, pady=8, sticky="nsew")
        frame_botoes.grid_columnconfigure((0, 1), weight=1)

        # ── Botão Calcular ─────────────────────────────────────────────────────
        ctk.CTkButton(
            frame_botoes,
            text="⚡  Calcular Ranking",
            height=44,
            fg_color=CORES["verde_escuro"],
            hover_color=CORES["verde_medio"],
            text_color=CORES["verde_claro"],
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10,
            command=self._calcular_ranking,
        ).grid(row=0, column=0, columnspan=2, padx=4, pady=6, sticky="ew")

        # ── Botão Remover Selecionado ──────────────────────────────────────────
        ctk.CTkButton(
            frame_botoes,
            text="🗑  Remover",
            height=38,
            fg_color=CORES["fundo_escuro"],
            hover_color=CORES["vermelho"],
            text_color=CORES["texto_claro"],
            border_color=CORES["cinza_suave"],
            border_width=1,
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            command=self._remover_alimento,
        ).grid(row=1, column=0, padx=(4, 2), pady=4, sticky="ew")

        # ── Botão Limpar Tudo ──────────────────────────────────────────────────
        ctk.CTkButton(
            frame_botoes,
            text="🔄  Limpar Tudo",
            height=38,
            fg_color=CORES["fundo_escuro"],
            hover_color="#7B2D30",
            text_color=CORES["texto_claro"],
            border_color=CORES["cinza_suave"],
            border_width=1,
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            command=self._limpar_tudo,
        ).grid(row=1, column=1, padx=(2, 4), pady=4, sticky="ew")

        # ── Área de estatísticas resumidas ────────────────────────────────────
        self.frame_stats = ctk.CTkFrame(
            frame_botoes,
            fg_color=CORES["preto_suave"],
            corner_radius=10,
        )
        self.frame_stats.grid(
            row=2, column=0, columnspan=2, padx=4, pady=(12, 4), sticky="ew"
        )

        ctk.CTkLabel(
            self.frame_stats,
            text="📊  Estatísticas",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=CORES["verde_claro"],
            fg_color="transparent",
        ).pack(anchor="w", padx=12, pady=(8, 2))

        self.label_total_alimentos = ctk.CTkLabel(
            self.frame_stats,
            text="Alimentos cadastrados: 0",
            font=ctk.CTkFont(size=11),
            text_color=CORES["texto_claro"],
            fg_color="transparent",
        )
        self.label_total_alimentos.pack(anchor="w", padx=12, pady=2)

        self.label_media_custo = ctk.CTkLabel(
            self.frame_stats,
            text="Média de custo: —",
            font=ctk.CTkFont(size=11),
            text_color=CORES["texto_claro"],
            fg_color="transparent",
        )
        self.label_media_custo.pack(anchor="w", padx=12, pady=2)

        self.label_melhor = ctk.CTkLabel(
            self.frame_stats,
            text="Melhor custo-benefício: —",
            font=ctk.CTkFont(size=11),
            text_color=CORES["amarelo"],
            fg_color="transparent",
            wraplength=220,
        )
        self.label_melhor.pack(anchor="w", padx=12, pady=(2, 8))

    # ──────────────────────────────────────────────────────────────────────────
    # LÓGICA DE NEGÓCIO — AÇÕES DOS BOTÕES
    # ──────────────────────────────────────────────────────────────────────────

    def _adicionar_alimento(self, dados: dict):
        """
        Recebe os dados do formulário, valida e adiciona o alimento à lista.

        MATEMÁTICA APLICADA:
        - Chama calcular_proteina_total() → fórmula: (proteina_por_100g * peso) / 100
        - Chama calcular_custo_por_grama() → fórmula: preco / proteina_total
        - Lógica booleana para validação de entrada
        """
        # LÓGICA BOOLEANA: Verificação de campos obrigatórios
        nome = dados.get("nome", "").strip()
        if not nome:
            self.barra_status.erro("⚠ Nome do alimento não pode ser vazio.")
            return

        # LÓGICA BOOLEANA: Verificação de valores numéricos positivos
        try:
            preco        = float(dados["preco"])
            peso_total   = float(dados["peso_total"])
            prot_100g    = float(dados["proteina_por_100g"])
        except ValueError:
            self.barra_status.erro("⚠ Preencha todos os campos numéricos corretamente.")
            return

        # LÓGICA BOOLEANA: Impedir valores negativos ou zero
        if preco <= 0 or peso_total <= 0 or prot_100g <= 0:
            self.barra_status.erro("⚠ Valores devem ser maiores que zero.")
            return

        if prot_100g > 100:
            self.barra_status.erro("⚠ Proteína por 100g não pode ultrapassar 100g.")
            return

        # ── CÁLCULOS MATEMÁTICOS ───────────────────────────────────────────────
        # Fórmula 1: proteina_total = (proteina_por_100g * peso_total) / 100
        proteina_total = calcular_proteina_total(prot_100g, peso_total)

        # Verificação de divisão por zero (LÓGICA BOOLEANA)
        if proteina_total == 0:
            self.barra_status.erro("⚠ Proteína total não pode ser zero.")
            return

        # Fórmula 2: custo_por_grama = preco / proteina_total
        custo_por_grama = calcular_custo_por_grama(preco, proteina_total)

        # ── Criação do dicionário do alimento (ESTRUTURA DE DADOS) ────────────
        # Representação vetorial: [preco, proteina_total, custo_por_grama]
        alimento = {
            "nome":              nome,
            "preco":             preco,
            "peso_total":        peso_total,
            "proteina_por_100g": prot_100g,
            "proteina_total":    proteina_total,
            "custo_por_grama":   custo_por_grama,
        }

        # Adiciona à lista principal
        self.alimentos.append(alimento)

        # Atualiza a interface
        self.tabela.atualizar(self.alimentos)
        self._atualizar_stats()
        self.formulario.limpar()
        self.barra_status.sucesso(
            f"✅  '{nome}' adicionado — {formatar_grama(proteina_total)} de proteína"
            f" por {formatar_moeda(custo_por_grama)}/g"
        )

    def _calcular_ranking(self):
        """
        Ordena os alimentos pelo custo por grama e exibe o ranking visual.

        MATEMÁTICA APLICADA:
        - Algoritmo de ordenação (sorted) — comparação numérica
        - Cálculo da média aritmética
        - Identificação do mínimo (melhor custo)
        """
        # LÓGICA BOOLEANA: verificar se há alimentos cadastrados
        if not self.alimentos:
            self.barra_status.erro("⚠ Cadastre ao menos um alimento antes de calcular.")
            return

        if len(self.alimentos) < 2:
            self.barra_status.aviso("ℹ  Adicione pelo menos 2 alimentos para comparar.")

        # ORDENAÇÃO: menor custo_por_grama primeiro (algoritmo de comparação)
        ranking = ordenar_por_custo(self.alimentos)

        # MÉDIA ARITMÉTICA: soma dos custos / quantidade
        media = calcular_media_custo(self.alimentos)

        # Atualiza o painel de ranking visual
        self.painel_ranking.atualizar(ranking, media)

        # Destaca o melhor na tabela
        self.tabela.destacar_melhor(ranking[0]["nome"])

        # Mensagem educativa
        melhor = ranking[0]
        self.barra_status.sucesso(
            f"🏆  '{melhor['nome']}' possui o melhor custo-benefício: "
            f"{formatar_moeda(melhor['custo_por_grama'])}/g de proteína"
        )

        self._atualizar_stats(ranking=ranking, media=media)

    def _remover_alimento(self, nome: str = None):
        """
        Remove um alimento da lista pelo nome.

        LÓGICA BOOLEANA: verificações de existência e confirmação
        """
        # Se não vier da tabela, pegar o selecionado
        if nome is None:
            nome = self.tabela.obter_selecionado()

        if not nome:
            self.barra_status.aviso("ℹ  Selecione um alimento na tabela para remover.")
            return

        # LÓGICA BOOLEANA: confirmar remoção
        confirmado = messagebox.askyesno(
            "Confirmar remoção",
            f"Deseja remover '{nome}' da lista?",
        )

        if confirmado:
            # List comprehension — filtra o alimento pelo nome (CONJUNTOS)
            self.alimentos = [a for a in self.alimentos if a["nome"] != nome]
            self.tabela.atualizar(self.alimentos)
            self.painel_ranking.limpar()
            self._atualizar_stats()
            self.barra_status.sucesso(f"🗑  '{nome}' removido com sucesso.")

    def _limpar_tudo(self):
        """Apaga todos os alimentos cadastrados após confirmação."""
        # LÓGICA BOOLEANA: verificar se há dados para limpar
        if not self.alimentos:
            self.barra_status.aviso("ℹ  Não há alimentos cadastrados.")
            return

        confirmado = messagebox.askyesno(
            "Confirmar limpeza",
            "Deseja apagar todos os alimentos cadastrados?",
        )

        if confirmado:
            self.alimentos = []        # Esvazia a lista (ESTRUTURA DE DADOS)
            self.tabela.atualizar(self.alimentos)
            self.painel_ranking.limpar()
            self._atualizar_stats()
            self.formulario.limpar()
            self.barra_status.aviso("🔄  Todos os dados foram apagados.")

    def _atualizar_stats(self, ranking=None, media=None):
        """Atualiza os indicadores estatísticos no painel esquerdo."""
        total = len(self.alimentos)
        self.label_total_alimentos.configure(
            text=f"Alimentos cadastrados: {total}"
        )

        # LÓGICA BOOLEANA: só calcula se houver dados
        if self.alimentos and media is not None:
            self.label_media_custo.configure(
                text=f"Média de custo: {formatar_moeda(media)}/g"
            )
        elif self.alimentos:
            custos = [a["custo_por_grama"] for a in self.alimentos]
            med = sum(custos) / len(custos)
            self.label_media_custo.configure(
                text=f"Média de custo: {formatar_moeda(med)}/g"
            )
        else:
            self.label_media_custo.configure(text="Média de custo: —")

        if ranking:
            self.label_melhor.configure(
                text=f"🏆 Melhor: {ranking[0]['nome']} "
                     f"({formatar_moeda(ranking[0]['custo_por_grama'])}/g)"
            )
        elif not self.alimentos:
            self.label_melhor.configure(text="Melhor custo-benefício: —")

    def _abrir_manual(self):
        """Exibe a janela do manual de uso do sistema."""
        janela_manual = JanelaManual(self, cores=CORES)
        janela_manual.grab_set()


# ==============================================================================
# JANELA DO MANUAL DE USO
# ==============================================================================
class JanelaManual(ctk.CTkToplevel):
    """
    Janela modal com o manual completo de uso do sistema.
    Acessível via botão ou tecla F1.
    """

    CONTEUDO = """
📌  COMO USAR O ProteinCost

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CADASTRAR UM ALIMENTO
   • Preencha todos os campos do formulário:
     - Nome: ex. "Frango grelhado"
     - Preço (R$): valor total pago pelo produto
     - Quantidade: peso total comprado (em gramas)
     - Proteína/100g: gramas de proteína por 100g do alimento
       (esta informação está na embalagem do produto)
   • Clique em "➕ Adicionar"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. CALCULAR O RANKING
   • Após cadastrar 2 ou mais alimentos,
     clique em "⚡ Calcular Ranking"
   • O sistema irá:
     ✔ Calcular a proteína total de cada alimento
     ✔ Calcular o custo por grama de proteína
     ✔ Ordenar do mais barato ao mais caro
     ✔ Destacar o melhor custo-benefício

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. INTERPRETAR OS RESULTADOS
   • 🥇 1º lugar = alimento mais econômico por proteína
   • O destaque amarelo/dourado indica o melhor
   • Compare a coluna "R$/g prot." entre os alimentos
   • Quanto menor o valor, mais barato é a proteína

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. REMOVER UM ALIMENTO
   • Clique sobre a linha na tabela para selecioná-la
   • Clique no botão "🗑 Remover"

5. LIMPAR TUDO
   • Clique em "🔄 Limpar Tudo" para recomeçar

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📐  MATEMÁTICA APLICADA

Fórmula 1 — Proteína Total:
  proteina_total = (proteina_por_100g × peso_total) / 100

Fórmula 2 — Custo por Grama de Proteína:
  custo_por_grama = preço / proteina_total

Fórmula 3 — Média de Custo:
  média = Σ(custo_por_grama) / n_alimentos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡  EXEMPLOS PRÁTICOS

Frango (500g, R$8,50, 25g prot/100g):
  proteina_total = (25 × 500) / 100 = 125g
  custo/g = 8,50 / 125 = R$0,068/g

Atum enlatado (170g, R$5,90, 26g prot/100g):
  proteina_total = (26 × 170) / 100 = 44,2g
  custo/g = 5,90 / 44,2 = R$0,133/g

→ Frango tem custo mais baixo por grama de proteína!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⌨️  ATALHOS
  F1 — Abrir este manual
"""

    def __init__(self, parent, cores: dict):
        super().__init__(parent)
        self.title("Manual de Uso — ProteinCost")
        self.geometry("600x680")
        self.configure(fg_color=cores["fundo_escuro"])
        self.resizable(False, False)

        # Cabeçalho
        ctk.CTkLabel(
            self,
            text="📖  Manual de Uso",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=cores["verde_claro"],
            fg_color=cores["verde_escuro"],
            corner_radius=10,
            height=48,
        ).pack(fill="x", padx=16, pady=(16, 8))

        # Área de texto com scroll
        texto = ctk.CTkTextbox(
            self,
            fg_color=cores["fundo_card"],
            text_color=cores["texto_claro"],
            font=ctk.CTkFont(family="Courier New", size=12),
            corner_radius=10,
            scrollbar_button_color=cores["verde_escuro"],
        )
        texto.pack(fill="both", expand=True, padx=16, pady=8)
        texto.insert("1.0", self.CONTEUDO)
        texto.configure(state="disabled")

        ctk.CTkButton(
            self,
            text="Fechar",
            height=40,
            fg_color=cores["verde_escuro"],
            hover_color=cores["verde_medio"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.destroy,
        ).pack(pady=(0, 16), padx=16, fill="x")


# ==============================================================================
# PONTO DE ENTRADA
# ==============================================================================
if __name__ == "__main__":
    app = ProteinCostApp()
    app.mainloop()
