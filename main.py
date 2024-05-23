from src.models.app_vacaciones import App_Vacaciones


def main():
    import warnings
    warnings.filterwarnings("ignore")
    app = App_Vacaciones()
    app.crear_app()


if __name__ == "__main__":
    main()