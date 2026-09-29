"""Exporta as tabelas usadas no dashboard de Power BI.

Lê o modelo dimensional do projeto olist-sql e as previsões do projeto
olist-previsao-atraso e grava:

    dados/*.csv                       tabelas para importar no Power BI
    docs/consultas_power_query.md     consulta M de cada tabela, com os tipos de coluna
    docs/valores_de_conferencia.md    totais para conferir se as medidas DAX estão certas

Uso:
    python exportar_dados.py
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
BANCO_DW = RAIZ.parent / "olist-sql" / "olist_dw.db"
PREVISOES = RAIZ.parent / "olist-previsao-atraso" / "saida" / "previsao_atraso.csv"
PASTA_DADOS = RAIZ / "dados"
PASTA_DOCS = RAIZ / "docs"

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def ler(con, sql):
    return pd.read_sql(sql, con)


def montar_tabelas():
    for caminho in (BANCO_DW, PREVISOES):
        if not caminho.exists():
            raise SystemExit(f"Arquivo nao encontrado: {caminho}\n"
                             "Rode antes os projetos olist-sql e olist-previsao-atraso.")

    with sqlite3.connect(BANCO_DW) as con:
        dim_data = ler(con, "SELECT * FROM dim_data")
        dim_cliente = ler(con, "SELECT * FROM dim_cliente")
        dim_vendedor = ler(con, "SELECT * FROM dim_vendedor")
        dim_produto = ler(con, "SELECT * FROM dim_produto")
        pedidos = ler(con, "SELECT * FROM fato_pedidos")
        itens = ler(con, "SELECT pedido_id, item_seq, vendedor_id, produto_id, preco, frete FROM fato_itens")

    # dim_data: nome do mês em português e número do mês para ordenar.
    dim_data["mes_nome"] = dim_data["mes"].map(lambda m: MESES[m - 1])
    dim_data = dim_data[["data_id", "data", "ano", "mes", "mes_nome", "ano_mes",
                         "trimestre", "dia_semana_num", "dia_semana"]]

    # fato_pedidos: traz o cliente único (a pessoa) e classifica o atraso em faixas.
    pedidos = pedidos.merge(dim_cliente[["cliente_id", "cliente_unico_id"]], on="cliente_id", how="left")
    atraso = pedidos["dias_atraso"]
    pedidos["ordem_faixa_atraso"] = np.select(
        [atraso.isna(), atraso == 0, atraso <= 3, atraso <= 7], [pd.NA, 1, 2, 3], default=4)
    pedidos["faixa_atraso"] = pd.Series(pedidos["ordem_faixa_atraso"]).map(
        {1: "No prazo", 2: "1 a 3 dias", 3: "4 a 7 dias", 4: "Mais de 7 dias"})
    pedidos = pedidos[["pedido_id", "cliente_id", "cliente_unico_id", "status", "data_compra_id",
                       "hora_compra", "qtd_itens", "valor_itens", "valor_frete", "valor_pago",
                       "parcelas", "nota_media", "dias_entrega", "dias_atraso", "entregue_no_prazo",
                       "faixa_atraso", "ordem_faixa_atraso"]]
    for coluna in ("qtd_itens", "parcelas", "entregue_no_prazo", "ordem_faixa_atraso"):
        pedidos[coluna] = pd.to_numeric(pedidos[coluna]).astype("Int64")

    # previsao_atraso: faixas de risco definidas pelos percentuais das próprias previsões
    # de validação (50% menores = baixo, 50% a 80% = médio, 20% maiores = alto).
    prev = pd.read_csv(PREVISOES)
    validacao = prev.loc[prev["origem"] == "validacao_temporal", "risco_atraso"]
    corte_medio, corte_alto = validacao.quantile(0.5), validacao.quantile(0.8)
    prev["faixa_risco"] = np.select(
        [prev["risco_atraso"] >= corte_alto, prev["risco_atraso"] >= corte_medio],
        ["Alto", "Médio"], default="Baixo")
    prev["ordem_faixa_risco"] = prev["faixa_risco"].map({"Baixo": 1, "Médio": 2, "Alto": 3})
    prev["origem"] = prev["origem"].map({"validacao_temporal": "Validação temporal",
                                         "em_andamento": "Em andamento"})
    prev["data_compra"] = pd.to_datetime(prev["order_purchase_timestamp"]).dt.strftime("%Y-%m-%d")
    prev["atrasou_real"] = prev["atrasado"].astype("Int64")
    prev = prev.rename(columns={"order_id": "pedido_id"})[
        ["pedido_id", "origem", "risco_atraso", "faixa_risco", "ordem_faixa_risco",
         "data_compra", "atrasou_real"]]

    tabelas = {
        "dim_data": dim_data, "dim_cliente": dim_cliente, "dim_vendedor": dim_vendedor,
        "dim_produto": dim_produto, "fato_pedidos": pedidos, "fato_itens": itens,
        "previsao_atraso": prev,
    }
    return tabelas, corte_medio, corte_alto


def tipo_m(serie, nome):
    if nome in ("data", "data_compra"):
        return "type date"
    if pd.api.types.is_integer_dtype(serie):
        return "Int64.Type"
    if pd.api.types.is_float_dtype(serie):
        return "type number"
    return "type text"


def escrever_consultas_m(tabelas):
    partes = ["# Consultas do Power Query\n",
              "Cada bloco abaixo é a consulta de uma tabela. Antes, crie um parâmetro de texto chamado "
              "`PastaDados` com o caminho da pasta `dados` (por exemplo `C:\\projetos\\olist-dashboard\\dados\\`, "
              "com a barra invertida no final).\n",
              "A conversão de tipos usa a cultura `en-US` porque os CSVs trazem o ponto como separador "
              "decimal. Sem isso, o Power BI em português lê `123.45` como `12345`.\n",
              "Para criar cada consulta: **Obter dados > Consulta em branco > Editor Avançado**, "
              "cole o código e dê à consulta o nome da tabela.\n"]
    for nome, tabela in tabelas.items():
        tipos = ", ".join(f'{{"{c}", {tipo_m(tabela[c], c)}}}' for c in tabela.columns)
        partes.append(f"## {nome}\n\n```\nlet\n"
                      f'    Origem = Csv.Document(File.Contents(PastaDados & "{nome}.csv"),\n'
                      f"        [Delimiter = \",\", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),\n"
                      f"    Cabecalho = Table.PromoteHeaders(Origem, [PromoteAllScalars = true]),\n"
                      f"    Tipos = Table.TransformColumnTypes(Cabecalho, {{{tipos}}}, \"en-US\")\n"
                      f"in\n    Tipos\n```\n")
    (PASTA_DOCS / "consultas_power_query.md").write_text("\n".join(partes), encoding="utf-8")


def escrever_conferencia(tabelas, corte_medio, corte_alto):
    p, i, prev = tabelas["fato_pedidos"], tabelas["fato_itens"], tabelas["previsao_atraso"]
    entregues = p[p["status"] == "delivered"]
    avaliados = entregues[entregues["entregue_no_prazo"].notna()]
    por_pessoa = entregues.groupby("cliente_unico_id")["pedido_id"].nunique()
    itens_entregues = i.merge(entregues[["pedido_id"]], on="pedido_id")
    categorias = itens_entregues.merge(tabelas["dim_produto"][["produto_id", "categoria"]], on="produto_id")
    top_cat = categorias.groupby("categoria")["preco"].sum().sort_values(ascending=False)
    andamento = prev[prev["origem"] == "Em andamento"]
    validacao = prev[prev["origem"] == "Validação temporal"]
    taxa_por_faixa = validacao.groupby("faixa_risco")["atrasou_real"].mean()

    linhas = [
        ("Pedidos entregues", f"{entregues['pedido_id'].nunique():,}"),
        ("Receita (itens de pedidos entregues)", f"R$ {entregues['valor_itens'].sum():,.2f}"),
        ("Frete (pedidos entregues)", f"R$ {entregues['valor_frete'].sum():,.2f}"),
        ("Ticket médio", f"R$ {entregues['valor_itens'].sum() / entregues['pedido_id'].nunique():,.2f}"),
        ("Receita de itens (pedidos entregues)", f"R$ {itens_entregues['preco'].sum():,.2f}"),
        ("Categoria com maior receita", f"{top_cat.index[0]} (R$ {top_cat.iloc[0]:,.2f})"),
        ("% entregue no prazo", f"{avaliados['entregue_no_prazo'].mean():.2%}"),
        ("Dias médios de entrega", f"{entregues['dias_entrega'].mean():.2f}"),
        ("Dias médios de atraso (só pedidos atrasados)",
         f"{avaliados.loc[avaliados['entregue_no_prazo'] == 0, 'dias_atraso'].mean():.2f}"),
        ("Nota média (média das notas por pedido)", f"{entregues['nota_media'].mean():.3f}"),
        ("Clientes únicos (pedidos entregues)", f"{por_pessoa.size:,}"),
        ("Clientes recorrentes (mais de 1 pedido)", f"{(por_pessoa > 1).sum():,}"),
        ("% de clientes recorrentes", f"{(por_pessoa > 1).mean():.2%}"),
        ("Previsões: pedidos em andamento", f"{len(andamento):,}"),
        ("Previsões: pedidos com validação temporal", f"{len(validacao):,}"),
        ("Corte da faixa de risco Médio", f"{corte_medio:.4f}"),
        ("Corte da faixa de risco Alto", f"{corte_alto:.4f}"),
        ("Pedidos em andamento com risco Alto", f"{(andamento['faixa_risco'] == 'Alto').sum():,}"),
        ("Taxa real de atraso na faixa Baixo", f"{taxa_por_faixa['Baixo']:.2%}"),
        ("Taxa real de atraso na faixa Médio", f"{taxa_por_faixa['Médio']:.2%}"),
        ("Taxa real de atraso na faixa Alto", f"{taxa_por_faixa['Alto']:.2%}"),
    ]
    texto = ["# Valores de conferência\n",
             "Totais calculados direto nos dados, sem passar pelo Power BI. Com as medidas DAX criadas "
             "e nenhum filtro aplicado, os cartões do dashboard devem mostrar os mesmos valores.\n",
             "| Indicador | Valor |", "|---|---|"]
    texto += [f"| {nome} | {valor} |" for nome, valor in linhas]
    (PASTA_DOCS / "valores_de_conferencia.md").write_text("\n".join(texto) + "\n", encoding="utf-8")


def main():
    PASTA_DADOS.mkdir(exist_ok=True)
    PASTA_DOCS.mkdir(exist_ok=True)
    tabelas, corte_medio, corte_alto = montar_tabelas()

    for nome, tabela in tabelas.items():
        tabela.to_csv(PASTA_DADOS / f"{nome}.csv", index=False, encoding="utf-8")
        print(f"  {nome:<16} {len(tabela):>8} linhas, {len(tabela.columns)} colunas")

    escrever_consultas_m(tabelas)
    escrever_conferencia(tabelas, corte_medio, corte_alto)
    print("\nConsultas M e valores de conferencia gravados em docs/")


if __name__ == "__main__":
    main()
