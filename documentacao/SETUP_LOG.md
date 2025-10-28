# Log de Configuração do Projeto

Este arquivo documenta os passos executados para configurar o ambiente de desenvolvimento do projeto `syntheticdata-generator`.

## Fase 0: Fundação do Projeto

Seguindo o guia fornecido, as seguintes ações foram tomadas:

### 1. Estrutura de Diretórios
- Os seguintes diretórios foram criados:
  - `src/gerador_dados`
  - `tests`
  - `config`
- O arquivo `src/gerador_dados/__init__.py` foi criado para definir o pacote Python.

### 2. Ambiente Virtual e Poetry
- Devido ao erro `poetry: command not found`, um ambiente virtual Python foi criado em `.venv`.
- O `Poetry` foi instalado dentro do ambiente virtual `.venv`.

### 3. Inicialização do Projeto com Poetry
- O comando `poetry init` foi executado para criar o arquivo `pyproject.toml`.
- O arquivo `pyproject.toml` foi modificado para incluir a configuração `packages = [{include = "gerador_dados", from = "src"}]` na seção `[tool.poetry]`, para que o Poetry encontre o código-fonte do projeto.

### 4. Instalação de Dependências
- As dependências principais foram instaladas com `poetry add`:
  - `pydantic`
  - `numpy`
  - `rstr`
  - `typer`
- As dependências de desenvolvimento foram instaladas com `poetry add --group dev`:
  - `pytest`
  - `ruff`

### 5. Configuração do Ruff (Qualidade de Código)
- A configuração do `Ruff` para formatação e "linting" foi adicionada ao arquivo `pyproject.toml`.
- Ocorreu um erro ao executar `ruff format` devido a um problema de parsing da versão do Python no `pyproject.toml`.
- O campo `requires-python` foi alterado de `^3.11` para `>=3.11` para corrigir o erro.
- Os comandos `ruff format .` e `ruff check --fix .` foram executados com sucesso para garantir a qualidade e consistência do código.

## Mudança de Rota: Migração para API com FastAPI

Após a configuração inicial, o plano foi alterado para desenvolver uma API web com FastAPI em vez de uma ferramenta de linha de comando.

### Fase 0.5: Adaptando o Ambiente para FastAPI
- As seguintes dependências foram adicionadas para suportar a API:
  - `fastapi`
  - `uvicorn` (como dependência de desenvolvimento)
- A dependência `typer`, que seria usada para a CLI, foi removida.

### Fase 1: Modelagem e Validação de Dados (Pydantic)
- **Status: Concluída.**
- O módulo `src/gerador_dados/modelos.py`, criado na fase inicial, foi utilizado diretamente pelo FastAPI para validação das requisições, sem necessidade de alterações.
- Um arquivo de configuração de exemplo, `config/exemplo.json`, foi criado para ser usado nos testes.
- O script `modelos.py` foi executado para um teste manual, que validou com sucesso as configurações corretas e rejeitou as incorretas.

### Fase 2: Implementação dos Geradores (Strategy)
- O arquivo `src/gerador_dados/geradores.py` foi criado.
- Foram implementadas as classes `GeradorDados` (abstrata), `GeradorRegex` e `GeradorGaussiano`, seguindo o padrão de projeto Strategy para a lógica de geração de dados.

### Fase 3: Orquestrador e Fábrica
- O arquivo `src/gerador_dados/servicos.py` foi criado.
- Foi implementada a função `get_gerador` (Factory) para selecionar a estratégia de geração correta com base na configuração.
- A classe `SistemaGerador` foi criada para orquestrar todo o processo de geração de dados.

### Fase 4: Utilitário de Serialização CSV
- O arquivo `src/gerador_dados/utils_csv.py` foi criado.
- A função `converter_para_csv_string` foi implementada para converter os dados gerados em memória para uma string no formato CSV.

### Fase 5: Criação do Endpoint FastAPI
- O arquivo principal da API, `src/gerador_dados/main.py`, foi criado.
- A aplicação FastAPI foi instanciada.
- Foi implementado o endpoint `POST /gerar-csv`, que recebe a configuração, orquestra a geração dos dados e retorna o arquivo CSV para download.

### Fase 6: Testes (Manual e Automatizado)
- **Teste Manual:**
  - O servidor `uvicorn` foi iniciado para executar a aplicação.
  - Um teste de integração foi realizado utilizando `curl` para enviar uma requisição `POST` com o arquivo `config/exemplo.json` para o endpoint `/gerar-csv`.
  - A API retornou com sucesso um arquivo CSV, que foi salvo como `meu_arquivo_gerado.csv`.
  - A verificação do arquivo confirmou que ele continha 101 linhas (1 de cabeçalho e 100 de dados), validando o sucesso da implementação do MVP.
