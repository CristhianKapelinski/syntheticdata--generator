import re # Para validar a sintaxe da Expressão Regular
from typing import Literal, Union, Annotated

from pydantic import (
    BaseModel,
    Field,
    PositiveFloat,
    PositiveInt,
    field_validator
)

print("Módulo 'modelos.py' carregado.")

class ConfigGeradorRegex(BaseModel):
    """Configuração para dados baseados em Expressão Regular (RF02)."""
    tipoGerador: Literal["regex"] = "regex"
    expressao: str

    @field_validator("expressao")
    @classmethod
    def validar_sintaxe_regex(cls, v: str) -> str:
        """Valida se a string de regex é uma sintaxe válida (RF05)."""
        try:
            re.compile(v)
        except re.error as e:
            # A sintaxe da regex é inválida
            raise ValueError(f"Expressão regular com sintaxe inválida: {e}")
        return v


class ConfigGeradorGaussiano(BaseModel):
    """Configuração para dados de distribuição Gaussiana (RF03)."""
    tipoGerador: Literal["gaussiano"] = "gaussiano"
    media: float
    # Usamos PositiveFloat para garantir que o desvio padrão é > 0 (RF05)
    desvioPadrao: PositiveFloat


class ConfigGeradorLinear(BaseModel):
    """Configuração para dados com tendência linear (RF06)."""
    tipoGerador: Literal["linear"] = "linear"
    valorInicial: float
    incremento: float


# Este tipo especial usa o campo 'tipoGerador' para decidir
# qual modelo (Regex ou Gaussiano) deve ser usado para validar.
TipoGeradorConfig = Annotated[
    Union[ConfigGeradorRegex, ConfigGeradorGaussiano, ConfigGeradorLinear],
    Field(discriminator="tipoGerador")
]

class ConfiguracaoColuna(BaseModel):
    """Define uma única coluna no CSV."""
    nome: str
    # 'configGerador' usa nossa Union para validar os parâmetros
    # corretos baseado no 'tipoGerador' interno.
    configGerador: TipoGeradorConfig


class ConfiguracaoCSV(BaseModel):
    """Define a estrutura completa do arquivo CSV (RF01)."""
    # Garante que o número de linhas seja um inteiro > 0 (RF05)
    numLinhas: PositiveInt
    colunas: list[ConfiguracaoColuna]
    delimitador: str = ","
    separadorDecimal: str = "."

    @field_validator("colunas")
    @classmethod
    def pelo_menos_uma_coluna(cls, v: list) -> list:
        """Valida se a lista de colunas não está vazia (RF05)."""
        if not v:
            raise ValueError("O arquivo CSV deve ter pelo menos uma coluna.")
        return v

# --- Bloco de Teste Manual ---
# Este código só executa quando você roda: python src/gerador_dados/modelos.py
if __name__ == "__main__":
    import json

    print("\n--- Testando validação ---")

    # 1. Teste de Sucesso
    print("Teste 1: Carregando configuração válida...")
    try:
        # Carrega o JSON de exemplo que criamos
        with open("config/exemplo.json", "r") as f:
            dados_ok = json.load(f)

        # Tenta validar os dados
        config_validada = ConfiguracaoCSV.model_validate(dados_ok)
        print("SUCESSO! Configuração válida carregada.")
        # print(config_validada.model_dump_json(indent=2))

    except Exception as e:
        print(f"FALHA INESPERADA! Erro na configuração válida: {e}")

    # 2. Teste de Falha (Regex Inválida)
    print("\nTeste 2: Testando regex com sintaxe inválida (RF05)...")
    dados_regex_invalida = {
        "numLinhas": 10,
        "colunas": [{
            "nome": "TESTE_FALHA",
            "configGerador": {
                "tipoGerador": "regex",
                "expressao": "([A-Z" # Parêntese não fechado
            }
        }]
    }

    try:
        ConfiguracaoCSV.model_validate(dados_regex_invalida)
        print("FALHA! Deveria ter dado erro de validação de regex.")
    except Exception as e:
        print(f"SUCESSO! Erro de validação pego como esperado.")
        # print(e) # Descomente para ver o erro completo

    # 3. Teste de Falha (Desvio Padrão Inválido)
    print("\nTeste 3: Testando desvio padrão negativo (RF05)...")
    dados_desvio_invalido = {
        "numLinhas": 10,
        "colunas": [{
            "nome": "TESTE_FALHA_2",
            "configGerador": {
                "tipoGerador": "gaussiano",
                "media": 100,
                "desvioPadrao": -5.0 # Valor negativo
            }
        }]
    }

    try:
        ConfiguracaoCSV.model_validate(dados_desvio_invalido)
        print("FALHA! Deveria ter dado erro de desvio padrão.")
    except Exception as e:
        print(f"SUCESSO! Erro de validação pego como esperado (PositiveFloat).")
        # print(e) # Descomente para ver o erro completo
