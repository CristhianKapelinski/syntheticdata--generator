# Gerador de Dados Sintéticos Flexível

Este projeto implementa uma API FastAPI para a geração flexível de dados sintéticos, baseada em configurações definidas pelo usuário. A API permite gerar dados seguindo diferentes padrões (Regex, Distribuição Gaussiana, Tendência Linear) e exportá-los em formato CSV, com opções de personalização de delimitadores e separadores decimais.

## Funcionalidades (Requisitos Implementados)

-   **RF01: Definir Estrutura do CSV:** O usuário pode definir o número de linhas e as colunas do CSV, especificando o tipo de gerador para cada coluna.
-   **RF02: Gerador de Dados Regex:** Geração de strings baseadas em expressões regulares.
-   **RF03: Gerador de Dados Gaussianos:** Geração de números com base em uma distribuição normal (média e desvio padrão).
-   **RF04: Exportar para CSV:** Os dados gerados são exportados em formato CSV.
-   **RF05: Validação de Configurações:** Todas as configurações são validadas usando Pydantic, garantindo a integridade dos dados de entrada (ex: regex válida, desvio padrão positivo).
-   **RF06: Gerador de Dados Lineares:** Geração de números com base em uma tendência linear (valor inicial e incremento).
-   **RF09: Delimitadores e Separadores Decimais:** Personalização do delimitador de colunas e do separador decimal no arquivo CSV.

## Arquitetura

O projeto segue uma arquitetura limpa e desacoplada, utilizando Padrões de Projeto como:
-   **Data Transfer Object (DTO):** Modelos Pydantic para validação e tipagem das configurações.
-   **Strategy Pattern:** Para os diferentes tipos de geradores de dados (Regex, Gaussiano, Linear).
-   **Factory Method:** Para instanciar o gerador correto com base na configuração.
-   **Service Layer:** Uma camada de serviço (`SistemaGerador`) que orquestra a geração dos dados.

## Configuração do Ambiente

Para configurar o ambiente de desenvolvimento, siga os passos:

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/CristhianKapelinski/syntheticdata--generator
    cd syntheticdata--generator
    ```

2.  **Crie e ative o ambiente virtual com Poetry:**
    ```bash
    python3 -m venv .venv
    .venv/bin/pip install poetry
    .venv/bin/poetry install
    ```

3.  **Instale as dependências:**
    ```bash
    .venv/bin/poetry install
    ```

## Como Executar a API

Para iniciar o servidor FastAPI:

```bash
.venv/bin/poetry run uvicorn src.gerador_dados.main:app --reload
```

A API estará disponível em `http://127.0.0.1:8000`.

## Documentação da API (Swagger UI)

Acesse a documentação interativa da API em seu navegador:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Como Usar a API (Exemplo)

Você pode usar o endpoint `POST /gerar-csv` para gerar dados. O corpo da requisição deve ser um JSON que segue a estrutura definida nos modelos Pydantic.

**Exemplo de `config/exemplo.json`:**

```json
{
  "numLinhas": 100,
  "colunas": [
    {
      "nome": "ID_USUARIO",
      "configGerador": {
        "tipoGerador": "regex",
        "expressao": "USER_[A-Z0-9]{8}"
      }
    },
    {
      "nome": "PONTUACAO_RISCO",
      "configGerador": {
        "tipoGerador": "gaussiano",
        "media": 150.5,
        "desvioPadrao": 25.0
      }
    },
    {
      "nome": "SEQUENCIA_LINEAR",
      "configGerador": {
        "tipoGerador": "linear",
        "valorInicial": 10,
        "incremento": 0.5
      }
    }
  ],
  "delimitador": ";",
  "separadorDecimal": ","
}
```



    *   Exemplo: `123e4567-e89b-12d3-a456-426614174000`

## Exemplos de Expressões Regulares

Aqui estão alguns exemplos de expressões regulares que você pode usar para gerar dados sintéticos:

*   **CPF (Cadastro de Pessoas Físicas):**
    *   Regex: `\d{3}\.\d{3}\.\d{3}-\d{2}`
    *   Exemplo: `123.456.789-00`

*   **CEP (Código de Endereçamento Postal):**
    *   Regex: `\d{5}-\d{3}`
    *   Exemplo: `12345-678`

*   **Endereço IPv4:**
    *   Regex: `^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)`
    *   Exemplo: `192.168.0.1`

*   **Endereço de E-mail:**
    *   Regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
    *   Exemplo: `exemplo@dominio.com`

*   **Número de Telefone (Brasil, com DDD):**
    *   Regex: `\(\d{2}\)\s\d{4,5}-\d{4}`
    *   Exemplo: `(11) 98765-4321`

*   **Data (dd/mm/aaaa):**
    *   Regex: `^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}`
    *   Exemplo: `25/12/2024`

*   **UUID (Universally Unique Identifier):**
    *   Regex: `^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}`
    *   Exemplo: `123e4567-e89b-12d3-a456-426614174000`

## Testes

Para executar a suíte de testes automatizados (unitários e de integração):

```bash
.venv/bin/poetry run pytest
```

## Próximos Passos (Evolução)

-   Implementação de novas distribuições de dados (RF08).
-   Melhorias na interface do usuário ou na experiência do desenvolvedor.
