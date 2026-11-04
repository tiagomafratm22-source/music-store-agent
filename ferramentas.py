"""Ferramentas que o modelo pode chamar e as funções de apoio delas.

A LangChain monta a descrição de cada ferramenta a partir dos tipos dos parâmetros e da docstring,
por isso elas precisam ficar assim. Não use o decorador @tool: montar_ficha chama
simular_parcelamento direto e isso quebraria.
"""
import json
import re # Usado para separar palavras, limpar telefones e e-mails e comparar strings.
import unicodedata
from datetime import date, datetime
from difflib import SequenceMatcher # Utilizado para comparar a similaridade entre strings, útil para encontrar termos semelhantes.

from dados import FUSO_DA_LOJA, TITULOS_DO_MANUAL, ler_csv, secoes_do_manual

MAX_RESULTADOS = 15

# Palavras que não ajudam a encontrar um produto
PALAVRAS_IGNORADAS = {
    "a", "as", "o", "os", "um", "uma", "de", "da", "do", "das", "dos", "e", "em", "no", "na",
    "para", "pra", "com", "por", "que", "ate", "reais", "r",
}

# O catálogo guarda algumas especificações em inglês; estas palavras entram na busca no lugar delas
ESPECIFICACOES_EM_PORTUGUES = {
    ("strings", "steel"): "aço",
    ("electronics", "yes"): "elétrico eletroacústico",
}

# As seções 7 e 10 orientam a equipe e já estão no prompt
SECOES_CONSULTAVEIS = TITULOS_DO_MANUAL.keys() - {"atendimento", "disposicoes"}

STATUS_PEDIDO = {
    "pending": "pendente",
    "confirmed": "confirmado, aguardando envio",
    "shipped": "enviado",
    "delivered": "entregue",
    "cancelled": "cancelado",
}
FORMA_DE_PAGAMENTO = {"pix": "PIX", "debit": "cartão de débito", "boleto": "boleto"}

# Mesma mensagem para qualquer falha na consulta de pedidos, assim ninguém descobre se um pedido existe
PEDIDO_NAO_LOCALIZADO = {
    "resultado": "Não foi possível localizar pedidos com esses dados. Peça ao cliente que confirme "
    "o telefone ou e-mail do cadastro e, se tiver, o número do pedido."
}


# ---------- Catálogo ----------

def separar_palavras(texto: str) -> list[str]:
    """Minúsculas, sem acento e com o plural "-ões" igualado ao singular: "Violões" vira "violao"."""
    sem_acento = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return [re.sub(r"oes$", "ao", palavra) for palavra in re.findall(r"[a-z0-9]+", sem_acento)]


def termo_encontrado(termo: str, palavras: list[str]) -> bool:
    """Aceita parte da palavra ("yama" em "yamaha") e erros de digitação pequenos."""
    # Termo de até 3 letras ("aço", "c40", "7") só vale inteiro: senão "aco" casaria com "ac" de "AC-39"
    if len(termo) <= 3:
        return termo in palavras
    return any(termo in palavra or SequenceMatcher(None, termo, palavra).ratio() >= 0.8 for palavra in palavras)


def calcular_parcelas_max(valor: float) -> int:
    """Faixas da seção 3.1 do manual: parcela mínima de R$ 100 em 7x a 12x, R$ 80 em 4x a 6x e R$ 50 até 3x."""
    for parcelas in range(12, 1, -1):
        if parcelas >= 7:
            minimo = 100
        elif parcelas >= 4:
            minimo = 80
        else:
            minimo = 50
        if valor / parcelas >= minimo:
            return parcelas
    return 1


def pegar_situacao(produto: dict) -> str:
    # O status vale mais que o estoque: descontinuado com estoque continua descontinuado
    if produto["status"] == "discontinued":
        return "descontinuado"
    if produto["status"] == "coming_soon":
        return "em breve"
    return "disponível" if int(produto["stock_quantity"]) > 0 else "sem estoque"


def pegar_categorias() -> dict[str, str]:
    return {categoria["category_id"]: categoria["name"] for categoria in ler_csv("categories")}


def pegar_promocoes_ativas() -> dict[str, dict]:
    """Promoção vigente de cada produto. Se houver duas, vale a de maior desconto."""
    ativas = {}
    for promocao in ler_csv("promotions"):
        if promocao["is_active"] != "1":
            continue
        atual = ativas.get(promocao["product_id"])
        if atual is None or float(promocao["discount_percent"]) > float(atual["discount_percent"]):
            ativas[promocao["product_id"]] = promocao
    return ativas


