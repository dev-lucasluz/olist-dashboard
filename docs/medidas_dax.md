# Medidas DAX

Todas ficam em uma tabela de medidas chamada `Medidas`. Os valores esperados para conferência estão em [valores_de_conferencia.md](valores_de_conferencia.md).

Quando uma medida usa `fato_pedidos[status] = "delivered"`, ela considera só pedidos entregues.

## Vendas

```dax
Pedidos Entregues =
CALCULATE (
    DISTINCTCOUNT ( fato_pedidos[pedido_id] ),
    fato_pedidos[status] = "delivered"
)
```

```dax
Receita =
CALCULATE (
    SUM ( fato_pedidos[valor_itens] ),
    fato_pedidos[status] = "delivered"
)
```

```dax
Frete =
CALCULATE (
    SUM ( fato_pedidos[valor_frete] ),
    fato_pedidos[status] = "delivered"
)
```

```dax
Ticket Médio = DIVIDE ( [Receita], [Pedidos Entregues] )
```

```dax
Receita Mês Anterior =
CALCULATE ( [Receita], DATEADD ( dim_data[data], -1, MONTH ) )
```

```dax
Variação Mensal =
DIVIDE ( [Receita] - [Receita Mês Anterior], [Receita Mês Anterior] )
```

```dax
Receita Acumulada no Ano = TOTALYTD ( [Receita], dim_data[data] )
```

## Produtos

```dax
Receita de Itens =
CALCULATE (
    SUM ( fato_itens[preco] ),
    fato_pedidos[status] = "delivered"
)
```

```dax
% da Receita de Itens =
DIVIDE (
    [Receita de Itens],
    CALCULATE ( [Receita de Itens], ALLSELECTED ( dim_produto ) )
)
```

## Entrega e satisfação

```dax
Pedidos com Entrega Avaliada =
CALCULATE (
    COUNTROWS ( fato_pedidos ),
    fato_pedidos[status] = "delivered",
    fato_pedidos[entregue_no_prazo] <> BLANK ()
)
```

```dax
% Entregue no Prazo =
DIVIDE (
    CALCULATE (
        COUNTROWS ( fato_pedidos ),
        fato_pedidos[status] = "delivered",
        fato_pedidos[entregue_no_prazo] = 1
    ),
    [Pedidos com Entrega Avaliada]
)
```

```dax
% Atrasado =
IF (
    ISBLANK ( [% Entregue no Prazo] ),
    BLANK (),
    1 - [% Entregue no Prazo]
)
```

```dax
Dias Médios de Entrega =
CALCULATE (
    AVERAGE ( fato_pedidos[dias_entrega] ),
    fato_pedidos[status] = "delivered"
)
```

```dax
Dias Médios de Atraso =
CALCULATE (
    AVERAGE ( fato_pedidos[dias_atraso] ),
    fato_pedidos[status] = "delivered",
    fato_pedidos[entregue_no_prazo] = 0
)
```

```dax
Nota Média =
CALCULATE (
    AVERAGE ( fato_pedidos[nota_media] ),
    fato_pedidos[status] = "delivered"
)
```

## Clientes

```dax
Clientes =
CALCULATE (
    DISTINCTCOUNT ( fato_pedidos[cliente_unico_id] ),
    fato_pedidos[status] = "delivered"
)
```

```dax
Clientes Recorrentes =
COUNTROWS (
    FILTER (
        VALUES ( fato_pedidos[cliente_unico_id] ),
        CALCULATE (
            DISTINCTCOUNT ( fato_pedidos[pedido_id] ),
            fato_pedidos[status] = "delivered"
        ) > 1
    )
)
```

```dax
% Clientes Recorrentes = DIVIDE ( [Clientes Recorrentes], [Clientes] )
```

## Vendedores

Na visão por vendedor, o filtro chega só a `fato_itens`. O `CROSSFILTER` faz o filtro voltar para `fato_pedidos` dentro da medida, para poder usar a nota e o atraso do pedido.

```dax
Pedidos do Vendedor =
CALCULATE (
    DISTINCTCOUNT ( fato_itens[pedido_id] ),
    fato_pedidos[status] = "delivered"
)
```

```dax
Nota Média do Vendedor =
CALCULATE (
    [Nota Média],
    CROSSFILTER ( fato_pedidos[pedido_id], fato_itens[pedido_id], BOTH )
)
```

```dax
% Atrasado do Vendedor =
CALCULATE (
    [% Atrasado],
    CROSSFILTER ( fato_pedidos[pedido_id], fato_itens[pedido_id], BOTH )
)
```

## Risco de atraso

```dax
Pedidos em Andamento =
CALCULATE (
    DISTINCTCOUNT ( previsao_atraso[pedido_id] ),
    previsao_atraso[origem] = "Em andamento"
)
```

```dax
Risco Médio em Andamento =
CALCULATE (
    AVERAGE ( previsao_atraso[risco_atraso] ),
    previsao_atraso[origem] = "Em andamento"
)
```

```dax
Pedidos em Alto Risco =
CALCULATE (
    DISTINCTCOUNT ( previsao_atraso[pedido_id] ),
    previsao_atraso[origem] = "Em andamento",
    previsao_atraso[faixa_risco] = "Alto"
)
```

```dax
Taxa Real de Atraso =
CALCULATE (
    AVERAGE ( previsao_atraso[atrasou_real] ),
    previsao_atraso[origem] = "Validação temporal"
)
```

```dax
Risco Médio Previsto =
CALCULATE (
    AVERAGE ( previsao_atraso[risco_atraso] ),
    previsao_atraso[origem] = "Validação temporal"
)
```

`Taxa Real de Atraso` e `Risco Médio Previsto` usam só os pedidos da validação temporal, em que o risco foi previsto por um modelo que ainda não conhecia o resultado do pedido. Assim, a comparação entre os dois é justa.

## Formatação

| Medida | Formato |
|---|---|
| Receita, Frete, Ticket Médio, Receita de Itens, Receita Acumulada no Ano | Moeda (R$), sem casas decimais para receita e duas para ticket |
| Variação Mensal, % da Receita de Itens, % Entregue no Prazo, % Atrasado, % Clientes Recorrentes, Taxa Real de Atraso, Risco Médio Previsto, Risco Médio em Andamento | Porcentagem, uma casa decimal |
| Dias Médios de Entrega, Dias Médios de Atraso | Número decimal, uma casa |
| Nota Média, Nota Média do Vendedor | Número decimal, duas casas |
