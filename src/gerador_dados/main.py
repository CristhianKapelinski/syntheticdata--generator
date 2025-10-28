from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import io

# Importa nossos modelos da Fase 1
from .modelos import ConfiguracaoCSV

# Importa nossos serviços das Fases 3 e 4
from .servicos import SistemaGerador
from .utils_csv import converter_para_csv_string

# Cria a instância principal da aplicação
app = FastAPI(
    title="Gerador de Dados Sintéticos Flexível",
    description="API para geração de dados sintéticos baseada na especificação de requisitos.",
    version="0.1.0 (MVP)"
)

@app.get("/")
async def root():
    """Endpoint de boas-vindas."""
    return {"message": "Bem-vindo ao Gerador de Dados Sintéticos. Use o endpoint /gerar-csv."}


@app.post("/gerar-csv")
async def gerar_csv(config: ConfiguracaoCSV):
    """
    Endpoint principal para gerar dados sintéticos.
    
    Recebe uma configuração JSON (validada pelo Pydantic 'config: ConfiguracaoCSV')
    e retorna um arquivo CSV (text/csv).
    """
    try:
        # 1. Instancia o serviço orquestrador (Fase 3)
        gerador = SistemaGerador(config)
        
        # 2. Gera os dados em memória (Fase 3)
        dados_gerados = gerador.gerar_dados()
        
        # 3. Converte os dados para uma string CSV (Fase 4)
        csv_string = converter_para_csv_string(
            dados_gerados,
            gerador.nomes_colunas,
            delimitador=config.delimitador,
            separadorDecimal=config.separadorDecimal
        )        
        # 4. Cria um buffer de 'bytes' para a resposta
        buffer = io.BytesIO(csv_string.encode("utf-8"))
        
        # 5. Retorna uma StreamingResponse
        # Isso permite ao navegador/cliente baixar o arquivo
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=dados_sinteticos.csv"
            }
        )

    except ValueError as ve:
        # Captura erros de lógica interna (ex: tipo de gerador desconhecido)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Captura quaisquer outros erros inesperados
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")
