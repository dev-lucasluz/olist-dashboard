# Páginas do dashboard

Quatro páginas, cada uma respondendo a uma pergunta. O tema é o [tema_claro.json](../tema/tema_claro.json): fundo claro, azul como cor principal e laranja só para destacar o que é problema (atraso, risco).

Todas as páginas têm filtros de **Ano** (`dim_data[ano]`) e **Estado do cliente** (`dim_cliente[estado]`), no topo, em uma única linha.

## 1. Visão geral: como estão as vendas?

| Visual | Campos |
|---|---|
| Cartão | `Receita` |
| Cartão | `Pedidos Entregues` |
| Cartão | `Ticket Médio` |
| Cartão | `Nota Média` |
| Cartão | `% Clientes Recorrentes` |
| Gráfico de linhas | Eixo `dim_data[ano_mes]`, valor `Receita` |
| Gráfico de barras horizontais | Eixo `dim_cliente[estado]`, valor `Receita`, 10 maiores |

O gráfico de linhas mostra o crescimento de 2017 a 2018 e o pico de novembro de 2017. Os cartões de recorrência mostram que menos de 5% dos clientes compram de novo.

## 2. Entrega: a promessa de prazo está sendo cumprida?

| Visual | Campos |
|---|---|
| Cartão | `% Entregue no Prazo` |
| Cartão | `Dias Médios de Entrega` |
| Cartão | `Dias Médios de Atraso` |
| Gráfico de linhas | Eixo `dim_data[ano_mes]`, valor `% Atrasado` |
| Gráfico de barras horizontais | Eixo `dim_cliente[estado]`, valor `% Atrasado`, 10 maiores; filtro do visual `Pedidos com Entrega Avaliada` maior ou igual a 300 |
| Gráfico de colunas | Eixo `fato_pedidos[faixa_atraso]`, valor `Nota Média` |

O gráfico de colunas por faixa de atraso é o destaque da página: a nota média cai de cerca de 4,3 (no prazo) para menos de 2 quando o atraso passa de uma semana.

## 3. Produtos e vendedores: onde está a receita?

| Visual | Campos |
|---|---|
| Gráfico de barras horizontais | Eixo `dim_produto[categoria]`, valor `Receita de Itens`, 10 maiores, com rótulo de dados |
| Tabela | `dim_vendedor[vendedor_id]`, `dim_vendedor[estado]`, `Receita de Itens`, `Pedidos do Vendedor`, `Nota Média do Vendedor`, `% Atrasado do Vendedor`; 10 maiores por `Receita de Itens` |
| Filtro | `dim_produto[categoria]` (lista com busca) |

Na tabela de vendedores, mostrar só os oito primeiros caracteres do `vendedor_id`, criando uma coluna calculada no Power Query se preferir.

## 4. Risco de atraso: quais pedidos pedem atenção?

Página construída sobre o modelo do projeto [olist-previsao-atraso](https://github.com/dev-lucasluz/olist-previsao-atraso). O risco é uma estimativa, não uma certeza, e a página deve dizer isso em uma nota.

| Visual | Campos |
|---|---|
| Cartão | `Pedidos em Andamento` |
| Cartão | `Risco Médio em Andamento` |
| Cartão | `Pedidos em Alto Risco` |
| Gráfico de colunas | Eixo `previsao_atraso[faixa_risco]`, valor `Taxa Real de Atraso` (validação temporal) |
| Gráfico de linhas | Eixo `dim_data[ano_mes]`, valores `Risco Médio Previsto` e `Taxa Real de Atraso` |
| Tabela | Pedidos em andamento ordenados por risco: `pedido_id`, `data_compra`, `dim_cliente[estado]`, `risco_atraso`; filtro do visual `origem` igual a "Em andamento" |

O gráfico de colunas por faixa de risco mostra que o modelo ordena bem: a taxa real de atraso sobe de 4,2% na faixa Baixo para 15,7% na faixa Alto. O gráfico de linhas mostra também a limitação: o risco previsto e a taxa real se afastam em alguns meses, porque o padrão dos atrasos muda ao longo do tempo.

Nota sugerida no rodapé da página: "Risco estimado por modelo estatístico. Serve para priorizar pedidos, não como probabilidade exata."

## Boas práticas usadas

- Uma única escala por gráfico; nada de eixo duplo.
- Uma cor principal (azul) e o laranja só para atraso e risco.
- Título de cada visual dizendo o que ele mostra, com a unidade.
- Sem rótulo em todos os pontos: só onde ajuda a leitura.
