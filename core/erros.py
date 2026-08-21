class ErroCarregamento(Exception):
    pass

class ArquivoIlegivel(ErroCarregamento):
    def __init__(self, nome: str):
        super().__init__(f"Não foi possível ler o arquivo {nome}.")


class ArquivoVazio(ErroCarregamento):
    def __init__(self, nome: str):
        super().__init__(f"O arquivo {nome} está vazio.")
