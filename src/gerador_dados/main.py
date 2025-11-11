from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import io
import os

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

# Configura a pasta de templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(BASE_DIR, "..", "templates")
templates = Jinja2Templates(directory=templates_dir)

# Monta a pasta estática apenas se ela existir, para evitar erros na inicialização
static_dir = os.path.join(BASE_DIR, "..", "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve a página HTML principal."""
    # Passa o 'request' para o template, necessário pelo Jinja2Templates
    return templates.TemplateResponse("index.html", {"request": request})

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
