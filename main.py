"""
==================================================
ProteinCost — Calculadora Inteligente de Custo por Grama de Proteína
==================================================
"""

import customtkinter as ctk
from tkinter import messagebox

from math_engine import (
    calcular_proteina_total,
    calcular_custo_por_grama,
    calcular_media_custo,
    ordenar_por_custo,
    formatar_moeda,
    formatar_grama,
)
from ui_components import (
    TabelaAlimentos,
    PainelRanking,
    FormularioEntrada,
    BarraStatus,
)

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")

# Paletas para Light e Dark
CORES_LIGHT = {
    "verde_escuro":  "#0E9422",
    "verde_medio":   "#4CAF50",
    "verde_claro":   "#76BA4E",
    "vermelho":      "#FF6467",
    "branco":        "#FFFFFF",
    "cinza_suave":   "#90A4AE",
    "cinza":         "#212121",
    "preto":         "#000000",
    "bg_principal":  "#FFFFFF",
    "bg_painel":     "#76BA4E",
}

CORES_DARK = {
    "verde_escuro": "#0E9422",
    "verde_medio":  "#4CAF50",
    "verde_claro":  "#66A23F",
    "vermelho":     "#FF6467",
    "branco":       "#F0F0F0",
    "cinza_suave":  "#78909C",
    "cinza":        "#FFFFFF",
    "preto":        "#121212",
    "bg_principal": "#1E1E1E",
    "bg_painel":    "#2C3E2F",
}

class JanelaManual(ctk.CTkToplevel):
    CONTEUDO = """📌 COMO USAR O PROTEINCOST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CADASTRAR UM ALIMENTO
   • Preencha os campos e clique em "➕ Adicionar"

2. CALCULAR O RANKING
   • Clique em "⚡ Calcular Ranking"

3. INTERPRETAR OS RESULTADOS
   • Menor R$/g prot. = melhor custo

4. REMOVER / LIMPAR
   • Use os botões correspondentes"""

    def __init__(self, parent, cores):
        super().__init__(parent)
        self.title("Manual — ProteinCost")
        self.geometry("620x620")
        self.configure(fg_color=cores["preto"])

        ctk.CTkLabel(self, text="📖 Manual de Uso", font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=cores["branco"], fg_color=cores["verde_escuro"],
                     corner_radius=10, height=48).pack(fill="x", padx=16, pady=(16,8))

        texto = ctk.CTkTextbox(self, fg_color=cores["bg_painel"], text_color=cores.get("branco"), font=ctk.CTkFont(size=12))
        texto.pack(fill="both", expand=True, padx=16, pady=8)
        texto.insert("1.0", self.CONTEUDO)
        texto.configure(state="disabled")

        ctk.CTkButton(self, text="Fechar", height=40, fg_color=cores["verde_escuro"],
                      command=self.destroy).pack(pady=(0,16), padx=16, fill="x")


class ProteinCostApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ProteinCost — Calculadora de Custo Proteico")
        self.geometry("1200x800")
        self.minsize(1000, 700)

        self.alimentos: list[dict] = []
        self.cores = CORES_LIGHT.copy()   # Inicia com Light

        self._construir_interface()
        self.bind("<F1>", lambda e: self._abrir_manual())

    def _atualizar_cores(self):
        """Atualiza cores dos painéis ao trocar tema"""
        modo = ctk.get_appearance_mode()
        self.cores = CORES_DARK.copy() if modo == "Dark" else CORES_LIGHT.copy()

        self.configure(fg_color=self.cores["bg_principal"])

        if hasattr(self, 'painel_esquerdo'):
            self.painel_esquerdo.configure(fg_color=self.cores["bg_painel"])
        if hasattr(self, 'painel_direito'):
            self.painel_direito.configure(fg_color=self.cores["bg_painel"])
        if hasattr(self, 'frame_stats'):
            self.frame_stats.configure(fg_color=self.cores["verde_escuro"])

    def _construir_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self._criar_cabecalho()
        self._atualizar_cores()

        self.painel_esquerdo = ctk.CTkFrame(self, fg_color=self.cores["bg_painel"], corner_radius=16)
        self.painel_esquerdo.grid(row=1, column=0, padx=(16,8), pady=8, sticky="nsew")
        self.painel_esquerdo.grid_rowconfigure(1, weight=1)
        self.painel_esquerdo.grid_columnconfigure(0, weight=1)

        self.painel_direito = ctk.CTkFrame(self, fg_color=self.cores["bg_painel"], corner_radius=16)
        self.painel_direito.grid(row=1, column=1, padx=(8,16), pady=8, sticky="nsew")
        self.painel_direito.grid_rowconfigure(0, weight=3)
        self.painel_direito.grid_rowconfigure(1, weight=1)
        self.painel_direito.grid_columnconfigure(0, weight=1)

        self.formulario = FormularioEntrada(self.painel_esquerdo, cores=self.cores, callback_adicionar=self._adicionar_alimento)
        self.formulario.grid(row=0, column=0, padx=16, pady=(16,8), sticky="ew")

        self._criar_botoes_acao()

        self.tabela = TabelaAlimentos(self.painel_direito, cores=self.cores, callback_remover=self._remover_alimento)
        self.tabela.grid(row=0, column=0, padx=16, pady=(16,8), sticky="nsew")

        self.painel_ranking = PainelRanking(self.painel_direito, cores=self.cores)
        self.painel_ranking.grid(row=1, column=0, padx=16, pady=(8,16), sticky="nsew")

        self.barra_status = BarraStatus(self, cores=self.cores)
        self.barra_status.grid(row=2, column=0, columnspan=2, padx=16, pady=(0,8), sticky="ew")

    def _criar_cabecalho(self):
        frame_header = ctk.CTkFrame(self, fg_color=self.cores["verde_escuro"], corner_radius=12, height=72)
        frame_header.grid(row=0, column=0, columnspan=2, padx=16, pady=(16,0), sticky="ew")
        frame_header.grid_propagate(False)
        frame_header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame_header, text="🥩", font=ctk.CTkFont(size=32), text_color=self.cores["branco"]).grid(row=0, column=0, padx=(20,8), pady=12)

        frame_titulos = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_titulos.grid(row=0, column=1, sticky="w", pady=8)
        ctk.CTkLabel(frame_titulos, text="ProteinCost", font=ctk.CTkFont(size=22, weight="bold"), text_color=self.cores["branco"]).pack(anchor="w")
        ctk.CTkLabel(frame_titulos, text="Calculadora de Custo por Grama de Proteína", font=ctk.CTkFont(size=11), text_color=self.cores["branco"]).pack(anchor="w")

        frame_btns = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_btns.grid(row=0, column=2, padx=16, pady=12)

        ctk.CTkButton(
            frame_btns, text="Manual (F1)", width=110, height=27,
            fg_color=self.cores["verde_medio"], command=self._abrir_manual).pack()

        self.btn_tema = ctk.CTkButton(
            frame_btns, text="🌙 Modo Escuro", width=110, height=27,
            fg_color=self.cores["verde_medio"], command=self._alternar_tema
        )
        self.btn_tema.pack(pady=(1,0))

    def _criar_botoes_acao(self):
        frame_botoes = ctk.CTkFrame(self.painel_esquerdo, fg_color="transparent")
        frame_botoes.grid(row=1, column=0, padx=16, pady=8, sticky="nsew")
        frame_botoes.grid_columnconfigure((0,1), weight=1)

        ctk.CTkButton(frame_botoes, text="⚡ Calcular Ranking", height=44,
                      fg_color=self.cores["verde_escuro"], command=self._calcular_ranking).grid(row=0, column=0, columnspan=2, sticky="ew", pady=4)

        ctk.CTkButton(frame_botoes, text="🗑 Remover", height=38, fg_color=self.cores["branco"], text_color=self.cores["preto"],
                      hover_color=self.cores["vermelho"], border_color=self.cores["branco"], border_width=1,
                      command=self._remover_alimento).grid(row=1, column=0, padx=(4,2), pady=4, sticky="ew")

        ctk.CTkButton(frame_botoes, text="🔄 Limpar Tudo", height=38, fg_color=self.cores["branco"], text_color=self.cores["preto"],
                      hover_color=self.cores["vermelho"], border_color=self.cores["branco"], border_width=1,
                      command=self._limpar_tudo).grid(row=1, column=1, padx=(2,4), pady=4, sticky="ew")

        self.frame_stats = ctk.CTkFrame(frame_botoes, fg_color=self.cores["verde_escuro"], corner_radius=10)
        self.frame_stats.grid(row=2, column=0, columnspan=2, padx=4, pady=(12,4), sticky="ew")

        ctk.CTkLabel(self.frame_stats, text="• Estatísticas", font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=self.cores["branco"]).pack(anchor="w", padx=12, pady=(8,2))

        self.label_total_alimentos = ctk.CTkLabel(self.frame_stats, text="Alimentos cadastrados: 0",
                                                  font=ctk.CTkFont(size=11), text_color=self.cores["branco"])
        self.label_total_alimentos.pack(anchor="w", padx=12, pady=2)

        self.label_media_custo = ctk.CTkLabel(self.frame_stats, text="Média de custo: —",
                                              font=ctk.CTkFont(size=11), text_color=self.cores["branco"])
        self.label_media_custo.pack(anchor="w", padx=12, pady=2)

        self.label_melhor = ctk.CTkLabel(self.frame_stats, text="Melhor custo-benefício: —",
                                         font=ctk.CTkFont(size=11), text_color=self.cores["branco"], wraplength=220)
        self.label_melhor.pack(anchor="w", padx=12, pady=(2,8))

    # ==================== LÓGICA (mantida igual) ====================
    def _adicionar_alimento(self, dados: dict):
        nome = dados.get("nome", "").strip()
        if not nome:
            self.barra_status.erro("⚠ Nome obrigatório.")
            return
        try:
            preco = float(dados["preco"])
            peso_total = float(dados["peso_total"])
            prot_100g = float(dados["proteina_por_100g"])
        except:
            self.barra_status.erro("⚠ Valores numéricos inválidos.")
            return

        if preco <= 0 or peso_total <= 0 or prot_100g <= 0 or prot_100g > 100:
            self.barra_status.erro("⚠ Valores devem ser positivos e válidos.")
            return

        proteina_total = calcular_proteina_total(prot_100g, peso_total)
        if proteina_total == 0:
            self.barra_status.erro("⚠ Proteína total inválida.")
            return

        custo_por_grama = calcular_custo_por_grama(preco, proteina_total)

        self.alimentos.append({
            "nome": nome, "preco": preco, "peso_total": peso_total,
            "proteina_por_100g": prot_100g, "proteina_total": proteina_total,
            "custo_por_grama": custo_por_grama
        })

        self.tabela.atualizar(self.alimentos)
        self._atualizar_stats()
        self.formulario.limpar()
        self.barra_status.sucesso(f"✅ '{nome}' adicionado")

    def _calcular_ranking(self):
        if not self.alimentos:
            self.barra_status.erro("Cadastre alimentos primeiro.")
            return
        ranking = ordenar_por_custo(self.alimentos)
        media = calcular_media_custo(self.alimentos)
        self.painel_ranking.atualizar(ranking, media)
        self.tabela.destacar_melhor(ranking[0]["nome"])
        self.barra_status.sucesso(f"🏆 Melhor: {ranking[0]['nome']}")
        self._atualizar_stats(ranking, media)

    def _remover_alimento(self, nome=None):
        if nome is None:
            nome = self.tabela.obter_selecionado()
        if not nome:
            self.barra_status.aviso("Selecione um alimento.")
            return
        if messagebox.askyesno("Remover", f"Remover '{nome}'?"):
            self.alimentos = [a for a in self.alimentos if a["nome"] != nome]
            self.tabela.atualizar(self.alimentos)
            self.painel_ranking.limpar()
            self._atualizar_stats()
            self.barra_status.sucesso(f"'{nome}' removido")

    def _limpar_tudo(self):
        if self.alimentos and messagebox.askyesno("Limpar", "Apagar todos?"):
            self.alimentos = []
            self.tabela.atualizar(self.alimentos)
            self.painel_ranking.limpar()
            self.formulario.limpar()
            self._atualizar_stats()
            self.barra_status.aviso("Dados apagados.")

    def _atualizar_stats(self, ranking=None, media=None):
        total = len(self.alimentos)
        self.label_total_alimentos.configure(text=f"Alimentos cadastrados: {total}")

        if self.alimentos:
            if media is None:
                media = sum(a["custo_por_grama"] for a in self.alimentos) / total
            self.label_media_custo.configure(text=f"Média: {formatar_moeda(media)}/g")
            if ranking:
                self.label_melhor.configure(text=f"🏆 {ranking[0]['nome']} ({formatar_moeda(ranking[0]['custo_por_grama'])}/g)")
        else:
            self.label_media_custo.configure(text="Média de custo: —")
            self.label_melhor.configure(text="Melhor custo-benefício: —")

    def _abrir_manual(self):
        JanelaManual(self, self.cores).grab_set()

    def _alternar_tema(self):
        if ctk.get_appearance_mode() == "Light":
            ctk.set_appearance_mode("dark")
            self.btn_tema.configure(text="☀️ Modo Claro")
        else:
            ctk.set_appearance_mode("light")
            self.btn_tema.configure(text="🌙 Modo Escuro")
        
        self._atualizar_cores()


if __name__ == "__main__":
    app = ProteinCostApp()
    app.mainloop()
