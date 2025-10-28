## 1. 📜 Visão Geral do Projeto

O sistema "Gerador de Dados Sintéticos Flexível" foi implementado como uma aplicação web full-stack, composta por um backend robusto em **Python 3.11+** e um frontend reativo.

* **Backend:** Utiliza o framework **FastAPI** para servir uma API RESTful (`/gerar-csv`) e a interface do usuário. A lógica de negócios é claramente separada em camadas de serviço, geração e validação.
* **Frontend:** A interface é construída com **HTML** e **Bootstrap** (para layout) e é tornada dinâmica através do **Alpine.js**. Esta abordagem cria uma experiência de usuário rica e reativa (semelhante a uma SPA, *Single Page Application*), permitindo a adição e remoção de colunas dinamicamente sem recarregar a página.

A solução foca na **extensibilidade** e **manutenibilidade**, implementando com sucesso não apenas os requisitos essenciais (MVP), mas também a maioria dos requisitos "Should Have" e "Could Have", como a geração linear e a configuração de delimitadores.

## 2. 🏛️ Arquitetura da Solução e Tecnologias

O projeto é estruturado seguindo uma arquitetura em camadas clara, que isola as responsabilidades e promove alta coesão e baixo acoplamento.

### 2.1. Camada de API e Controle (`main.py`)

* **Tecnologia:** **FastAPI**.
* **Responsabilidade:** Define os *endpoints* da aplicação.
    * `GET /`: Serve a interface do usuário (`index.html`) usando o motor de templates Jinja2.
    * `POST /gerar-csv`: Recebe a configuração do usuário em formato JSON.
* **Integração com Pydantic:** O FastAPI utiliza o `modelos.py` para validar automaticamente **todo** o payload JSON recebido. Se uma configuração for inválida (ex: `desvioPadrao` negativo ou `expressao` com sintaxe incorreta), a API retorna automaticamente um erro `HTTP 422 Unprocessable Entity`, o que cumpre integralmente o **RF05**.
* **Resposta:** Orquestra a chamada para a camada de serviço e, ao final, retorna os dados como um arquivo `text/csv` para download (cumprindo **RF04**).

### 2.2. Camada de Modelos e Validação (`modelos.py`)

* **Tecnologia:** **Pydantic**.
* **Responsabilidade:** Define a "fonte da verdade" para todas as estruturas de dados.
    * `ConfiguracaoCSV`: Define a estrutura geral, incluindo `numLinhas`, `delimitador`, `separadorDecimal` e uma lista de `colunas`.
    * `ConfigGerador...`: Define as configurações específicas para cada tipo de gerador (Regex, Gaussiano, Linear).
    * **Validação (RF05):** Esta camada implementa o **RF05** de forma proativa usando os tipos do Pydantic (ex: `PositiveInt`, `PositiveFloat`) e validadores customizados (`@field_validator`) para verificar a sintaxe das expressões regulares.

### 2.3. Camada de Serviço e Orquestração (`servicos.py`)

* **Tecnologia:** Python puro.
* **Responsabilidade:** Contém a lógica de negócios principal, desacoplando a API da lógica de geração.
    * `SistemaGerador`: Atua como o orquestrador central. Ele recebe a `ConfiguracaoCSV`, inicializa os geradores corretos (usando a *Factory*) e executa o loop principal para gerar os dados.
    * `get_gerador`: Implementa o padrão *Factory*, decidindo qual objeto gerador instanciar com base no `tipoGerador` da configuração.

### 2.4. Camada de Geração de Dados (`geradores.py`)

* **Tecnologia:** Python, **Numpy** e **rstr**.
* **Responsabilidade:** Implementa a lógica real de geração de cada tipo de dado.
    * `GeradorDados`: Classe base abstrata que define o contrato (`gerarValor()`).
    * `GeradorRegex`: Usa `rstr.xeger` para gerar strings baseadas em regex (cumprindo **RF02**).
    * `GeradorGaussiano`: Usa `numpy.random.normal` para gerar números com distribuição normal (cumprindo **RF03**).
    * `GeradorLinear`: Mantém um estado interno (`valor_atual`) para gerar uma sequência linear (cumprindo **RF06**).

