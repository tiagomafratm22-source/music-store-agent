"""Prompt do sistema e o contexto de data, hora e horário da loja que entra nele."""
from datetime import datetime, timedelta
from pathlib import Path

from dados import FUSO_DA_LOJA

# O texto fica em prompt.md para ser editado sem mexer no código. A única variável é {agora};
# qualquer outra chave escrita no arquivo precisa ser dobrada ({{ }}), senão o format dá KeyError.
PROMPT_DO_SISTEMA = (Path(__file__).parent / "prompt.md").read_text(encoding="utf-8")

DIAS_DA_SEMANA = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def situacao_da_loja(agora: datetime) -> str:
    """Se a loja está aberta e, se estiver fechada, quando volta. Feriados não constam nos dados."""
    # Sábado fecha às 13h, os outros dias às 18h. Domingo não abre.
    fechamento = 13 if agora.weekday() == 5 else 18
    if agora.weekday() != 6 and 9 <= agora.hour < fechamento:
        return f"A loja está aberta e atende até as {fechamento}h."

    dia_de_volta = agora.date() + timedelta(days=1) if agora.hour >= 9 else agora.date()
    if dia_de_volta.weekday() == 6:
        dia_de_volta += timedelta(days=1)

    # Do jeito que uma pessoa falaria: hoje, amanhã ou "segunda (09/11)"
    if dia_de_volta == agora.date():
        retorno = "hoje"
    elif dia_de_volta == agora.date() + timedelta(days=1):
        retorno = "amanhã"
    else:
        retorno = f"{DIAS_DA_SEMANA[dia_de_volta.weekday()]} ({dia_de_volta:%d/%m})"

    # Só o fato: quando e como falar do horário fica no prompt
    return f"A loja está fechada e volta a atender {retorno} às 9h."


def montar_prompt(agora: datetime | None = None) -> str:
    """Prompt com a data e a hora de agora. Refeito a cada chamada ao modelo."""
    agora = agora or datetime.now(FUSO_DA_LOJA)
    contexto = f"Hoje é {DIAS_DA_SEMANA[agora.weekday()]}, {agora:%d/%m/%Y, %H:%M}. {situacao_da_loja(agora)}"
    return PROMPT_DO_SISTEMA.format(agora=contexto)