def montar_ficha(produto: dict, categorias: dict[str, str], promocoes: dict[str, dict]) -> dict:
    """Dados do produto para o modelo. Preços e parcelas são calculados aqui, nunca pelo modelo."""
    preco_tabela = float(produto["price_brl"])
    situacao = pegar_situacao(produto)
    promocao = promocoes.get(produto["product_id"])
    desconto = float(promocao["discount_percent"]) if promocao else 0
    preco_final = round(preco_tabela * (1 - desconto / 100), 2)
    return {
        "nome": produto["name"],
        "categoria": categorias[produto["category_id"]],
        "situacao": situacao,
        "estoque": int(produto["stock_quantity"]) if situacao == "disponível" else 0,
        "preco_tabela": preco_tabela,
        "promocao": {"nome": promocao["description"], "desconto_percentual": desconto} if promocao else None,
        "preco_final": preco_final,
        # O desconto do PIX não acumula com promoção (seção 6.2 do manual)
        "preco_no_pix": None if promocao else round(preco_tabela * 0.95, 2),
        **simular_parcelamento(preco_final),
        "descricao": produto["description"],
        "especificacoes": json.loads(produto["specs"]),
    }


def pontuar(termos: list[str], produto: dict, ficha: dict) -> tuple[int, int]:
    """(termos encontrados no total, termos encontrados no nome, categoria ou especificações)."""
    especificacoes = [
        ESPECIFICACOES_EM_PORTUGUES.get((chave, str(valor)), str(valor))
        for chave, valor in ficha["especificacoes"].items()
    ]
    principais = separar_palavras(" ".join([produto["name"], ficha["categoria"], *especificacoes]))
    todas = principais + separar_palavras(produto["description"])
    no_total = sum(termo_encontrado(termo, todas) for termo in termos)
    no_nome = sum(termo_encontrado(termo, principais) for termo in termos)
    return no_total, no_nome


# ---------- Ferramentas ----------

def simular_parcelamento(valor: float | int) -> dict:
    """Calcula o máximo de parcelas sem juros e o valor de cada uma para um valor em reais.

    Args:
        valor: Valor total da compra em reais.
    """
    parcelas = calcular_parcelas_max(valor)
    return {"parcelas_max_sem_juros": parcelas, "valor_da_parcela": round(valor / parcelas, 2)}


def buscar_produtos(
    termo: str | None = None,
    preco_max: float | int | None = None,  # aceita int porque o modelo pode mandar 1000 em vez de 1000.0
    apenas_disponiveis: bool | None = None,
) -> dict:
    """Consulta o catálogo: preço, estoque, situação, promoção vigente e parcelamento.

    Use para qualquer pergunta sobre produtos, mesmo quando achar que sabe a resposta.

    Args:
        termo: Palavras-chave como tipo de instrumento, marca, modelo ou característica.
            Ex.: "violão", "Takamine GD20", "ukulele tenor", "violão nylon iniciante".
        preco_max: Preço final máximo em reais, já considerando promoção vigente.
        apenas_disponiveis: Se verdadeiro, traz só produtos que podem ser comprados agora.
    """
    categorias = pegar_categorias()
    promocoes = pegar_promocoes_ativas()
    termos = [palavra for palavra in separar_palavras(termo or "") if palavra not in PALAVRAS_IGNORADAS]

    catalogo = []
    candidatos = []
    for produto in ler_csv("products"):
        ficha = montar_ficha(produto, categorias, promocoes)
        catalogo.append(ficha)
        if preco_max is not None and ficha["preco_final"] > preco_max:
            continue
        if apenas_disponiveis and ficha["situacao"] != "disponível":
            continue
        pontos = pontuar(termos, produto, ficha)
        if pontos[0] > 0 or not termos:
            candidatos.append((pontos, ficha))

    # Ganha quem tem mais termos; no empate, quem tem mais termos no nome e não só na descrição
    melhor = max((pontos for pontos, _ in candidatos), default=(0, 0))
    fichas = sorted((ficha for pontos, ficha in candidatos if pontos == melhor), key=lambda ficha: ficha["preco_final"])

    # Se nada do que foi encontrado pode ser comprado, já devolve alternativas (seção 7.3 do manual)
    alternativas = []
    if fichas and all(ficha["situacao"] != "disponível" for ficha in fichas):
        referencia = fichas[0]
        opcoes = [
            ficha for ficha in catalogo
            if ficha["categoria"] == referencia["categoria"] and ficha["situacao"] == "disponível"
        ]
        # As de preço mais próximo do produto pedido primeiro
        opcoes.sort(key=lambda ficha: abs(ficha["preco_final"] - referencia["preco_final"]))
        alternativas = opcoes[:3]

    resultado = {
        "total_encontrado": len(fichas),
        "atende_todos_os_termos": melhor[0] == len(termos),
        "produtos": fichas[:MAX_RESULTADOS],
        "alternativas_disponiveis": alternativas,
    }
    # Sem este aviso o modelo trataria os mais baratos como o catálogo inteiro (ex.: "qual o mais caro?")
    if len(fichas) > MAX_RESULTADOS:
        resultado["aviso"] = (
            f"Mostrando só os {MAX_RESULTADOS} mais baratos de {len(fichas)}. Não conclua nada sobre os demais: "
            "busque de novo com termo mais específico (marca, modelo, tipo) ou com preco_max."
        )
    return resultado


