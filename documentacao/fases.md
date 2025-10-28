### 🏛️ Fase 0: Configuração do Ambiente e Arquitetura

* **Status:** ✅ **Concluída**
* **Objetivo:** Estabelecer a fundação técnica do projeto, garantindo profissionalismo e manutenibilidade.
* **O que foi feito:**
    * Criação da estrutura de diretórios (`src/gerador_dados`, `tests/`, `config/`).
    * Gerenciamento de dependências iniciado com `Poetry`.
    * Instalação das bibliotecas de produção (core): `pydantic`, `numpy`, `rstr`.
    * Instalação das bibliotecas de interface (API): `fastapi`.
    * Instalação das bibliotecas de desenvolvimento: `pytest`, `ruff` (para linting/formatação) e `uvicorn` (para servir a API).
    * Repositório `git` inicializado com `.gitignore`.

### 📦 Fase 1: Modelagem de Dados e Validação (DTO)

* **Status:** ✅ **Concluída**
* **Objetivo:** Implementar **RF01 (Definir Estrutura)** e **RF05 (Validar Configurações)** através de contratos de dados claros.
* **O que foi feito:**
    * Criação do módulo `src/gerador_dados/modelos.py`.
    * Definição dos modelos Pydantic que servem como "Data Transfer Objects" (DTOs):
        * `ConfigGeradorRegex` (para RF02)
        * `ConfigGeradorGaussiano` (para RF03)
        * `ConfiguracaoColuna` e `ConfiguracaoCSV` (para RF01).
    * Implementação de regras de validação (RF05) usando validadores do Pydantic (ex: `PositiveInt`) e customizados (ex: sintaxe de regex).
* **Padrão de Projeto:** **Data Transfer Object (DTO)**.

### 🏭 Fase 2: Implementação do Core - Geradores (Strategy)

* **Status:** ✅ **Concluída**
* **Objetivo:** Implementar a lógica de geração pura para os requisitos **RF02 (Regex)** e **RF03 (Gaussiano)**.
* **O que foi feito:**
    * Criação do módulo `src/gerador_dados/geradores.py`.
    * Definição da interface `GeradorDados (ABC)`.
    * Implementação das classes `GeradorRegex` e `GeradorGaussiano` como "estratégias" concretas.
* **Padrão de Projeto:** **Strategy Pattern (Padrão de Estratégia)**.

### ⚙️ Fase 3: Implementação do Core - Orquestrador (Service/Factory)

* **Status:** ✅ **Concluída**
* **Objetivo:** Criar a lógica de negócios que conecta os DTOs (Fase 1) aos Geradores (Fase 2).
* **O que foi feito:**
    * Criação do módulo `src/gerador_dados/servicos.py`.
    * Implementação da classe `SistemaGerador`, que atua como a **Camada de Serviço** (orquestra o processo).
    * Implementação da função `get_gerador()`, que atua como uma **Fábrica** (decide qual *Strategy* instanciar).
* **Padrões de Projeto:** **Service Layer**, **Factory Method** (Simple Factory).

### 💾 Fase 4: Implementação do Core - Serializador CSV

* **Status:** ✅ **Concluída**
* **Objetivo:** Implementar o **RF04 (Exportar para CSV)** de forma otimizada para uma API (em memória, sem acesso a disco).
* **O que foi feito:**
    * Criação do módulo `src/gerador_dados/utils_csv.py`.
    * Implementação da função `converter_para_csv_string`, que usa `io.StringIO` e o módulo `csv` para serializar os dados gerados (da Fase 3) em uma string formatada.

### 🚀 Fase 5: Implementação da Interface (API Endpoint)

* **Status:** ✅ **Concluída**
* **Objetivo:** Expor toda a funcionalidade do sistema através de uma interface web (API), substituindo a CLI (Fase 6 do plano original).
* **O que foi feito:**
    * Criação do módulo `src/gerador_dados/main.py`.
    * Instanciação do `app = FastAPI()`.
    * Implementação do endpoint `POST /gerar-csv` que:
        1.  Recebe o DTO `ConfiguracaoCSV` (da Fase 1) como *request body*.
        2.  Usa o `SistemaGerador` (da Fase 3) para gerar os dados.
        3.  Usa o `converter_para_csv_string` (da Fase 4) para serializar os dados.
        4.  Retorna os dados como um arquivo para download (`StreamingResponse`).

---

### 🧪 Fase 6: Testes Automatizados (Próxima Fase)

* **Status:** ✅ **Concluída**
* **Objetivo:** Garantir a **RNF04 (Confiabilidade)** do MVP, validando todas as camadas de forma automatizada.
* **O que será feito:**
    1.  Adicionar `httpx` como dependência de desenvolvimento (necessário para o `TestClient` do FastAPI).
    2.  Criar `tests/test_api.py` para testes de integração:
        * Testar o "caminho feliz" (enviar `config/exemplo.json` e esperar status 200 e um CSV válido).
        * Testar falhas de validação (enviar regex inválida ou desvio padrão negativo e esperar status 422).
    3.  Criar `tests/test_core.py` para testes unitários:
        * Testar as *Strategies* (`GeradorRegex`, `GeradorGaussiano`) isoladamente.
        * Testar a *Factory* (`get_gerador`).
        * Testar o *Service* (`SistemaGerador`) com dados "mockados".

### 📈 Fase 7: Evolução (Requisitos "Should Have")

* **Status:** ✅ **Concluída**
* **Objetivo:** Implementar requisitos de prioridade média, como **RF06 (Tendência Linear)** e **RF07 (Combinação de tipos)** (já suportado pela arquitetura).
* **O que será feito:**
    1.  **Modelos (Fase 1):** Adicionar `ConfigGeradorLinear` ao DTO `ConfiguracaoColuna`.
    2.  **Core (Fase 2):** Criar a nova *Strategy* `GeradorLinear(GeradorDados)`.
    3.  **Core (Fase 3):** Atualizar a *Factory* `get_gerador()` para instanciar a nova *Strategy*.
* **Padrões de Projeto:** Extensão dos padrões **Strategy** e **Factory**.

### ⚛️ Fase 8: Evolução (Requisitos "Could Have")

* **Status:** ✅ **Concluída**
* **Objetivo:** Implementar requisitos de baixa prioridade e preparar para extensibilidade futura, como **RF08 (Novas distribuições)** e **RF09 (Delimitadores)**.
* **O que será feito:**
    1.  **RF08:** Seguir o mesmo processo da Fase 7 (adicionar nova *Strategy* e atualizar *Factory*).
    2.  **RF09:**
        * Adicionar os campos `delimitador` e `separadorDecimal` ao DTO `ConfiguracaoCSV` (Fase 1).
        * Modificar o Serializador (Fase 4) para receber e usar esses parâmetros no `csv.DictWriter`.
* **Padrões de Projeto:** Extensão dos padrões **Strategy** e **Factory**.