### 2.5. Camada de Serialização (`utils_csv.py`)

* **Tecnologia:** Módulo `csv` nativo do Python.
* **Responsabilidade:** Converte os dados gerados (uma lista de dicionários Python) em uma string formatada como CSV.
* **Recursos:** Utiliza `csv.DictWriter` para garantir que as colunas sejam escritas na ordem correta e aplica os `delimitador` e `separadorDecimal` personalizados (cumprindo **RF09**).

### 2.6. Camada de Visualização (View) (`index.html`)

* **Tecnologia:** HTML, **Bootstrap**, **Alpine.js**.
* **Responsabilidade:** Fornece a interface gráfica do usuário (GUI), cumprindo o **RNF01**.
* **Reatividade:** O Alpine.js (`x-data="configuracaoForm()"`) gerencia o estado do formulário. Funções como `adicionarColuna()` e `removerColuna()` manipulam o estado, e o Alpine.js atualiza o DOM automaticamente.
* **Comunicação:** A função `submeterFormulario` usa a `fetch` API nativa do navegador para enviar o estado como JSON para o backend (`/gerar-csv`) e processar a resposta, seja ela um erro de validação (JSON) ou um arquivo CSV para download.

## 3. 🧩 Análise de Padrões de Design (Design Patterns)

A arquitetura do projeto é fortemente baseada em padrões de design clássicos para garantir extensibilidade (**RF08**, **RNF07**) e manutenibilidade (**RNF06**).

### 3.1. Padrão Strategy (Estratégia)

Este é o padrão de design central da solução, usado para a geração de dados.

* **Interface (Strategy):** A classe abstrata `GeradorDados` em `geradores.py`. Ela define um método comum, `gerarValor()`, que todas as estratégias de geração devem implementar.
* **Estratégias Concretas (Concrete Strategies):** As classes `GeradorRegex`, `GeradorGaussiano` e `GeradorLinear`. Cada uma fornece uma implementação diferente para `gerarValor()`.
* **Contexto (Context):** A classe `SistemaGerador` em `servicos.py`. Ela *contém* uma lista de objetos Strategy (`self.geradores_por_coluna`). Quando `gerar_dados()` é chamado, o Contexto não sabe (nem precisa saber) *como* cada valor é gerado; ele apenas itera por seus geradores e chama `gerador.gerarValor()`.
* **Benefício:** Este padrão é a chave para cumprir o **RF08**. Para adicionar um novo tipo de gerador (ex: "Distribuição Uniforme"), um desenvolvedor só precisa:
    1.  Criar uma nova classe `GeradorUniforme(GeradorDados)`.
    2.  Atualizar a *Factory* (`get_gerador`) para reconhecê-la.
    *Nenhuma alteração é necessária no `SistemaGerador` ou `main.py`.*

### 3.2. Padrão Factory (Fábrica)

O Padrão Strategy é habilitado por uma *Factory Function* (Função de Fábrica).

* **Implementação:** A função `get_gerador(config_gerador)` em `servicos.py`.
* **Propósito:** Ela encapsula e centraliza a lógica de criação das "Estratégias Concretas". Ela recebe um objeto de configuração, lê o campo `tipoGerador` e retorna a instância correta (`GeradorRegex`, `GeradorGaussiano`, etc.).
* **Benefício:** Desacopla o `SistemaGerador` (o "Contexto") da criação dos objetos que ele utiliza, simplificando a manutenção.

### 3.3. Padrão Facade (Fachada)

* **Implementação:** A classe `SistemaGerador` também atua como uma Fachada.
* **Propósito:** Ela fornece uma interface simples e unificada (`gerar_dados()`) para um subsistema complexo (validação, fábricas, múltiplas estratégias, loops).
* **Benefício:** A camada de API (`main.py`) permanece extremamente simples. Ela não precisa saber sobre os detalhes dos geradores; ela apenas entrega a configuração para a "Fachada" (`SistemaGerador`) e pede os dados de volta.