- **Testes Automatizados:**
  - A dependência `httpx` foi adicionada para suportar os testes de API.
  - O arquivo `tests/test_api.py` foi criado com testes de integração para a API, cobrindo tanto o caminho feliz quanto os casos de falha de validação.
  - O arquivo `tests/test_core.py` foi criado com testes unitários para a lógica de negócio (geradores, fábrica e serviço).
  - Um bug no teste `test_sistema_gerador` foi identificado e corrigido (o desvio padrão não pode ser zero).
  - A suíte de testes inicial (7 testes) foi executada com sucesso.

### Fase 7: Evolução - Gerador Linear (RF06)
- O modelo `ConfigGeradorLinear` foi adicionado ao `src/gerador_dados/modelos.py` e incluído na união `TipoGeradorConfig`.
- A nova estratégia `GeradorLinear` foi implementada em `src/gerador_dados/geradores.py`.
- A fábrica `get_gerador` em `src/gerador_dados/servicos.py` foi atualizada para instanciar o `GeradorLinear`.
- Testes unitários para o `GeradorLinear` e para a fábrica foram adicionados em `tests/test_core.py`.
- Um teste de integração para a API foi adicionado em `tests/test_api.py` para validar a geração de dados com o gerador linear.
- Todos os 9 testes da suíte foram executados e passaram com sucesso, confirmando a correta implementação da nova funcionalidade.

### Fase 8: Evolução - Delimitadores e Separadores Decimais (RF09)
- Os campos `delimitador` e `separadorDecimal` foram adicionados ao modelo `ConfiguracaoCSV` em `src/gerador_dados/modelos.py`.
- A função `converter_para_csv_string` em `src/gerador_dados/utils_csv.py` foi modificada para aceitar e utilizar os novos parâmetros de delimitador e separador decimal.
- O endpoint `gerar_csv` em `src/gerador_dados/main.py` foi atualizado para passar os valores de `delimitador` e `separadorDecimal` da configuração para a função de conversão CSV.
- Novos testes de integração foram adicionados em `tests/test_api.py` para validar a funcionalidade de delimitadores e separadores decimais personalizados.
- Um erro de indentação em `src/gerador_dados/main.py` foi corrigido.
- Um erro nos testes de API foi corrigido para refletir as mudanças no `config/exemplo.json` e o comportamento de citação de campos do `csv.DictWriter`.
- Todos os 11 testes da suíte foram executados e passaram com sucesso, confirmando a correta implementação da nova funcionalidade.

## Fase 9: Correções e Melhorias na Interface do Usuário

Nesta fase, foram realizadas correções de bugs e melhorias na interface do usuário para aprimorar a experiência de uso da aplicação.

-   **Correção do Download do CSV:** Foi corrigido um bug no arquivo `templates/index.html` que impedia o download do arquivo CSV gerado. O problema era que o elemento `<a>` de download era removido do DOM antes que o evento de clique pudesse ser disparado. A correção envolveu adicionar `a.click()` antes de `a.remove()`.

-   **Melhoria na Usabilidade do Campo Regex:** Para tornar o uso do gerador de regex mais intuitivo, foram feitas as seguintes melhorias no `templates/index.html`:
    -   Adicionado um `placeholder` ao campo de expressão regular com um exemplo de formato (`ex: \d{3}\.\d{3}\.\d{3}-\d{2}`).
    -   Incluído um texto descritivo abaixo do campo para guiar o usuário sobre a sintaxe de regex esperada (Python) e fornecer exemplos práticos como CPF e CEP.

-   **Correção da Configuração do Gerador Linear:** Foi identificado e corrigido um erro de incompatibilidade entre o frontend e o backend para o gerador linear. O formulário em `templates/index.html` enviava os campos `coeficienteAngular` and `coeficienteLinear`, enquanto o modelo Pydantic no backend esperava `incremento` e `valorInicial`. Os nomes dos campos e os rótulos no formulário foram atualizados para corresponder ao backend.

-   **Atualização da Documentação (README.md):** O arquivo `README.md` foi atualizado para incluir uma nova seção com exemplos de expressões regulares, como CPF, CEP, IPv4, e-mail, etc. Isso ajuda os usuários a entenderem como utilizar o gerador de regex de forma eficaz.

O projeto continua evoluindo com novas funcionalidades e cobertura de testes robusta.