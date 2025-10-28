from .modelos import ConfiguracaoCSV, ConfiguracaoColuna, TipoGeradorConfig
from .geradores import GeradorDados, GeradorRegex, GeradorGaussiano


def get_gerador(config_gerador: TipoGeradorConfig) -> GeradorDados:
    """
    Factory Function.
    Recebe uma configuração de gerador e retorna a instância
    correta do gerador (Strategy).
    """
    if config_gerador.tipoGerador == "regex":
        return GeradorRegex(config_gerador)
    elif config_gerador.tipoGerador == "gaussiano":
        return GeradorGaussiano(config_gerador)
    else:
        # Isso não deve acontecer se a validação do Pydantic (Fase 1)
        # estiver funcionando.
        raise ValueError(f"Tipo de gerador desconhecido: {config_gerador.tipoGerador}")


class SistemaGerador:
    """
    Serviço orquestrador que gerencia o processo de geração de dados.
    (Equivalente ao 'SistemaGerador' do Diagrama de Classes)
    
    """
    def __init__(self, config: ConfiguracaoCSV):
        self.config = config
        # Cria a lista de geradores (Strategies) usando a Factory
        self.geradores_por_coluna: list[GeradorDados] = [
            get_gerador(col.configGerador) for col in self.config.colunas
        ]
        # Armazena os nomes das colunas
        self.nomes_colunas: list[str] = [col.nome for col in self.config.colunas]

    def gerar_dados(self) -> list[dict]:
        """
        Gera a lista completa de dados em memória (RF01).
        
        
        Retorna:
            Uma lista de dicionários (ex: [{'col1': val1}, {'col1': val2}])
        """
        dados_gerados = []
        for _ in range(self.config.numLinhas):
            linha = {}
            # Itera sobre os nomes das colunas e seus respectivos geradores
            for nome_col, gerador in zip(self.nomes_colunas, self.geradores_por_coluna):
                linha[nome_col] = gerador.gerarValor()
            dados_gerados.append(linha)
        return dados_gerados
