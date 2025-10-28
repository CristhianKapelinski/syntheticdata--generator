import pytest
from unittest.mock import Mock
from src.gerador_dados.modelos import ConfigGeradorRegex, ConfigGeradorGaussiano, ConfigGeradorLinear, ConfiguracaoColuna, ConfiguracaoCSV
from src.gerador_dados.geradores import GeradorRegex, GeradorGaussiano, GeradorLinear
from src.gerador_dados.servicos import get_gerador, SistemaGerador
from src.gerador_dados.utils_csv import converter_para_csv_string

# Testes para as Strategies (Geradores)

def test_gerador_regex():
    """Testa o gerador de regex isoladamente."""
    config = ConfigGeradorRegex(expressao=r'\d{3}')
    gerador = GeradorRegex(config)
    valor = gerador.gerarValor()
    assert isinstance(valor, str)
    assert len(valor) == 3
    assert valor.isdigit()

def test_gerador_gaussiano():
    """Testa o gerador gaussiano isoladamente."""
    config = ConfigGeradorGaussiano(media=100, desvioPadrao=10)
    gerador = GeradorGaussiano(config)
    valor = gerador.gerarValor()
    assert isinstance(valor, float)


def test_gerador_linear():
    """Testa o gerador linear isoladamente."""
    config = ConfigGeradorLinear(valorInicial=10, incremento=2)
    gerador = GeradorLinear(config)
    assert gerador.gerarValor() == 10
    assert gerador.gerarValor() == 12
    assert gerador.gerarValor() == 14


# Teste para a Factory

def test_get_gerador_factory():
    """Testa a factory function 'get_gerador'."""
    config_regex = ConfigGeradorRegex(expressao='[a-z]')
    gerador_regex = get_gerador(config_regex)
    assert isinstance(gerador_regex, GeradorRegex)

    config_gaussiano = ConfigGeradorGaussiano(media=0, desvioPadrao=1)
    gerador_gaussiano = get_gerador(config_gaussiano)
    assert isinstance(gerador_gaussiano, GeradorGaussiano)

    config_linear = ConfigGeradorLinear(valorInicial=0, incremento=1)
    gerador_linear = get_gerador(config_linear)
    assert isinstance(gerador_linear, GeradorLinear)

    # Testa um tipo de gerador inválido (não deve acontecer na prática)
    with pytest.raises(ValueError):
        config_invalida = Mock()
        config_invalida.tipoGerador = "tipo_inexistente"
        get_gerador(config_invalida)

# Teste para o Service (Orquestrador)

def test_sistema_gerador():
    """Testa o serviço orquestrador 'SistemaGerador' com geradores mockados."""
    # Cria uma configuração de CSV para o teste
    config_csv = ConfiguracaoCSV(
        numLinhas=5,
        colunas=[
            ConfiguracaoColuna(
                nome="COL_A",
                configGerador=ConfigGeradorRegex(expressao="A")
            ),
            ConfiguracaoColuna(
                nome="COL_B",
                configGerador=ConfigGeradorGaussiano(media=1, desvioPadrao=1)
            )
        ]
    )

    # Instancia o sistema gerador (isso vai criar geradores reais)
    sistema = SistemaGerador(config_csv)

    # Mock dos geradores para ter um resultado previsível
    mock_gerador_a = Mock()
    mock_gerador_a.gerarValor.return_value = "VALOR_A"
    
    mock_gerador_b = Mock()
    mock_gerador_b.gerarValor.return_value = "VALOR_B"

    sistema.geradores_por_coluna = [mock_gerador_a, mock_gerador_b]

    # Gera os dados
    dados = sistema.gerar_dados()

    # Verifica o resultado
    assert len(dados) == 5  # Deve gerar 5 linhas
    assert dados[0] == {"COL_A": "VALOR_A", "COL_B": "VALOR_B"}
    assert dados[4] == {"COL_A": "VALOR_A", "COL_B": "VALOR_B"}

    # Verifica se os mocks foram chamados o número correto de vezes
    assert mock_gerador_a.gerarValor.call_count == 5
    assert mock_gerador_b.gerarValor.call_count == 5


def test_conversor_csv_string_delimitador_separador_customizados():
    """Testa o serializador CSV (Fase 4) com delimitador ';' e separador ',' (RF09)."""

    # 1. Arrange
    nomes_colunas = ["Produto", "Preco"]
    dados = [
        {"Produto": "Item A", "Preco": 123.45},
        {"Produto": "Item B; com ponto-e-virgula", "Preco": 9.99}
    ]

    # 2. Act
    csv_string = converter_para_csv_string(
        dados,
        nomes_colunas,
        delimitador=";",
        separadorDecimal=","
    )

    # 3. Assert
    linhas = csv_string.strip().split('\r\n')
    assert linhas[0] == 'Produto;Preco' # Delimitador ;
    assert linhas[1] == 'Item A;123,45' # Separador ,
    # O módulo CSV adiciona aspas se o delimitador estiver no campo
    assert linhas[2] == '"Item B; com ponto-e-virgula";9,99'
