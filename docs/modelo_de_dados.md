# Modelo de dados

Esquema estrela vindo do projeto [olist-sql](https://github.com/dev-lucasluz/olist-sql), mais a tabela de previsões do projeto [olist-previsao-atraso](https://github.com/dev-lucasluz/olist-previsao-atraso).

```
dim_data ---------\
                   \
dim_cliente ------- fato_pedidos ---- fato_itens ---- dim_produto
                        |                  |
                 previsao_atraso      dim_vendedor
```

## Tabelas

| Tabela | Linhas | Descrição |
|---|---:|---|
| fato_pedidos | 99.441 | Um pedido por linha: valores, entrega, nota e cliente único. |
| fato_itens | 112.650 | Um item por linha: preço, frete, produto e vendedor. |
| previsao_atraso | 71.785 | Risco de atraso previsto por pedido. |
| dim_data | 1.096 | Calendário de 2016 a 2018. |
| dim_cliente | 99.441 | Cliente de cada pedido (`cliente_id`) e a pessoa (`cliente_unico_id`), com cidade e estado. |
| dim_produto | 32.951 | Categoria em inglês, peso e volume. |
| dim_vendedor | 3.095 | Cidade e estado do vendedor. |

## Relacionamentos

Todos com filtro em uma única direção, da tabela do lado "um" para a do lado "muitos".

| De (um) | Para (muitos) | Colunas |
|---|---|---|
| dim_data | fato_pedidos | `data_id` para `data_compra_id` |
| dim_cliente | fato_pedidos | `cliente_id` para `cliente_id` |
| fato_pedidos | fato_itens | `pedido_id` para `pedido_id` |
| dim_produto | fato_itens | `produto_id` para `produto_id` |
| dim_vendedor | fato_itens | `vendedor_id` para `vendedor_id` |
| fato_pedidos | previsao_atraso | `pedido_id` para `pedido_id` (um para um) |

O filtro de data e de cliente chega em `fato_itens` passando por `fato_pedidos`. Assim, escolher um ano ou um estado afeta as medidas de pedidos e as de itens da mesma forma.

Vendedor e produto filtram só os itens. Para trazer a nota e o atraso do pedido para a visão por vendedor, as medidas usam `CROSSFILTER` (veja [medidas_dax.md](medidas_dax.md)).

## Ajustes no modelo

- Marcar `dim_data` como tabela de datas, usando a coluna `data`.
- Ordenar `mes_nome` por `mes` e `dia_semana` por `dia_semana_num`.
- Ordenar `faixa_atraso` (em `fato_pedidos`) por `ordem_faixa_atraso`.
- Ordenar `faixa_risco` (em `previsao_atraso`) por `ordem_faixa_risco`.
- Ocultar as colunas de chave e de ordenação da visão de relatório.

## Decisões

- **Pedidos entregues como base:** a receita e as métricas de entrega consideram só pedidos com status `delivered`. Pedidos cancelados ou indisponíveis não geraram receita, e os em andamento ainda não têm desfecho.
- **Cliente único:** a análise de recompra usa `cliente_unico_id`, porque cada pedido recebe um `cliente_id` novo.
- **Faixas de atraso e de risco calculadas na exportação**, e não em DAX, para manter as medidas simples. A definição está no script `exportar_dados.py`.
