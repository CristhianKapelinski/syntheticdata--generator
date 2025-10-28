import rstr
import numpy as np
from abc import ABC, abstractmethod
from typing import Any

# Importa nossos modelos de configuração da Fase 1
from .modelos import ConfigGeradorRegex, ConfigGeradorGaussiano, ConfigGeradorLinear

class GeradorDados(ABC):
    """Classe base abstrata (Interface) para todos os geradores."""
    @abstractmethod
    def gerarValor(self) -> Any:
        """Gera um único valor sintético."""
        pass


class GeradorRegex(GeradorDados):
    """Gera dados textuais com base em uma Expressão Regular (RF02)."""
    def __init__(self, config: ConfigGeradorRegex):
        self.expressao = config.expressao

    def gerarValor(self) -> str:
        """Gera uma string que corresponde à regex."""
        return rstr.xeger(self.expressao)


class GeradorGaussiano(GeradorDados):
    """Gera dados numéricos seguindo uma Distribuição Gaussiana (RF03)."""
    def __init__(self, config: ConfigGeradorGaussiano):
        self.media = config.media
        self.desvio = config.desvioPadrao

    def gerarValor(self) -> float:
        """Gera um número float da distribuição normal."""
        return float(np.random.normal(self.media, self.desvio))


class GeradorLinear(GeradorDados):
    """Gera dados com incremento linear a cada chamada (RF06)."""
    def __init__(self, config: ConfigGeradorLinear):
        self.valor_atual = config.valorInicial
        self.incremento = config.incremento

    def gerarValor(self) -> float:
        """Gera o próximo valor na sequência linear."""
        valor = self.valor_atual
        self.valor_atual += self.incremento
        return valor
