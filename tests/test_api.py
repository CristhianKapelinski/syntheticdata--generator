import json
from fastapi.testclient import TestClient
from src.gerador_dados.main import app

client = TestClient(app)

def test_gerar_csv_caminho_feliz():
    """
    Testa o 'caminho feliz' da API, enviando uma configuração válida
    e esperando um CSV como resposta.
    """
    # Carrega a configuração de exemplo válida
    with open("config/exemplo.json", "r") as f:
        config_valida = json.load(f)

    response = client.post("/gerar-csv", json=config_valida)

    # Verifica se a requisição foi bem-sucedida
    assert response.status_code == 200
    # Verifica se o tipo de conteúdo é CSV
    assert "text/csv" in response.headers["content-type"]
    # Verifica se o arquivo vem como anexo para download
    assert "attachment" in response.headers["content-disposition"]

    # Verifica o conteúdo do CSV
    content = response.text
    lines = content.strip().split('\r\n')
    
    # Verifica se temos 101 linhas (1 cabeçalho + 100 de dados)
    assert len(lines) == 101
    # Verifica o cabeçalho
    assert lines[0] == "ID_USUARIO,PONTUACAO_RISCO"


def test_falha_validacao_regex_invalida():
    """
    Testa a falha de validação para uma expressão regular com sintaxe inválida.
    Espera um status HTTP 422 Unprocessable Entity.
    """
    config_invalida = {
        "numLinhas": 10,
        "colunas": [{
            "nome": "TESTE_FALHA",
            "configGerador": {
                "tipoGerador": "regex",
                "expressao": "([A-Z"  # Parêntese não fechado
            }
        }]
    }

    response = client.post("/gerar-csv", json=config_invalida)

    # O FastAPI retorna 422 para erros de validação do Pydantic
    assert response.status_code == 422
    # Verifica se a mensagem de erro contém a causa da falha
    assert "Expressão regular com sintaxe inválida" in response.text


def test_falha_validacao_desvio_padrao_negativo():
    """
    Testa a falha de validação para um desvio padrão negativo.
    Espera um status HTTP 422 Unprocessable Entity.
    """
    config_invalida = {
        "numLinhas": 10,
        "colunas": [{
            "nome": "TESTE_FALHA_2",
            "configGerador": {
                "tipoGerador": "gaussiano",
                "media": 100,
                "desvioPadrao": -5.0  # Valor negativo
            }
        }]
    }

    response = client.post("/gerar-csv", json=config_invalida)

    # O FastAPI retorna 422 para erros de validação do Pydantic
    assert response.status_code == 422
    # Verifica se a mensagem de erro indica que o input deve ser > 0
    assert "Input should be greater than 0" in response.text


def test_gerar_csv_com_gerador_linear():
    """
    Testa a geração de CSV com o novo gerador linear.
    """
    config = {
        "numLinhas": 5,
        "colunas": [
            {
                "nome": "SEQUENCIA",
                "configGerador": {
                    "tipoGerador": "linear",
                    "valorInicial": 100,
                    "incremento": 10
                }
            }
        ]
    }

    response = client.post("/gerar-csv", json=config)

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]

    content = response.text
    lines = content.strip().split('\r\n')

    assert len(lines) == 6  # 1 cabeçalho + 5 linhas
    assert lines[0] == "SEQUENCIA"
    assert lines[1] == "100.0"
    assert lines[2] == "110.0"
    assert lines[3] == "120.0"
    assert lines[4] == "130.0"
    assert lines[5] == "140.0"
