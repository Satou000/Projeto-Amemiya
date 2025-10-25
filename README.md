API de Processamento de Formulários com Google Document AI

Este projeto consiste em uma API Flask (Python) projetada para receber imagens de formulários, processá-las usando a API Google Document AI para extrair dados estruturados (campos de texto e checkboxes) e, em seguida, armazenar esses dados em um banco de dados MySQL.

Visão Geral do Fluxo

Um cliente (como um aplicativo front-end) envia uma imagem (ex: JPG, PNG, PDF) para o endpoint /api/upload da API.

O servidor Flask recebe o arquivo.

A imagem é enviada para um Processador específico do Google Document AI.

A IA do Google analisa a imagem, extrai os campos de texto e o status dos checkboxes.

A API recebe os dados extraídos, limpa-os e formata-os.

Os dados limpos são salvos em uma tabela (formularios) em um banco de dados MySQL.

A API retorna uma resposta JSON indicando sucesso ou falha.

Tecnologias Utilizadas

Python: Linguagem principal do backend.

Flask: Micro-framework web para criar a API.

Google Document AI: Serviço de IA do Google Cloud para extração de dados de documentos.

MySQL: Banco de dados relacional para armazenar os dados extraídos.

mysql-connector-python: Driver Python para conectar ao MySQL.

python-dotenv: Para gerenciamento de variáveis de ambiente.

--- Configuração do Ambiente ---

Siga os passos abaixo para configurar e executar o projeto localmente.

1. Pré-requisitos

Python 3.8 ou superior

Uma conta do Google Cloud com o Document AI ativado.

Um Processador de Document AI treinado e seu ID.

Um arquivo de credenciais JSON do Google Cloud (Service Account).

Um servidor de banco de dados MySQL acessível.

2. Instalação

Clone este repositório:

git clone <url-do-seu-repositorio>
cd <nome-do-repositorio>


Crie e ative um ambiente virtual (recomendado):

python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate


Instale as dependências. Crie um arquivo requirements.txt com o seguinte conteúdo:

flask
google-cloud-documentai
mysql-connector-python
python-dotenv


Em seguida, instale-o:

pip install -r requirements.txt


3. Variáveis de Ambiente

Crie um arquivo chamado .env na raiz do projeto. Este arquivo armazenará suas credenciais e configurações sensíveis.

# --- Configuração do Google Cloud ---

# Caminho para o seu arquivo JSON de credenciais do Service Account
# Ex: C:\Users\SeuUsuario\Desktop\google-credentials.json
GOOGLE_APPLICATION_CREDENTIALS="caminho/para/seu/arquivo.json"

# Informações do Processador do Document AI
PROJECT_ID="seu-project-id-do-gcp"
LOCATION="us" # ou a localização do seu processador
PROCESSOR_ID="seu-processor-id"

# --- Configuração do Banco de Dados MySQL ---
DB_HOST="localhost"
DB_PORT="3306"
DB_USER="root"
DB_PASSWORD="sua_senha_segura"
DB_NAME_ONLINE="nome_do_seu_banco"


4. Estrutura do Banco de Dados

Você precisa de uma tabela no seu banco de dados MySQL que corresponda aos dados que estão sendo inseridos. A consulta INSERT no script espera a seguinte estrutura de tabela (os tipos de dados são sugestões):

CREATE TABLE IF NOT EXISTS formularios (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Campos do Cabeçalho
    Data DATE NULL,
    Item VARCHAR(255) NULL,
    QntPecas VARCHAR(100) NULL,
    Maquina VARCHAR(100) NULL,
    Setor VARCHAR(100) NULL,
    NomeCracha VARCHAR(255) NULL,
    
    -- Campos de Não Conformidade (Checkboxes)
    Montagem BOOLEAN DEFAULT FALSE,
    Regulagem BOOLEAN DEFAULT FALSE,
    MarcaRetifica BOOLEAN DEFAULT FALSE,
    Empenamento BOOLEAN DEFAULT FALSE,
    FalhaRaio BOOLEAN DEFAULT FALSE,
    FalhaZinco BOOLEAN DEFAULT FALSE,
    Rebarba BOOLEAN DEFAULT FALSE,
    Batida BOOLEAN DEFAULT FALSE,
    Risco BOOLEAN DEFAULT FALSE,
    Trepidacao BOOLEAN DEFAULT FALSE,
    Ressalto BOOLEAN DEFAULT FALSE,
    Oxidacao BOOLEAN DEFAULT FALSE,

    -- Campos de Dimensão
    DiametroInt BOOLEAN DEFAULT FALSE,
    DiametroIntDimensao VARCHAR(100) NULL,
    DiametroExt BOOLEAN DEFAULT FALSE,
    Comprimento BOOLEAN DEFAULT FALSE,
    ComprimentoDimensao VARCHAR(100) NULL,
    DimensaoMaior BOOLEAN DEFAULT FALSE,
    Menor BOOLEAN DEFAULT FALSE,
    Outros BOOLEAN DEFAULT FALSE,
    OutrosDescricao TEXT NULL,
    Observacoes TEXT NULL,
    
    -- Data de registro (Opcional, mas recomendado)
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


Como Executar

Com o ambiente virtual ativado e o arquivo .env configurado, inicie o servidor Flask:

python seu_script.py 
# (ou o nome que você deu ao arquivo, ex: app.py)

O servidor estará em execução em http://0.0.0.0:5000/.

Uso da API

Endpoint: POST /api/upload

Este é o único endpoint disponível, usado para enviar uma imagem para processamento.

Método: POST

Tipo de Conteúdo: multipart/form-data

Corpo da Requisição:
A requisição deve conter um campo imagem com o arquivo do formulário (ex: .png, .jpg, .pdf).

Exemplo de Resposta (Sucesso):

{
  "status": "sucesso",
  "dados_lidos": {
    "Data": "25/10/24",
    "Item": "Peça Exemplo 123",
    "QntPecas": "10",
    "Maquina": "Torno-05",
    "Setor": "Usinagem",
    "NomeCracha": "João Silva",
    "Montagem": false,
    "Regulagem": true,
    "MarcaRetifica": false,
    "Empenamento": false,
    "FalhaRaio": false,
    "FalhaZinco": false,
    "Rebarba": true,
    "Batida": false,
    "Risco": false,
    "Trepidacao": false,
    "Ressalto": false,
    "Oxidacao": false,
    "DiametroInt": false,
    "DiametroIntDimensao": null,
    "DiametroExt": true,
    "Comprimento": false,
    "ComprimentoDimensao": null,
    "DimensaoMaior": false,
    "Menor": false,
    "Outros": false,
    "OutrosDescricao": null,
    "Observacoes": "Peça com rebarba e regulagem fora."
  }
}


Exemplo de Resposta (Erro):

{
  "status": "erro",
  "mensagem": "Descrição detalhada do erro que ocorreu."
}
