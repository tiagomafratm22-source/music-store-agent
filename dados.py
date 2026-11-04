"""Acesso aos arquivos da loja: catálogo, clientes e pedidos em CSV e o manual de políticas em PDF."""
import csv
import re
from datetime import timedelta, timezone
from functools import cache
from pathlib import Path

from pypdf import PdfReader

PASTA_DADOS = Path(__file__).parent / "data"

# Campo Grande/MS fica em UTC-4, sem horário de verão
FUSO_DA_LOJA = timezone(timedelta(hours=-4))

TITULOS_DO_MANUAL = {
    "sobre_e_contato": "1. Sobre a Empório da Música",
    "horario": "2. Horário de Funcionamento",
    "pagamento": "3. Formas de Pagamento",
    "trocas_devolucoes": "4. Política de Trocas e Devoluções",
    "frete": "5. Política de Frete e Entregas",
    "promocoes": "6. Promoções e Descontos",
    "atendimento": "7. Atendimento via WhatsApp",
    "garantia": "8. Garantia",
    "privacidade": "9. Privacidade e Proteção de Dados",
    "disposicoes": "10. Disposições Finais",
}

# Cabeçalho e rodapé que se repetem em todas as páginas do PDF
LINHA_DE_PAGINA = re.compile(r"Empório da Música Manual de Políticas e Procedimentos|Página \d+")


def ler_csv(nome: str) -> list[dict]:
    """Lê um CSV da pasta de dados. É lido a cada consulta para refletir mudanças no arquivo."""
    with open(PASTA_DADOS / f"{nome}.csv", encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


@cache
def secoes_do_manual() -> dict[str, str]:
    """Divide o manual nas seções numeradas. O resultado fica guardado após a primeira leitura."""
    leitor = PdfReader(PASTA_DADOS / "politicas_da_loja.pdf")
    # O modo layout mantém linhas e tabelas; no modo normal vinha uma palavra por linha
    texto = "\n".join(pagina.extract_text(extraction_mode="layout") for pagina in leitor.pages)

    linhas = []
    for linha in texto.splitlines():
        linha = re.sub(r" {3,}", "  ", linha.strip())
        if linha and not LINHA_DE_PAGINA.fullmatch(linha):
            linhas.append(linha)

    # Só o título exato abre uma seção: a lista numerada do §7.2 ("1. Saudação") não pode virar seção
    titulos = "|".join(re.escape(titulo) for titulo in TITULOS_DO_MANUAL.values())
    partes = re.split(rf"^({titulos})$", "\n".join(linhas), flags=re.MULTILINE)
    chave_do_titulo = {titulo: chave for chave, titulo in TITULOS_DO_MANUAL.items()}
    secoes = {
        chave_do_titulo[titulo]: f"{titulo}\n{corpo.strip()}" if corpo.strip() else titulo
        for titulo, corpo in zip(partes[1::2], partes[2::2])
    }

    faltando = TITULOS_DO_MANUAL.keys() - secoes.keys()
    if faltando:
        raise ValueError(f"Seções não encontradas no manual: {sorted(faltando)}")
    return secoes
