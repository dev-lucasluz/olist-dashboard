# Consultas do Power Query

Cada bloco abaixo é a consulta de uma tabela. Antes, crie um parâmetro de texto chamado `PastaDados` com o caminho da pasta `dados` (por exemplo `C:\projetos\olist-dashboard\dados\`, com a barra invertida no final).

A conversão de tipos usa a cultura `en-US` porque os CSVs trazem o ponto como separador decimal. Sem isso, o Power BI em português lê `123.45` como `12345`.

Para criar cada consulta: **Obter dados > Consulta em branco > Editor Avançado**, cole o código e dê à consulta o nome da tabela.

## dim_data

```
let
    Origem = Csv.Document(File.Contents(PastaDados & "dim_data.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Origem, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {{"data_id", Int64.Type}, {"data", type date}, {"ano", Int64.Type}, {"mes", Int64.Type}, {"mes_nome", type text}, {"ano_mes", type text}, {"trimestre", Int64.Type}, {"dia_semana_num", Int64.Type}, {"dia_semana", type text}}, "en-US")
in
    Tipos
```

## dim_cliente

```
let
    Origem = Csv.Document(File.Contents(PastaDados & "dim_cliente.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Origem, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {{"cliente_id", type text}, {"cliente_unico_id", type text}, {"cidade", type text}, {"estado", type text}}, "en-US")
in
    Tipos
```

## dim_vendedor

```
let
    Origem = Csv.Document(File.Contents(PastaDados & "dim_vendedor.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Origem, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {{"vendedor_id", type text}, {"cidade", type text}, {"estado", type text}}, "en-US")
in
    Tipos
```

## dim_produto

```
let
    Origem = Csv.Document(File.Contents(PastaDados & "dim_produto.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Origem, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {{"produto_id", type text}, {"categoria", type text}, {"peso_g", type number}, {"volume_cm3", type number}}, "en-US")
in
    Tipos
```

## fato_pedidos

```
let
    Origem = Csv.Document(File.Contents(PastaDados & "fato_pedidos.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Origem, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {{"pedido_id", type text}, {"cliente_id", type text}, {"cliente_unico_id", type text}, {"status", type text}, {"data_compra_id", Int64.Type}, {"hora_compra", Int64.Type}, {"qtd_itens", Int64.Type}, {"valor_itens", type number}, {"valor_frete", type number}, {"valor_pago", type number}, {"parcelas", Int64.Type}, {"nota_media", type number}, {"dias_entrega", type number}, {"dias_atraso", type number}, {"entregue_no_prazo", Int64.Type}, {"faixa_atraso", type text}, {"ordem_faixa_atraso", Int64.Type}}, "en-US")
in
    Tipos
```

## fato_itens

```
let
    Origem = Csv.Document(File.Contents(PastaDados & "fato_itens.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Origem, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {{"pedido_id", type text}, {"item_seq", Int64.Type}, {"vendedor_id", type text}, {"produto_id", type text}, {"preco", type number}, {"frete", type number}}, "en-US")
in
    Tipos
```

## previsao_atraso

```
let
    Origem = Csv.Document(File.Contents(PastaDados & "previsao_atraso.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Origem, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {{"pedido_id", type text}, {"origem", type text}, {"risco_atraso", type number}, {"faixa_risco", type text}, {"ordem_faixa_risco", Int64.Type}, {"data_compra", type date}, {"atrasou_real", Int64.Type}}, "en-US")
in
    Tipos
```
