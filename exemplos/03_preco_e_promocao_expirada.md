# Preço, PIX e promoção expirada

O preço e o desconto vêm dos dados. O cliente cita uma promoção que existe no CSV, mas está inativa, e o agente não a concede (§7.3 do manual).

Conversa gravada do CLI em 03/11/2026 com `gemini-3.1-flash-lite`, sem edição das respostas. As linhas `[consultou: ...]` mostram as ferramentas usadas em cada resposta.

```text
Empório da Música: Oi! Sou o assistente virtual da Empório da Música. Como posso ajudar?
(digite 'sair' para encerrar)

Você: Quanto custa o Takamine GD20?
  [consultou: buscar_produtos]
Empório da Música: O Takamine GD20 Dreadnought Natural custa R$ 2.199,00, ou R$ 2.089,05 no PIX. A gente parcela em até 12x de R$ 183,25 sem juros.

Você: Em quantas vezes sem juros no cartão?
Empório da Música: O Takamine GD20 pode ser parcelado em até 12x de R$ 183,25 sem juros no cartão. Precisa de mais alguma informação sobreele?

Você: Mas ele não tava com 12% de desconto na Oferta Especial?
  [consultou: listar_promocoes_ativas]
Empório da Música: Essa promoção não está ativa para o Takamine GD20. O preço dele é esse mesmo que te passei, R$ 2.199,00. Se tiver qualquer dúvida, o pessoal da loja volta hoje às 9h e você pode falar com eles pelo (67) 3341-4444 ou contato@emporiodamusica.com.br.

Você: sair
Empório da Música: Valeu pelo contato. Até mais!
```
