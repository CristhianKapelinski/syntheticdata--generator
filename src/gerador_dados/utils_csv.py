import csv
import io
from typing import List, Dict, Any

def converter_para_csv_string(dados: List[Dict[str, Any]], nomes_colunas: List[str]) -> str:
    """
    Converte uma lista de dicionários em uma string formatada como CSV (RF04).
    
    
    Usa um buffer de string em memória (StringIO) para construir o CSV.
    """
    # io.StringIO() é um buffer de texto em memória.
    # Funciona como um arquivo, mas sem tocar no disco.
    buffer = io.StringIO()
    
    # Usamos DictWriter para escrever o CSV a partir dos dicionários
    # 'fieldnames' garante a ordem correta das colunas
    writer = csv.DictWriter(buffer, fieldnames=nomes_colunas)
    
    # Escreve o cabeçalho (nomes das colunas)
    writer.writeheader()
    
    # Escreve todas as linhas de dados
    writer.writerows(dados)
    
    # Pega o valor completo do buffer como uma string
    return buffer.getvalue()
