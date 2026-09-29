# olist-dashboard

Dashboard em Power BI sobre o dataset público de e-commerce da Olist, com quatro páginas: vendas, entrega, produtos e vendedores, e risco de atraso. É o último projeto de uma série que começa em um pipeline de carga em Java e passa por modelagem em SQL e por um modelo de previsão em Python.

| Projeto | O que faz |
|---|---|
| [olist-etl-java](https://github.com/dev-lucasluz/olist-etl-java) | Lê os CSVs, limpa e grava em um banco SQLite. |
| [olist-sql](https://github.com/dev-lucasluz/olist-sql) | Modelo dimensional e 13 consultas de negócio. |
| [olist-previsao-atraso](https://github.com/dev-lucasluz/olist-previsao-atraso) | Modelo que estima o risco de atraso de cada pedido. |
| **olist-dashboard** | Dashboard que junta tudo. |

## Páginas

1. **Visão geral:** receita, pedidos entregues, ticket médio, nota média, recorrência de clientes, evolução mensal e receita por estado.
2. **Entrega:** percentual entregue no prazo, tempo médio de entrega e de atraso, atraso por estado e por mês, e a relação entre atraso e nota de avaliação.
3. **Produtos e vendedores:** categorias que mais geram receita e os dez maiores vendedores, com nota e taxa de atraso.
4. **Risco de atraso:** pedidos em andamento ordenados pelo risco previsto pelo modelo, e a comparação entre o risco previsto e o atraso que de fato aconteceu.

O detalhe de cada visual está em [`docs/paginas.md`](docs/paginas.md).

## O que o dashboard mostra

- A receita mensal de pedidos entregues cresceu de cerca de R$ 112 mil em janeiro de 2017 para cerca de R$ 970 mil em maio de 2018, com pico em novembro de 2017.
- 93,2% dos pedidos chegaram no prazo. Quando o atraso passa de uma semana, a nota média de avaliação cai de 4,3 para menos de 2.
- Só 3% dos clientes compraram mais de uma vez.
- O modelo de risco ordena bem os pedidos: a taxa real de atraso é de 4,2% na faixa de risco baixo e de 15,7% na faixa alta.

## Modelo de dados e medidas

Esquema estrela com duas tabelas fato (pedidos e itens), quatro dimensões e a tabela de previsões. Os relacionamentos e as decisões estão em [`docs/modelo_de_dados.md`](docs/modelo_de_dados.md), e as medidas DAX, em [`docs/medidas_dax.md`](docs/medidas_dax.md).

Os totais de cada indicador, calculados fora do Power BI, estão em [`docs/valores_de_conferencia.md`](docs/valores_de_conferencia.md) e servem para conferir se as medidas estão corretas.

## Como reproduzir

1. Rode os projetos anteriores para gerar o banco `olist_dw.db` (olist-sql) e o arquivo `previsao_atraso.csv` (olist-previsao-atraso).
2. Gere os CSVs do dashboard (requer Python com pandas):

```bash
python exportar_dados.py
```

3. Abra o Power BI Desktop, crie o parâmetro `PastaDados` apontando para a pasta `dados` e crie as consultas de [`docs/consultas_power_query.md`](docs/consultas_power_query.md).
4. Crie os relacionamentos, aplique o tema `tema/tema_claro.json` e crie as medidas.

O arquivo `olist-dashboard.pbix` deste repositório já traz tudo pronto.

## Estrutura

```
exportar_dados.py           gera os CSVs, as consultas M e os valores de conferência
tema/tema_claro.json        tema do relatório
docs/
    paginas.md              o que há em cada página
    modelo_de_dados.md      tabelas e relacionamentos
    medidas_dax.md          medidas DAX
    consultas_power_query.md
    valores_de_conferencia.md
```

## Limitações

- O dashboard é uma fotografia dos dados de 2016 a 2018. Não se atualiza sozinho.
- O risco de atraso é uma estimativa. O modelo perde qualidade quando o padrão dos atrasos muda, como explicado no projeto olist-previsao-atraso.
- A análise por vendedor usa `CROSSFILTER` nas medidas, o que funciona bem para este volume de dados, mas seria revisto em um modelo maior.

## Dados

Dataset publicado pela Olist no Kaggle, sob licença CC BY-NC-SA 4.0. Os dados são anonimizados.