def listar_promocoes_ativas() -> dict:
    """Lista as promoções vigentes hoje. Promoção fora desta lista não está valendo."""
    categorias = pegar_categorias()
    promocoes = pegar_promocoes_ativas()
    fichas = [
        montar_ficha(produto, categorias, promocoes)
        for produto in ler_csv("products")
        if produto["product_id"] in promocoes
    ]
    return {"promocoes_ativas": sorted(fichas, key=lambda ficha: ficha["preco_final"])}


# ---------- Pedidos ----------

def identificar_cliente(contato: str) -> dict | None:
    """O único cliente com esse e-mail ou telefone. Dois clientes com o mesmo dado contam como nenhum."""
    contato = contato.strip().lower()
    if "@" in contato:
        encontrados = [cliente for cliente in ler_csv("customers") if cliente["email"].lower() == contato]
    else:
        numero = re.sub(r"\D", "", contato).removeprefix("55")
        encontrados = [cliente for cliente in ler_csv("customers") if re.sub(r"\D", "", cliente["phone"]) == numero]
    return encontrados[0] if len(encontrados) == 1 else None


def dias_desde(data_iso: str, hoje: date) -> int:
    return (hoje - date.fromisoformat(data_iso)).days


def consultar_pedidos(telefone_ou_email: str, numero_pedido: int | None = None) -> dict:
    """Consulta pedidos do próprio cliente: status, itens, total, rastreio e prazos.

    Só use com o telefone ou e-mail informado pelo cliente nesta conversa.

    Args:
        telefone_ou_email: Telefone com DDD ou e-mail do cadastro do cliente.
        numero_pedido: Número do pedido. Sem ele, retorna todos os pedidos do cliente.
    """
    cliente = identificar_cliente(telefone_ou_email)
    if cliente is None:
        return PEDIDO_NAO_LOCALIZADO

    # Só os pedidos desse cliente: um número de pedido de outra pessoa cai no "não localizado"
    pedidos = [
        pedido for pedido in ler_csv("orders")
        if pedido["customer_id"] == cliente["customer_id"]
        and (numero_pedido is None or int(pedido["order_id"]) == numero_pedido)
    ]
    if not pedidos:
        return PEDIDO_NAO_LOCALIZADO

    nomes_dos_produtos = {produto["product_id"]: produto["name"] for produto in ler_csv("products")}
    itens_dos_pedidos = ler_csv("order_items")
    hoje = datetime.now(FUSO_DA_LOJA).date()

    resultado = []
    for pedido in pedidos:
        previsao = pedido["estimated_delivery"] or None  # pedido sem envio não tem previsão nem rastreio
        forma = pedido["payment_method"]  # o crédito vem como "credit_12x"
        resultado.append({
            "numero": int(pedido["order_id"]),
            "data_compra": pedido["order_date"],
            "dias_desde_compra": dias_desde(pedido["order_date"], hoje),
            "status": STATUS_PEDIDO[pedido["status"]],
            "total": float(pedido["total_brl"]),
            "pagamento": FORMA_DE_PAGAMENTO.get(forma) or "cartão de crédito em " + forma.split("_")[1],
            "codigo_rastreio": pedido["tracking_code"] or None,
            "previsao_entrega": previsao,
            "dias_desde_previsao_entrega": dias_desde(previsao, hoje) if previsao else None,
            "observacoes": pedido["notes"] or None,
            "itens": [
                {"produto": nomes_dos_produtos[item["product_id"]], "quantidade": int(item["quantity"])}
                for item in itens_dos_pedidos
                if item["order_id"] == pedido["order_id"]
            ],
        })

    return {"primeiro_nome_cliente": cliente["name"].split()[0], "pedidos": resultado}


# ---------- Políticas ----------

def consultar_politicas(secao: str) -> str:
    """Retorna uma seção do manual de políticas da loja.

    Args:
        secao: sobre_e_contato (a loja, endereço, o que vende); horario (funcionamento);
            pagamento (formas e parcelamento); trocas_devolucoes (arrependimento, defeito, trocas);
            frete (entregas, prazos, rastreio); promocoes (regras de desconto); garantia;
            privacidade (dados pessoais, LGPD).
    """
    if secao not in SECOES_CONSULTAVEIS:
        return f"Seção inexistente. Opções: {', '.join(sorted(SECOES_CONSULTAVEIS))}."
    return secoes_do_manual()[secao]


FERRAMENTAS = [buscar_produtos, listar_promocoes_ativas, simular_parcelamento, consultar_pedidos, consultar_politicas]
