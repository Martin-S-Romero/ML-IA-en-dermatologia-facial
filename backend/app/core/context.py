from contextvars import ContextVar

# Almacena el ID del usuario autenticado en la solicitud actual
# Útil para inyectarlo en la base de datos para RLS (Row Level Security)
current_user_id: ContextVar[str] = ContextVar("current_user_id", default="")
