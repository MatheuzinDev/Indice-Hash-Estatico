class ErroCarregamento(Exception):
    pass

class ArquivoIlegivel(ErroCarregamento):
    def __init__(self, nome: str):
        super().__init__(f"Não foi possível ler o arquivo {nome}.")


class ArquivoVazio(ErroCarregamento):
    def __init__(self, nome: str):
        super().__init__(f"O arquivo {nome} está vazio.")


class ErroTamanhoPagina(Exception):
    pass


class TamanhoPaginaVazio(ErroTamanhoPagina):
    def __init__(self):
        super().__init__("Informe o tamanho da página.")


class TamanhoPaginaNaoNumerico(ErroTamanhoPagina):
    def __init__(self, texto: str):
        super().__init__(f"'{texto}' não é um número inteiro.")


class TamanhoPaginaInvalido(ErroTamanhoPagina):
    def __init__(self, tamanho: int):
        super().__init__(f"O tamanho da página deve ser maior que zero, mas veio {tamanho}.")
