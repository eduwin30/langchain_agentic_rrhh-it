import os
import json
import datetime
from dotenv import load_dotenv

# LangChain Core
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

# LangChain integrations
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI

# === Importa tus tools de RRHH/IT ===
from agentic.tools import (
    listar_beneficios,
    reiniciar_contrasena,
    alta_usuario,
    consultar_vacaciones,
    consultar_licencias,
)

# === Cargar variables de entorno ===
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Falta GOOGLE_API_KEY en las variables de entorno (.env)")

# === Prompt del sistema (ReAct + Transparencia) ===
SYSTEM_PROMPT = (
    "Eres un asistente inteligente de Recursos Humanos e IT para una empresa tecnológica. "
    "Ayudas a los empleados con beneficios, vacaciones, licencias, altas de usuario y soporte técnico. "
    "Usa razonamiento paso a paso (ReAct): analiza la consulta, decide si usar una herramienta, "
    "ejecútala si es necesario y luego genera una respuesta reflexiva, profesional y concisa. "
    "Cumple con la política de transparencia de IA: explica si una respuesta se basó en razonamiento o en una herramienta. "
    "Si una herramienta requiere un campo de usuario y no fue proporcionado, usa el nombre del usuario actual de la sesión. "
    "Nunca vuelvas a pedir el nombre del usuario salvo que falten datos críticos."
)

# === Carpeta para la memoria ===
MEMORIA_DIR = os.path.join(os.path.dirname(__file__), "memoria")
os.makedirs(MEMORIA_DIR, exist_ok=True)


# === Crear o recuperar historial de conversación ===
def get_history(session_id: str):
    filepath = os.path.join(MEMORIA_DIR, f"{session_id}.json")
    return FileChatMessageHistory(file_path=filepath)


# === Mapeo de tools ===
def as_tool_dict(tools):
    return {t.name: t for t in tools}

# === Completar automáticamente argumentos de usuario ===
USER_ARG_KEYS = ["usuario", "username", "user", "nombre", "empleado", "id_usuario"]


def enrich_tool_args_with_user(args: dict, user_id: str) -> dict:
    """Si la herramienta requiere campo de usuario y falta, lo completa con el nombre actual."""
    args = dict(args or {})
    if not any(k in args and args[k] for k in USER_ARG_KEYS):
        args.setdefault("usuario", user_id)
        args.setdefault("nombre", user_id)
    return args


# === MAIN ===
def main():
    print("🤖 Agente Gemini 2.5 Flash (RRHH & IT con arquitectura ReAct)")
    print("Escribe 'salir' para terminar.\n")

    # === 1. Identificación del usuario ===
    raw_name = input("Por favor ingresa tu nombre: ").strip() or "Usuario"
    user_name = raw_name.title()
    session_id = user_name.lower()

    # === 2. Inicializa modelo Gemini ===
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=GOOGLE_API_KEY,
        temperature=0.3,
        convert_system_message_to_human=True,
    )

    # === 3. Inicializa tools de RRHH e IT ===
    tools = [
        listar_beneficios,
        reiniciar_contrasena,
        alta_usuario,
        consultar_vacaciones,
        consultar_licencias,
    ]
    tool_by_name = as_tool_dict(tools)
    llm_with_tools = llm.bind_tools(tools)

    # === 4. Configura memoria persistente ===
    chat_history = get_history(session_id)
    if not chat_history.messages:
        chat_history.add_message(
            HumanMessage(
                content=(
                    f"Mi nombre es {user_name}. Soy empleado de la empresa y necesito asistencia en Recursos Humanos e IT."
                ),
                name=user_name,
            )
        )

    # === 5. Prompt estructurado con placeholders ===
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        MessagesPlaceholder(variable_name="messages"),
    ])

    chain = prompt | llm_with_tools

    # === 6. Agente con memoria persistente ===
    runnable = RunnableWithMessageHistory(
        chain,
        get_history,
        input_messages_key="messages",
        history_messages_key="history",
    )

    config = {"configurable": {"session_id": session_id}}
    MAX_TOOL_TURNS = 5

    # === 7. Ciclo principal (ReAct completo) ===
    while True:
        user_input = input(f"\n¿En qué puedo ayudarte hoy, {user_name}?: ").strip()
        if user_input.lower() == "salir":
            print(f"👋 Hasta pronto, {user_name}. ¡Gracias por usar el asistente!")
            break
        if not user_input:
            print("Por favor escribe una consulta.\n")
            continue

        messages = [HumanMessage(content=user_input, name=user_name)]

        # --- Ciclo ReAct (razona → actúa → observa → reflexiona) ---
        try:
            for _ in range(MAX_TOOL_TURNS):
                ai_msg: AIMessage = runnable.invoke({"messages": messages}, config=config)

                # Caso 1: respuesta directa sin tools
                if not getattr(ai_msg, "tool_calls", None):
                    try:
                        print(f"\n🤖 Respuesta: {ai_msg.content[0]['text']}\n")
                    except Exception as e:
                        print(f"\n⚠️ Error al mostrar la respuesta del agente: {e}\n")
                        print(f"Respuesta bruta: {ai_msg.content}\n")
                    break

                # Caso 2: llamada a herramientas
                tool_messages = []
                for tc in ai_msg.tool_calls:
                    name = tc.get("name")
                    args = enrich_tool_args_with_user(tc.get("args") or {}, user_name)
                    call_id = tc.get("id") or f"tool_call_{name}_{datetime.datetime.now().timestamp()}"

                    tool = tool_by_name.get(name)
                    if tool is None:
                        result = f"La herramienta '{name}' no está disponible."
                    else:
                        try:
                            result = tool.invoke(args)
                        except Exception as e:
                            result = f"Error al ejecutar {name}: {e}"

                    tool_msg = ToolMessage(
                        content=str(result),
                        name=name or "tool",
                        tool_call_id=call_id,
                    )
                    tool_messages.append(tool_msg)

                messages.extend(tool_messages)

            else:
                print("⚠️ Se alcanzó el límite de llamadas a herramientas para este turno.\n")
        except Exception as e:
            print(f"\n⚠️ Error inesperado en el ciclo del agente: {e}\n")

if __name__ == "__main__":
    main()
