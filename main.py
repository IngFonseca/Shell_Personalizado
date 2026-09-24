"""Punto de entrada: python main.py"""
import sys

try:
    from controllers.shell_controller import ShellController
    from models.sistema import ServicioSistema
    from views.consola_view import ConsolaView
except ModuleNotFoundError as e:
    print(f"Falta una dependencia: {e.name}")
    print("Instálalas con:  pip install -r requirements.txt")
    sys.exit(1)


def main() -> None:
    ShellController(ServicioSistema(), ConsolaView()).ejecutar()


if __name__ == "__main__":
    main()