### 3.4. Padrão Model-View-ViewModel (MVVM) no Frontend

O `index.html` com Alpine.js implementa uma versão leve do padrão MVVM.

* **Model:** Os dados brutos (o payload JSON que será enviado, ex: `this.numLinhas`, `this.colunas`).
* **View:** O HTML (`<form>`, `<input>`, `<select>`) que o usuário vê.
* **ViewModel:** O objeto Alpine.js (`configuracaoForm()`). Ele atua como o intermediário:
    * Expõe o *Model* para a *View* (ex: `x-model="coluna.nome"`).
    * Expõe ações (lógica da UI) para a *View* (ex: `@click="adicionarColuna()"`).
    * Contém a lógica de comunicação com o backend (`submeterFormulario`).

## 4. ✅ Análise de Requisitos (Implementado vs. Especificado)

Abaixo está um mapeamento detalhado de cada requisito do `Engenharia_de_software.pdf` para sua implementação no código.

### 4.1. Must Have (Essencial) - 100% Implementado

* **RF01: Definição da estrutura do CSV (linhas, colunas, nomes)**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** `modelos.py` (classe `ConfiguracaoCSV`) e `index.html` (campos "Número de Linhas" e formulário dinâmico de colunas).

* **RF02: Geração de dados com Regex**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** `geradores.py` (classe `GeradorRegex`) e `modelos.py` (classe `ConfigGeradorRegex`).

* **RF03: Geração de dados com distribuição Gaussiana**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** `geradores.py` (classe `GeradorGaussiano`) e `modelos.py` (classe `ConfigGeradorGaussiano`).

* **RF04: Exportação para arquivo CSV**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** `main.py` (retorna `StreamingResponse` com `media_type="text/csv"`) e `utils_csv.py` (função `converter_para_csv_string`).

* **RF05: Validação de configurações de entrada**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** `modelos.py` (uso de `PositiveFloat` para `desvioPadrao` e `@field_validator` para `expressao`). Os testes `test_falha_validacao_regex_invalida` e `test_falha_validacao_desvio_padrao_negativo` em `test_api.py` confirmam que a API retorna erros 422.

* **RNF01: Usabilidade mínima para operação**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** O `index.html` fornece uma GUI completa, muito acima de uma "usabilidade mínima" de linha de comando.

* **RNF03: Portabilidade entre sistemas operacionais**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** A solução é uma aplicação web baseada em Python, sendo inerentemente portátil (executa em Windows, Linux, macOS).

* **RNF04: Confiabilidade na geração dos dados**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** O uso de bibliotecas padrão da indústria (`numpy` para estatística, `rstr` para regex) e a cobertura de testes (`test_core.py`) garantem a confiabilidade.

### 4.2. Should Have (Importante) - 75% Implementado

* **RF06: Geração de dados com tendência linear**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** `geradores.py` (classe `GeradorLinear`) e `test_api.py` (teste `test_gerar_csv_com_gerador_linear`).

* **RF07: Combinação de colunas com tipos de dados diferentes**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** A arquitetura (Padrão Strategy) suporta isso nativamente. `SistemaGerador` armazena uma lista mista de geradores. O teste `test_gerar_csv_caminho_feliz` em `test_api.py` valida um CSV com três tipos diferentes.

* **RNF02: Meta de desempenho para 1 milhão de linhas**
    * **Status:** ❌ **Não Implementado (Risco Crítico).**
    * **Evidência:** A implementação atual é um **gargalo de memória**. `SistemaGerador.gerar_dados` cria uma lista Python completa em memória. `converter_para_csv_string` então cria uma *string* completa em memória. Isso causará um erro de *Out-of-Memory (OOM)* muito antes de 1 milhão de linhas. O requisito de desempenho não foi atendido.

* **RNF05: Segurança (não armazenamento de dados)**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** A aplicação opera "stateless" (sem estado). Ela não usa banco de dados e não armazena nenhuma configuração ou dado gerado no servidor.

### 4.3. Could Have (Desejável) - 100% Implementado

