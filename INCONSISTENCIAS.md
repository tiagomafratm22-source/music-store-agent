# Inconsistências encontradas nos materiais da loja

Levantamento feito no manual `data/politicas_da_loja.pdf` e nos arquivos CSV de `data/`.

> **Nenhum dado foi corrigido.** O campo **Como o agente lida** indica a suposição adotada para que ele responda de forma coerente. Em uma implantação real, cada item deveria ser validado com a loja.

## Sumário

- [Manual de políticas](#manual-de-políticas)
- [Produtos](#produtos)
- [Pedidos](#pedidos)
- [Promoções](#promoções)
- [Clientes](#clientes)

---

## Manual de políticas

### Telefone/WhatsApp

- **Inconsistência:** o número aparece como (67) 3341-4444 na capa e no §1.2, e como (67) 3321-4500 no §7.
- **Como o agente lida:** usa (67) 3341-4444, que aparece em dois pontos, inclusive nos dados da empresa.

### E-mail

- **Inconsistência:** a capa traz `contato@emporiodamusica.com.br`; o §1.2 traz `contato@empóriodamusica.com.br`, com acento.
- **Como o agente lida:** usa a versão sem acento.

### Parcela mínima

- **Inconsistência:** a tabela do §3 indica parcela mínima de R$ 100,00, enquanto o §3.1 define faixas de R$ 50, R$ 80 e R$ 100.
- **Como o agente lida:** segue as faixas do §3.1, por serem mais detalhadas.

### Parcelas até 3x

- **Inconsistência:** a regra "Sem valor mínimo (exceto abaixo de R$ 50,00)" se contradiz.
- **Como o agente lida:** interpreta como parcela mínima de R$ 50,00.

### Defeito

- **Inconsistência:** o §4.2 prevê troca em 30 dias após a compra e, depois disso, garantia com o fabricante. O §8.1 prevê garantia legal de 90 dias a partir do recebimento.
- **Como o agente lida:** informa as duas regras e orienta o cliente a falar com a equipe.

### Troca por preferência

- **Inconsistência:** o §4.3 concede "até 7 dias", sem informar a partir de quando.
- **Como o agente lida:** não tratado. Nos testes, o agente contou a partir do recebimento.

### Tamanho do catálogo

- **Inconsistência:** o §1 menciona "mais de 300 instrumentos", mas `products.csv` contém 65 produtos.
- **Como o agente lida:** responde apenas com o que está nos dados.

### Categorias sem produto

- **Inconsistência:** sopros e cordas orquestrais constam no §1 e em `categories.csv`, mas não têm nenhum produto.
- **Como o agente lida:** informa que não há itens desse tipo no momento.

### Lojas parceiras

- **Inconsistência:** o §7.1 manda sugerir lojas parceiras, mas não existe nenhuma lista.
- **Como o agente lida:** não sugere nem inventa lojas.

### Cancelamento

- **Inconsistência:** não há política de cancelamento de pedido.
- **Como o agente lida:** orienta o cliente a falar com a equipe.

### Reclamações

- **Inconsistência:** o §7.3 manda registrar e encaminhar as reclamações, mas não há sistema para isso.
- **Como o agente lida:** passa os contatos da equipe e não afirma ter registrado nada.

---

## Produtos

### Produto 136 — Ibanez Bass 2X

- **Inconsistência:** o status é `discontinued`, mas o estoque é 13.
- **Como o agente lida:** o status prevalece. Informa que está descontinuado e oferece alternativas.

### Produto 130 — Kala KA-ABP-CTG

- **Inconsistência:** o status é `coming_soon` e o estoque é 2, mas o produto já foi vendido (pedido 3 entregue e pedido 14 pendente).
- **Como o agente lida:** o status prevalece. Informa que ainda não está à venda.

### Produto 96 — Giannini GF-3D

- **Inconsistência:** o status é `active`, mas o estoque é 0.
- **Como o agente lida:** informa que está sem estoque e oferece alternativas.

### Produtos 135, 137, 139, 140, 142 e 144

- **Inconsistência:** a marca no nome diverge da descrição (por exemplo, "Music Man" descrito como "Fender Jazz Bass").
- **Como o agente lida:** o nome prevalece. A busca prioriza o nome sobre a descrição.

### Produto 142 — Korg Synth 1

- **Inconsistência:** a descrição indica 88 teclas, mas as especificações indicam 61.
- **Como o agente lida:** não tratado. A divergência pode ser repassada ao cliente.

### Produto 137 — Yamaha Bass 3X

- **Inconsistência:** a descrição indica 5 cordas, mas as especificações indicam 4.
- **Como o agente lida:** não tratado. A divergência pode ser repassada ao cliente.

### Produtos 139 e 140

- **Inconsistência:** o material dos cascos na descrição diverge das especificações.
- **Como o agente lida:** não tratado. A divergência pode ser repassada ao cliente.

### Produto 94 — Taylor 110e

- **Inconsistência:** o nome não indica que o instrumento é eletrônico, mas as especificações trazem `electronics: yes`.
- **Como o agente lida:** não tratado.

### Produto 84 — Giannini GN-15

- **Inconsistência:** o nome contém a palavra truncada "Cedr".
- **Como o agente lida:** não tratado.

---

## Pedidos

### Pedidos 3 e 20

- **Inconsistência:** o total não corresponde à soma dos itens. No pedido 3, o total é 3.450 contra 3.498 dos itens; no pedido 20, é 1.400 contra 1.488.
- **Como o agente lida:** informa o total registrado.

### Pedidos 1, 5, 10, 13 e 17

- **Inconsistência:** foram pagos com PIX, mas o total não reflete o desconto de 5%.
- **Como o agente lida:** informa o total registrado.

### Pedidos 9, 16 e 18

- **Inconsistência:** as parcelas ficam abaixo do mínimo do §3.1: R$ 58,32, R$ 71,65 e R$ 38,32.
- **Como o agente lida:** informa o pedido como registrado.

### Pedidos 1 a 5, 7 e 8

- **Inconsistência:** os clientes de Campo Grande têm prazo de 10 a 15 dias e código de rastreio, mas o §5.1 prevê entrega por motoboy em 1 a 3 dias úteis.
- **Como o agente lida:** informa a previsão registrada.

### Todos os pedidos — data de entrega

- **Inconsistência:** não há data real de entrega.
- **Como o agente lida:** usa a previsão de entrega como referência para os 7 dias e avisa que a equipe confirma a data exata.

### Todos os pedidos — canal de venda

- **Inconsistência:** não há registro do canal de venda, mas o direito de arrependimento (§4.1) só vale para compra online.
- **Como o agente lida:** pergunta ao cliente.

### Todos os pedidos — datas dos dados

- **Inconsistência:** os dados terminam em março de 2026, então, na data atual, os pedidos pendentes e enviados parecem muito atrasados.
- **Como o agente lida:** usa a data real. Se a previsão já passou, orienta o cliente a falar com a equipe.

---

## Promoções

### Vigência

- **Inconsistência:** não há datas de início e fim, apenas o campo `is_active`.
- **Como o agente lida:** `is_active` é a única fonte de verdade.

### Duplicidade

- **Inconsistência:** os produtos 93, 96 e 99 têm mais de uma promoção. O produto 96 tem 18% e 40% na mesma campanha.
- **Como o agente lida:** todas estão inativas hoje. Se houvesse mais de uma ativa, valeria o maior desconto.

### Faixas do §6.1

- **Inconsistência:** a promoção 1 (Black Friday) é de 10%, abaixo da faixa de 15% a 30%. A promoção 17 (Aniversário) é de 30%, acima da faixa de 10% a 25%.
- **Como o agente lida:** sem efeito hoje, pois ambas estão inativas.

### Campanhas fora do manual

- **Inconsistência:** as campanhas Páscoa, Inverno, Oferta Especial e Desconto Exclusivo não constam no §6.1.
- **Como o agente lida:** aceita as que estiverem ativas.

### Produto descontinuado em promoção

- **Inconsistência:** a promoção 16 aponta para o produto 113, que está descontinuado.
- **Como o agente lida:** sem efeito hoje, pois está inativa.

### "Venda final"

- **Inconsistência:** o §4.4 exclui itens com esse aviso, mas os dados não têm um campo que o indique.
- **Como o agente lida:** o agente não consegue identificar esses itens.

---

## Clientes

### E-mail duplicado

- **Inconsistência:** o e-mail `bruno.martins@jmail.com` aparece nos clientes 11 e 43.
- **Como o agente lida:** um e-mail ambíguo não identifica ninguém. A consulta falha e o cliente precisa informar o telefone.
