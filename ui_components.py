"""
==================================================
ui_components.py — Componentes Visuais do ProteinCost
==================================================
Define widgets reutilizáveis para a interface gráfica.

Componentes:
    - FormularioEntrada: campo de cadastro de alimentos
    - TabelaAlimentos: exibição dos alimentos com destaque
    - PainelRanking: ranking visual pós-cálculo
    - BarraStatus: mensagens de feedback ao usuário
==================================================
"""

import customtkinter as ctk
from math_engine import formatar_moeda, formatar_grama, calcular_economia_percentual
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk


# FORMULÁRIO DE ENTRADA
class FormularioEntrada(ctk.CTkFrame):
    """
    Formulário com os campos necessários para cadastrar um alimento.

    Campos:
        - Nome do alimento
        - Preço (R$)
        - Quantidade (g)
        - Proteína por 100g
    """

    def __init__(self, parent, cores: dict, callback_adicionar):
        super().__init__(parent, fg_color="transparent")
        self.cores = cores
        self.callback_adicionar = callback_adicionar

        self._construir_formulario()

    def _construir_formulario(self):
        """Monta os campos de entrada do formulário."""
        self.grid_columnconfigure(0, weight=1)

        # Título do formulário
        ctk.CTkLabel(
            self,
            text="➕  Cadastrar Alimento",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores["branco"],
            fg_color="transparent",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        # Definição dos campos: (label, atributo, placeholder, dica)
        campos = [
            ("Nome do Alimento",     "entry_nome",    "Ex: Frango grelhado",       None),
            ("Preço (R$)",           "entry_preco",   "Ex: 8,50",                  "Valor pago pelo produto"),
            ("Quantidade (gramas)",  "entry_peso",    "Ex: 500",                   "Peso total do produto"),
            ("Proteína por 100g",    "entry_prot",    "Ex: 25",                    "Ver na embalagem"),
        ]

        for idx, (label, attr, placeholder, dica) in enumerate(campos):
            linha = idx + 1

            # Label do campo
            ctk.CTkLabel(
                self,
                text=label,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.cores["branco"],
                fg_color="transparent",
            ).grid(row=linha, column=0, sticky="w", pady=(6, 0))

            # Campo de entrada
            entry = ctk.CTkEntry(
                self,
                placeholder_text=placeholder,
                height=36,
                fg_color=self.cores["branco"],
                border_color=self.cores["cinza_suave"],
                text_color=self.cores["preto"],
                placeholder_text_color=self.cores["cinza_suave"],
                font=ctk.CTkFont(size=12),
                corner_radius=8,
            )
            entry.grid(row=linha, column=0, columnspan=2, sticky="ew", pady=(2, 0))
            setattr(self, attr, entry)

            # Dica opcional abaixo do campo
            if dica:
                ctk.CTkLabel(
                    self,
                    text=f"  ℹ {dica}",
                    font=ctk.CTkFont(size=10),
                    text_color=self.cores["cinza_suave"],
                    fg_color="transparent",
                ).grid(row=linha + 10, column=0, sticky="w")  # offset para não colidir

        # Ajustar linhas das dicas manualmente (reorganizar grid)
        for widget in self.winfo_children():
            widget.grid_remove()

        self._grid_campos_com_dicas()

    def _grid_campos_com_dicas(self):
        """Reconstrói o grid dos campos de forma organizada."""
        self.grid_columnconfigure(0, weight=1)

        # Título
        ctk.CTkLabel(
            self,
            text="➕  Cadastrar Alimento",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.cores["branco"],
            fg_color="transparent",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Campos organizados
        campos_info = [
            ("Nome do Alimento",     "entry_nome",  "Ex: Frango grelhado"),
            ("Preço total (R$)",     "entry_preco", "Ex: 8.50  →  valor pago pelo produto"),
            ("Quantidade (gramas)",  "entry_peso",  "Ex: 500  →  peso total comprado"),
            ("Proteína por 100g (g)", "entry_prot", "Ex: 25.0  →  consultar embalagem"),
        ]

        for i, (label_txt, attr, placeholder) in enumerate(campos_info):
            row_base = 1 + (i * 2)

            ctk.CTkLabel(
                self,
                text=label_txt,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.cores["branco"],
                fg_color="transparent",
            ).grid(row=row_base, column=0, sticky="w", pady=(8, 0))

            entry = ctk.CTkEntry(
                self,
                placeholder_text=placeholder,
                height=38,
                fg_color=self.cores["branco"],
                border_color=self.cores["cinza_suave"],
                border_width=1,
                text_color=self.cores["preto"],
                placeholder_text_color=self.cores["cinza_suave"],
                font=ctk.CTkFont(size=12),
                corner_radius=8,
            )
            entry.grid(row=row_base + 1, column=0, sticky="ew", pady=(2, 0))
            setattr(self, attr, entry)

        # Botão
        ctk.CTkButton(
            self,
            text="➕  Adicionar Alimento",
            height=44,
            fg_color=self.cores["verde_escuro"],
            hover_color=self.cores["verde_medio"],
            text_color=self.cores["branco"],
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10,
            command=self._on_adicionar,
        ).grid(row=99, column=0, sticky="ew", pady=(16, 4))

    def _on_adicionar(self):
        """Coleta os dados dos campos e chama o callback."""
        dados = {
            "nome":             self.entry_nome.get(),
            "preco":            self.entry_preco.get().replace(",", "."),
            "peso_total":       self.entry_peso.get().replace(",", "."),
            "proteina_por_100g": self.entry_prot.get().replace(",", "."),
        }
        self.callback_adicionar(dados)

    def limpar(self):
        """Limpa todos os campos do formulário."""
        for attr in ("entry_nome", "entry_preco", "entry_peso", "entry_prot"):
            entry = getattr(self, attr, None)
            if entry:
                entry.delete(0, "end")
        self.entry_nome.focus()


# TABELA DE ALIMENTOS
class TabelaAlimentos(ctk.CTkFrame):
    """
    Tabela visual para exibição dos alimentos cadastrados.
    Permite seleção de linha e destaque do melhor alimento.
    """

    COLUNAS = [
        ("nome",             "Alimento",      180),
        ("preco",            "Preço (R$)",     90),
        ("peso_total",       "Qtd (g)",        80),
        ("proteina_por_100g","Prot/100g",       80),
        ("proteina_total",   "Prot. Total",     90),
        ("custo_por_grama",  "R$/g prot.",      90),
    ]

    def __init__(self, parent, cores: dict, callback_remover):
        super().__init__(parent, fg_color="transparent")
        self.cores = cores
        self.callback_remover = callback_remover
        self._melhor_nome = None
        self._alimento_selecionado = None

        self._construir_tabela()

    def _construir_tabela(self):
        """Monta a tabela com estilo personalizado."""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título
        ctk.CTkLabel(
            self,
            text=">  Alimentos Cadastrados",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.cores["branco"],
            fg_color="transparent",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Frame para a tabela com scrollbar
        frame_tabela = ctk.CTkFrame(
            self,
            fg_color=self.cores["branco"],
            corner_radius=10,
        )
        frame_tabela.grid(row=1, column=0, sticky="nsew")
        frame_tabela.grid_rowconfigure(0, weight=1)
        frame_tabela.grid_columnconfigure(0, weight=1)

        # Estilo da tabela (ttk.Treeview)
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "ProteinCost.Treeview",
            background=self.cores.get("branco", "#FFFFFF"),
            fieldbackground=self.cores.get("branco", "#FFFFFF"),
            foreground=self.cores.get("preto", "#000000"),
            rowheight=30,
            font=("Helvetica", 11),
            borderwidth=0,
        )
        style.configure(
            "ProteinCost.Treeview.Heading",
            background=self.cores.get("verde_escuro", "#0E9422"),
            foreground=self.cores.get("branco", "#FFFFFF"),
            font=("Helvetica", 11, "bold"),
            relief="flat",
            padding=6,
        )
        style.map(
            "ProteinCost.Treeview",
            background=[("selected", self.cores.get("verde_medio", "#4CAF50"))],
            foreground=[("selected", self.cores.get("branco", "#FFFFFF"))],
        )
        style.map(
            "ProteinCost.Treeview.Heading",
            background=[("active", self.cores.get("verde_medio", "#4CAF50"))],
        )

        # Cria o Treeview
        cols = [c[0] for c in self.COLUNAS]
        self.tree = ttk.Treeview(
            frame_tabela,
            columns=cols,
            show="headings",
            style="ProteinCost.Treeview",
            selectmode="browse",
        )

        # Configura colunas e cabeçalhos
        for col_id, col_label, col_width in self.COLUNAS:
            self.tree.heading(col_id, text=col_label)
            self.tree.column(col_id, width=col_width, anchor="center", minwidth=60)

        # Tag para destaque do melhor alimento
        self.tree.tag_configure(
            "melhor",
            background=self.cores.get("verde_claro", "#76BA4E"),
            foreground=self.cores.get("branco", "#FFFFFF"),
        )
        self.tree.tag_configure(
            "normal",
            background=self.cores.get("fundo_claro", self.cores.get("branco")),
            foreground=self.cores.get("preto"),
        )

        # Scrollbar vertical
        scrollbar = ctk.CTkScrollbar(
            frame_tabela,
            orientation="vertical", 
            command=self.tree.yview,
            button_color=self.cores["verde_escuro"],
            button_hover_color=self.cores["verde_medio"],
            corner_radius=99
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(4, 8), pady=10)

        # Evento de seleção
        self.tree.bind("<<TreeviewSelect>>", self._on_selecionar)

    def atualizar(self, alimentos: list):
        """
        Atualiza a tabela com a lista de alimentos.

        ESTRUTURA DE DADOS: itera sobre lista de dicionários
        """
        # Limpa todos os itens existentes
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insere os novos alimentos
        for alimento in alimentos:
            tag = "melhor" if alimento["nome"] == self._melhor_nome else "normal"
            valores = (
                alimento["nome"],
                f"R$ {alimento['preco']:.2f}",
                f"{alimento['peso_total']:.0f}g",
                f"{alimento['proteina_por_100g']:.1f}g",
                formatar_grama(alimento["proteina_total"]),
                formatar_moeda(alimento["custo_por_grama"]),
            )
            self.tree.insert("", "end", values=valores, tags=(tag,))

    def destacar_melhor(self, nome: str):
        """Marca visualmente o alimento de melhor custo-benefício."""
        self._melhor_nome = nome
        # Re-aplica tags para todos os itens
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            tag = "melhor" if vals[0] == nome else "normal"
            self.tree.item(item, tags=(tag,))

    def obter_selecionado(self) -> str | None:
        """Retorna o nome do alimento selecionado na tabela."""
        sel = self.tree.selection()
        if sel:
            return self.tree.item(sel[0], "values")[0]
        return None

    def _on_selecionar(self, event):
        """Callback de seleção de linha."""
        self._alimento_selecionado = self.obter_selecionado()


# PAINEL DE RANKING
class PainelRanking(ctk.CTkFrame):
    """
    Exibe o ranking dos alimentos ordenados do melhor ao pior custo por proteína.
    """

    MEDALHAS = [
        ("🥇", "military_tech"),
        ("🥈", "military_tech"),
        ("🥉", "military_tech"),
    ]

    def __init__(self, parent, cores: dict):
        super().__init__(parent, fg_color=cores["branco"], corner_radius=12)
        self.cores = cores
        self._construir_painel()

    def _construir_painel(self):
        """Monta a estrutura base do painel."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Cabeçalho
        frame_header = ctk.CTkFrame(self, fg_color=self.cores["verde_escuro"], corner_radius=8)
        frame_header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        frame_header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame_header,
            text="•  Ranking de Custo-Benefício",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.cores["branco"],
            fg_color="transparent",
        ).grid(row=0, column=0, padx=12, pady=6, sticky="w")

        self.label_media = ctk.CTkLabel(
            frame_header,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=self.cores["branco"],
            fg_color="transparent",
        )
        self.label_media.grid(row=0, column=1, padx=12, pady=6, sticky="e")

        # Área scrollável do ranking
        self.scroll_ranking = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=self.cores["verde_escuro"],
            height=120,
        )
        self.scroll_ranking.grid(row=1, column=0, sticky="nsew", padx=8, pady=(4, 8))
        self.scroll_ranking.grid_columnconfigure(0, weight=1)

        # Mensagem inicial
        self.label_vazio = ctk.CTkLabel(
            self.scroll_ranking,
            text="⚡  Clique em 'Calcular Ranking' para ver os resultados",
            font=ctk.CTkFont(size=11),
            text_color=self.cores["cinza_suave"],
            fg_color="transparent",
        )
        self.label_vazio.grid(row=0, column=0, pady=20)

    def atualizar(self, ranking: list, media: float):
        """
        Atualiza o ranking com os alimentos ordenados.

        MATEMÁTICA: utiliza posição na lista (índice) como posição no ranking
        """
        # Limpar conteúdo anterior
        for widget in self.scroll_ranking.winfo_children():
            widget.destroy()

        # Atualiza a média
        from math_engine import formatar_moeda
        self.label_media.configure(
            text=f"Média: {formatar_moeda(media)}/g",
            text_color=self.cores["branco"]
        )

        # Calcula economia percentual em relação ao mais caro
        # LÓGICA BOOLEANA: verifica se há mais de um alimento
        custo_pior = ranking[-1]["custo_por_grama"] if len(ranking) > 1 else 0

        # Cria uma linha para cada alimento no ranking
        for pos, alimento in enumerate(ranking):
            self._criar_linha_ranking(pos, alimento, custo_pior)

    def _criar_linha_ranking(self, posicao: int, alimento: dict, custo_pior: float):
        from math_engine import formatar_moeda, calcular_economia_percentual

        bg_color = self.cores["verde_medio"]
        borda = self.cores["branco"]

        frame = ctk.CTkFrame(
            self.scroll_ranking,
            fg_color=bg_color,
            corner_radius=8,
            border_width=1,
            border_color=borda,
        )
        frame.grid(
            row=posicao, column=0,
            sticky="ew", pady=3, padx=4
        )
        frame.grid_columnconfigure(2, weight=1)

        # Posição
        if posicao < len(self.MEDALHAS):
            emoji_fallback, icon_name = self.MEDALHAS[posicao]
        else:
            emoji_fallback, icon_name = (f"{posicao+1}", None)

        try:
            families = tkfont.families()
        except Exception:
            families = []

        use_material = "Material Symbols Outlined" in families and icon_name is not None

        if use_material:
            medal_text = icon_name
            medal_font = ctk.CTkFont(family="Material Symbols Outlined", size=16)
        else:
            medal_text = emoji_fallback
            medal_font = ctk.CTkFont(size=16)

        medal_colors = {0: "#FFD700", 1: "#C0C0C0", 2: "#CD7F32"}
        medal_color = medal_colors.get(posicao, self.cores.get("texto_claro", self.cores.get("branco", "#FFFFFF")))

        ctk.CTkLabel(
            frame,
            text=medal_text,
            font=medal_font,
            text_color=medal_color,
            fg_color="transparent",
            width=36,
        ).grid(row=0, column=0, padx=(8, 4), pady=6)

        # Nome do alimento
        ctk.CTkLabel(
            frame,
            text=alimento["nome"],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.cores.get("branco", "#FFFFFF"),
            fg_color="transparent",
        ).grid(row=0, column=1, sticky="w", padx=4)

        # Custo por grama
        ctk.CTkLabel(
            frame,
            text=f"{formatar_moeda(alimento['custo_por_grama'])}/g",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.cores["branco"],
            fg_color="transparent",
        ).grid(row=0, column=2, sticky="e", padx=8)

        # Economia percentual para o 1º lugar
        if posicao == 0 and custo_pior > 0:
            economia = calcular_economia_percentual(
                alimento["custo_por_grama"], custo_pior
            )
            if economia > 0:
                ctk.CTkLabel(
                    frame,
                    text=f"💚 {economia:.1f}% mais barato",
                    font=ctk.CTkFont(size=12),
                    text_color=self.cores["branco"],
                    fg_color="transparent",
                ).grid(row=0, column=3, padx=(4, 12))

    def limpar(self):
        """Limpa o painel de ranking."""
        for widget in self.scroll_ranking.winfo_children():
            widget.destroy()

        self.label_vazio = ctk.CTkLabel(
            self.scroll_ranking,
            text="⚡  Clique em 'Calcular Ranking' para ver os resultados",
            font=ctk.CTkFont(size=11),
            text_color=self.cores["cinza_suave"],
            fg_color="transparent",
        )
        self.label_vazio.grid(row=0, column=0, pady=20)
        self.label_media.configure(text="")


# BARRA DE STATUS
class BarraStatus(ctk.CTkFrame):
    """
    Barra inferior de mensagens de feedback para o usuário.
    Exibe mensagens de sucesso, erro e aviso com cores distintas.
    """

    def __init__(self, parent, cores: dict):
        super().__init__(
            parent,
            fg_color=cores["branco"],
            corner_radius=8,
            height=36,
        )
        self.cores = cores
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.label_msg = ctk.CTkLabel(
            self,
            text="ℹ  Bem-vindo ao ProteinCost! Cadastre alimentos e calcule o ranking.",
            font=ctk.CTkFont(size=12),
            text_color=cores["preto"],
            fg_color="transparent",
            anchor="w",
        )
        self.label_msg.grid(row=1, column=0, sticky="ew", padx=12, pady=6)

    def sucesso(self, mensagem: str):
        """Exibe uma mensagem de sucesso (verde)."""
        self.label_msg.configure(
            text=mensagem,
            text_color=self.cores["branco"],
        )

    def erro(self, mensagem: str):
        """Exibe uma mensagem de erro (vermelho)."""
        self.label_msg.configure(
            text=mensagem,
            text_color=self.cores["vermelho"],
        )

    def aviso(self, mensagem: str):
        """Exibe uma mensagem de aviso (branco)."""
        self.label_msg.configure(
            text=mensagem,
            text_color=self.cores["branco"],
        )
