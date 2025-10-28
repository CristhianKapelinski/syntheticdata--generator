import csv
import io
from typing import List, Dict, Any

def converter_para_csv_string(
    dados: List[Dict[str, Any]],
    nomes_colunas: List[str],
    delimitador: str = ",",
    separadorDecimal: str = "."
) -> str:
    """
    Converte uma lista de dicionários em uma string formatada como CSV (RF04, RF09).

    Usa um buffer de string em memória (StringIO) para construir o CSV.
    """
    # io.StringIO() é um buffer de texto em memória.
    # Funciona como um arquivo, mas sem tocar no disco.
    buffer = io.StringIO()

    # Usamos DictWriter para escrever o CSV a partir dos dicionários
    # 'fieldnames' garante a ordem correta das colunas
    # Adiciona o delimitador configurável
    writer = csv.DictWriter(buffer, fieldnames=nomes_colunas, delimiter=delimitador)

    # Escreve o cabeçalho (nomes das colunas)
    writer.writeheader()

    # Escreve todas as linhas de dados
    for linha in dados:
        linha_processada = {}
        for chave, valor in linha.items():
            if isinstance(valor, float):
                # Substitui o separador decimal padrão por um configurável
                linha_processada[chave] = str(valor).replace('.', separadorDecimal)
            else:
                linha_processada[chave] = valor
        writer.writerow(linha_processada)

    # Pega o valor completo do buffer como uma string
    return buffer.getvalue()
