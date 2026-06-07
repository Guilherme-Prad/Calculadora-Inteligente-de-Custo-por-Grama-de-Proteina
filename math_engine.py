"""
==================================================
math_engine.py — Módulo de Matemática Computacional
==================================================
Contém todas as funções matemáticas do sistema ProteinCost.

CONCEITOS APLICADOS:
- Funções matemáticas puras (sem efeitos colaterais)
- Lógica booleana nas validações
- Estruturas de dados (listas, dicionários, tuplas)
- Algoritmo de ordenação
- Estatística descritiva (média aritmética)
==================================================
"""


# ==============================================================================
# FUNÇÕES MATEMÁTICAS PRINCIPAIS
# ==============================================================================

def calcular_proteina_total(proteina_por_100g: float, peso_total: float) -> float:
    """
    Calcula a quantidade total de proteína em gramas.

    FÓRMULA MATEMÁTICA:
        proteina_total = (proteina_por_100g × peso_total) / 100

    Esta é uma REGRA DE TRÊS simples:
        Se em 100g há X gramas de proteína,
        em peso_total gramas haverá (X × peso_total) / 100 gramas.

    Parâmetros:
        proteina_por_100g (float): gramas de proteína a cada 100g do alimento
        peso_total (float): peso total do alimento em gramas

    Retorna:
        float: total de proteína em gramas

    Exemplo:
        >>> calcular_proteina_total(25.0, 500.0)
        125.0  # (25 × 500) / 100 = 125g de proteína
    """
    # LÓGICA BOOLEANA: garantia de que os valores são positivos
    if proteina_por_100g <= 0 or peso_total <= 0:
        return 0.0

    # CÁLCULO: regra de três — proporção linear
    return (proteina_por_100g * peso_total) / 100


def calcular_custo_por_grama(preco: float, proteina_total: float) -> float:
    """
    Calcula o custo em reais por grama de proteína.

    FÓRMULA MATEMÁTICA:
        custo_por_grama = preço / proteina_total

    Esta é uma RAZÃO (divisão de duas grandezas):
        Quanto custa cada grama de proteína do alimento.
    Quanto menor o resultado, mais eficiente economicamente o alimento é.

    Parâmetros:
        preco (float): preço total pago pelo alimento (R$)
        proteina_total (float): total de proteína em gramas

    Retorna:
        float: custo em R$ por grama de proteína

    Exemplo:
        >>> calcular_custo_por_grama(8.50, 125.0)
        0.068  # R$0,068 por grama de proteína
    """
    # LÓGICA BOOLEANA: prevenção de divisão por zero
    if proteina_total == 0:
        raise ValueError("Proteína total não pode ser zero (divisão por zero).")

    if preco < 0:
        raise ValueError("Preço não pode ser negativo.")

    # CÁLCULO: razão — custo unitário por grama de proteína
    return preco / proteina_total


def calcular_media_custo(alimentos: list) -> float:
    """
    Calcula a média aritmética do custo por grama entre todos os alimentos.

    FÓRMULA MATEMÁTICA (ESTATÍSTICA DESCRITIVA):
        média = Σ(custo_por_grama_i) / n

    Onde:
        Σ = somatório de todos os valores
        n = número de alimentos

    Parâmetros:
        alimentos (list): lista de dicionários com dados dos alimentos

    Retorna:
        float: média do custo por grama, ou 0.0 se lista vazia

    Exemplo:
        >>> alimentos = [{"custo_por_grama": 0.068}, {"custo_por_grama": 0.133}]
        >>> calcular_media_custo(alimentos)
        0.1005
    """
    # LÓGICA BOOLEANA: evitar divisão por zero com lista vazia
    if not alimentos:
        return 0.0

    # SOMATÓRIO: extrai todos os custos em uma lista (list comprehension)
    custos = [a["custo_por_grama"] for a in alimentos]

    # MÉDIA ARITMÉTICA: soma dividida pela quantidade
    return sum(custos) / len(custos)


def ordenar_por_custo(alimentos: list) -> list:
    """
    Ordena os alimentos do menor para o maior custo por grama de proteína.

    ALGORITMO DE ORDENAÇÃO:
        Utiliza o algoritmo Timsort (interno ao Python via sorted()),
        com complexidade O(n log n) no pior caso.

    A função sorted() recebe uma key (função de comparação):
        key = lambda a: a["custo_por_grama"]
    Isso instrui o algoritmo a comparar os dicionários pelo campo numérico.

    Parâmetros:
        alimentos (list): lista de dicionários dos alimentos

    Retorna:
        list: nova lista ordenada (não modifica a original — imutabilidade)

    Exemplo:
        >>> ordenar_por_custo([{"custo_por_grama": 0.133}, {"custo_por_grama": 0.068}])
        [{"custo_por_grama": 0.068}, {"custo_por_grama": 0.133}]
    """
    # LÓGICA BOOLEANA: verificar se a lista possui elementos
    if not alimentos:
        return []

    # ORDENAÇÃO: sorted() retorna nova lista sem modificar a original
    # key: função lambda que extrai o valor de comparação (custo_por_grama)
    # reverse=False: ordem crescente (menor custo = melhor)
    return sorted(alimentos, key=lambda a: a["custo_por_grama"])


def calcular_economia_percentual(custo_melhor: float, custo_pior: float) -> float:
    """
    Calcula o percentual de economia do melhor alimento em relação ao pior.

    FÓRMULA MATEMÁTICA (VARIAÇÃO PERCENTUAL):
        economia% = ((custo_pior - custo_melhor) / custo_pior) × 100

    Parâmetros:
        custo_melhor (float): menor custo por grama
        custo_pior (float): maior custo por grama

    Retorna:
        float: percentual de economia (0 a 100)
    """
    # LÓGICA BOOLEANA: prevenir divisão por zero
    if custo_pior == 0:
        return 0.0

    if custo_melhor >= custo_pior:
        return 0.0

    # CÁLCULO: variação percentual relativa
    return ((custo_pior - custo_melhor) / custo_pior) * 100


def vetor_alimento(alimento: dict) -> tuple:
    """
    Representa um alimento como vetor numérico (ÁLGEBRA LINEAR).

    ÁLGEBRA LINEAR:
        Um alimento pode ser representado como um vetor no espaço R³:
        v = (preço, proteína_total, custo_por_grama)

    Isso permite operações vetoriais para análise comparativa.

    Parâmetros:
        alimento (dict): dicionário com dados do alimento

    Retorna:
        tuple: vetor (preço, proteína_total, custo_por_grama)
    """
    return (
        alimento["preco"],
        alimento["proteina_total"],
        alimento["custo_por_grama"],
    )


# ==============================================================================
# FUNÇÕES AUXILIARES DE FORMATAÇÃO
# ==============================================================================

def formatar_moeda(valor: float) -> str:
    """
    Formata um valor float como moeda brasileira.

    Parâmetros:
        valor (float): valor numérico

    Retorna:
        str: string formatada ex. "R$ 0,068"
    """
    return f"R$ {valor:.3f}".replace(".", ",")


def formatar_grama(valor: float) -> str:
    """
    Formata um valor float como massa em gramas.

    Parâmetros:
        valor (float): valor em gramas

    Retorna:
        str: string formatada ex. "125,0g"
    """
    return f"{valor:.1f}g".replace(".", ",")


def formatar_percentual(valor: float) -> str:
    """
    Formata um valor float como percentual.

    Parâmetros:
        valor (float): valor percentual

    Retorna:
        str: string formatada ex. "48,9%"
    """
    return f"{valor:.1f}%".replace(".", ",")