* **RF08: Suporte a distribuições estatísticas adicionais**
    * **Status:** ✅ **Implementado (Arquiteturalmente).**
    * **Evidência:** O uso dos padrões Strategy e Factory torna a adição de novos geradores trivial, cumprindo perfeitamente este requisito.

* **RF09: Configuração de delimitadores e separadores do CSV**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** Os campos `delimitador` e `separadorDecimal` estão no modelo `ConfiguracaoCSV`, no frontend `index.html`, e são usados em `utils_csv.py`. Os testes `test_gerar_csv_com_delimitador_personalizado` e `test_gerar_csv_com_separador_decimal_personalizado` provam a funcionalidade.

* **RNF06: Manutenibilidade (código modular e testes unitários)**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** A separação de arquivos por responsabilidade (`modelos`, `servicos`, `geradores`) e a presença de `test_core.py` (testes unitários) e `test_api.py` (testes de integração) cumprem este requisito.

* **RNF07: Escalabilidade (arquitetura extensível)**
    * **Status:** ✅ **Implementado.**
    * **Evidência:** Idêntico ao **RF08**. A arquitetura é o pilar da extensibilidade.

### 4.4. Won't Have (Fora do Escopo)

* **RF10 (Visualização), RF11 (Importação), RF12 (Imperfeições), RF13 (Outros formatos)**
    * **Status:** ✅ **Não Implementado (Corretamente).**
    * **Evidência:** Nenhum desses recursos foi implementado, conforme a priorização MOSCOW.

## 5. ⚙️ Fluxo de Dados: De Requisição a Download

Este é o fluxo completo de uma solicitação de geração de CSV:

1.  **Usuário (Frontend):** O usuário acessa a `GET /`. O FastAPI (`main.py`) renderiza o `index.html`.
2.  **Alpine.js (Frontend):** O `configuracaoForm()` é inicializado, gerenciando o estado do formulário. O usuário preenche os campos (ex: 50 linhas) e adiciona colunas (ex: `COL_A` (Regex) e `COL_B` (Linear)).
3.  **Fetch API (Frontend):** O usuário clica em "Gerar". A função `submeterFormulario` constrói um objeto JSON com o estado do formulário e envia uma `POST /gerar-csv`.
4.  **FastAPI/Pydantic (Backend):** O `main.py` recebe a requisição. O Pydantic (`modelos.py`) **valida automaticamente** o JSON.
    * *Cenário de Falha:* Se a regex em `COL_A` for inválida, o Pydantic levanta um erro. O FastAPI captura isso e retorna um `HTTP 422` com um JSON detalhando o erro. O frontend (`catch (error)`) recebe o 422, lê o JSON do erro e exibe a mensagem para o usuário.
5.  **Camada de Serviço (Backend):**
    * *Cenário de Sucesso:* A validação passa. O `main.py` instancia `SistemaGerador(config)`.
    * O `SistemaGerador.__init__` itera pelas colunas. Para `COL_A`, ele chama `get_gerador("regex", ...)`, que retorna um `GeradorRegex()`. Para `COL_B`, ele chama `get_gerador("linear", ...)`, que retorna um `GeradorLinear()`.
    * O `main.py` chama `gerador.gerar_dados()`.
    * `SistemaGerador` entra em um loop de 1 a 50. Em cada iteração, ele chama `gerarValor()` no `GeradorRegex` e `gerarValor()` no `GeradorLinear`, montando um dicionário de linha (ex: `{'COL_A': 'ABC', 'COL_B': 10.0}`).
    * Ao final, `gerar_dados()` retorna uma lista com 50 dicionários.
6.  **Serialização (Backend):** O `main.py` passa essa lista para `converter_para_csv_string()`, que a transforma em uma única string CSV.
7.  **Resposta (Backend):** O `main.py` coloca essa string em uma `StreamingResponse` e a envia com `Content-Disposition: attachment`, forçando o download.
8.  **Download (Frontend):** O `fetch` API recebe a resposta `HTTP 200`. Ele lê o `Blob` da resposta, cria uma URL de objeto local e simula um clique em um link, fazendo o navegador baixar o arquivo `dados_sinteticos.csv`.