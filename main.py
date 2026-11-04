"""Agente de atendimento da Empório da Música no terminal.

Uso: python main.py
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langchain_core.messages import ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from contexto import montar_prompt
from ferramentas import FERRAMENTAS

SAUDACAO = "Oi! Sou o assistente virtual da Empório da Música. Como posso ajudar?"
COMANDOS_DE_SAIDA = {"sair", "exit", "quit"}


@dynamic_prompt
def prompt_com_horario(request: ModelRequest) -> str:
    # Refeito a cada chamada ao modelo para a data e a hora ficarem certas
    return montar_prompt()


def criar_agente(chave: str, modelo: str):
    # Erros temporários da API (como 429 ou 503) são repetidos até 5 vezes
    llm = ChatGoogleGenerativeAI(model=modelo, google_api_key=chave, temperature=0.2, timeout=30, max_retries=5)
    # O checkpointer guarda a conversa inteira, inclusive as consultas, para o modelo reaproveitar os dados
    return create_agent(llm, tools=FERRAMENTAS, middleware=[prompt_com_horario], checkpointer=InMemorySaver())


def limpar_texto(texto: str) -> str:
    # Às vezes o modelo usa markdown, e no terminal apareceriam os asteriscos
    linhas = texto.replace("**", "").split("\n")
    return "\n".join("- " + linha[2:].strip() if linha.startswith("* ") else linha for linha in linhas).strip()


def ferramentas_usadas(mensagens: list) -> list[str]:
    return [mensagem.name for mensagem in mensagens if isinstance(mensagem, ToolMessage)]


def main() -> int:
    # Sem isso os acentos podem dar erro no terminal do Windows
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

    load_dotenv(Path(__file__).parent / ".env")
    chave = os.getenv("GOOGLE_API_KEY")
    if not chave:
        print("Defina GOOGLE_API_KEY no arquivo .env (veja .env.example).")
        return 1

    agente = criar_agente(chave, os.getenv("LLM_MODEL", "gemini-3.1-flash-lite"))
    config = {"configurable": {"thread_id": "atendimento"}}  # identifica a conversa na memória
    mensagens_vistas = 0  # para saber quais mensagens são novas a cada resposta

    print(f"Empório da Música: {SAUDACAO}\n(digite 'sair' para encerrar)\n")
    while True:
        try:
            mensagem = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEmpório da Música: Até mais!")
            return 0
        if not mensagem:
            continue
        if mensagem.lower() in COMANDOS_DE_SAIDA:
            print("Empório da Música: Valeu pelo contato. Até mais!")
            return 0

        try:
            resultado = agente.invoke({"messages": [{"role": "user", "content": mensagem}]}, config=config)
        except KeyboardInterrupt:
            print("\nEmpório da Música: Até mais!")
            return 0
        except Exception as erro:
            # Se der erro na API, o programa continua e o cliente pode tentar de novo
            print(f"Empório da Música: Tive um problema técnico. Pode tentar de novo? [{type(erro).__name__}]\n")
            continue

        mensagens = resultado["messages"]
        usadas = ferramentas_usadas(mensagens[mensagens_vistas:])
        mensagens_vistas = len(mensagens)
        if usadas:
            print(f"  [consultou: {', '.join(usadas)}]")

        # No Gemini 3 o conteúdo pode vir em blocos; .text junta só o texto
        texto = limpar_texto(mensagens[-1].text or "")
        print(f"Empório da Música: {texto or 'Não consegui responder agora. Pode reformular?'}\n")


if __name__ == "__main__":
    sys.exit(main())
