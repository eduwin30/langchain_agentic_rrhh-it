from langchain.tools import tool

@tool("listar_beneficios")
def listar_beneficios(query: str = "") -> str:
    """
    Lista los beneficios disponibles para empleados.
    """
    beneficios = [
        "Medios días libres",
        "Licencia por fallecimiento de familiar directo",
        "Licencia por casamiento",
        "Día de cumpleaños libre",
        "Permiso por maternidad/paternidad",
        "Seguro de salud",
        "Bonos por desempeño"
    ]
    return "Beneficios disponibles:\n- " + "\n- ".join(beneficios)

@tool("reiniciar_contrasena")
def reiniciar_contrasena(username: str) -> str:
    """
    Simula el reinicio de contraseña para un usuario.
    """
    return f"La contraseña del usuario '{username}' ha sido reiniciada exitosamente. El usuario recibirá un correo con instrucciones para establecer una nueva contraseña."

@tool("alta_usuario")
def alta_usuario(username: str) -> str:
    """
    Simula el alta de un usuario en el sistema IT.
    """
    return f"El usuario '{username}' ha sido dado de alta en el sistema IT. Recibirá un correo con sus credenciales de acceso."

@tool("consultar_vacaciones")
def consultar_vacaciones(username: str) -> str:
    """
    Simula la consulta de días de vacaciones disponibles para un usuario.
    """
    # Simulación: siempre devuelve 12 días disponibles
    return f"El usuario '{username}' tiene 12 días de vacaciones disponibles."

@tool("consultar_licencias")
def consultar_licencias(username: str) -> str:
    """
    Simula la consulta de licencias disponibles para un usuario.
    """
    licencias = [
        "Licencia por maternidad/paternidad",
        "Licencia por enfermedad",
        "Licencia por casamiento",
        "Licencia por fallecimiento de familiar directo"
    ]
    return f"Licencias disponibles para '{username}':\n- " + "\n- ".join(licencias)
