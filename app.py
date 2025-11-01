import os
import mysql.connector
from flask import Flask, request, jsonify
from google.cloud import documentai_v1 as documentai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configurações
app = Flask(__name__)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

# Informações do Processador do Google Document IA
PROJECT_ID = 'projeto-amemiya'
LOCATION = 'us'
PROCESSOR_ID = '98b736a0b757dd27'

# Banco de dados MySQL:
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT', 3306)
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME_ONLINE = os.environ.get('DB_NAME_ONLINE')

# Conecta com a API do Google Cloud e cria o Path do processador
def processar_documento(imagem_bytes, mime_type_enviado):
    print(f"Enviando para o Google Document AI como {mime_type_enviado}...")
    client = documentai.DocumentProcessorServiceClient()
    projeto_amemiya = client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

    # Configurar para enviar a imagem ao Google
    documento_formatado = documentai.RawDocument(
        content=imagem_bytes,
        mime_type=mime_type_enviado
    )
    request_google = documentai.ProcessRequest(name=projeto_amemiya, raw_document=documento_formatado)

    # Envia de fato para o Google e espera a resposta
    resultado = client.process_document(request=request_google)
    print("Processando...")
    dados_limpos = {}

    print("Resposta recebida! Limpando os dados...")

    # Loop para campos de texto do formulário:
    for entity in resultado.document.entities:

        nome_da_etiqueta = entity.type_ #Nome do campo do formulário
        valor_preenchido_formulario = entity.mention_text #Valor de o operador anotou
        
        #Trata as desformatações do texto extraído
        valor_preenchido_tratado = valor_preenchido_formulario.replace('\n', ' ').strip()
        
        print(f"IA leu TEXTO: {nome_da_etiqueta} = {valor_preenchido_tratado}")
        dados_limpos[nome_da_etiqueta] = valor_preenchido_tratado

    # Loop para os campos tipo checkbox do formulário:
    for checkbox in resultado.document.form_fields:

        nome_da_etiqueta = checkbox.field_name.text #Nome do campo do formulário
        status = checkbox.field_value.text #Valor que o operador flegou
        
        if status == 'checked':
             print(f"CHECKBOX: {nome_da_etiqueta} = MARCADO")
             dados_limpos[nome_da_etiqueta] = True
        else:
             dados_limpos[nome_da_etiqueta] = False
    
    return dados_limpos

# Armazenar dados no banco de dados
def salvar_no_banco(dados):
    print("Salvando no banco de dados online...")
    conn = None
    cursor = None
    try:
        # Tenta se conectar usando as novas variáveis de configuração
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME_ONLINE
        )
        cursor = conn.cursor()

        #Tratar valor do tipo data:
        data_string_crua = dados.get('Data')
        data_para_banco = None

        if data_string_crua:
            try:
                data_objeto = datetime.strptime(data_string_crua, "%d/%m/%y")
                data_para_banco = data_objeto.strftime("%Y-%m-%d")
            except ValueError:
                print(f"Erro ao converter data: '{data_string_crua}'. Salvando como Nulo.")
                data_para_banco = None

       #Nome dos campos do document IA
        valores = (
            #Campos cabeçalho
            data_para_banco,
            dados.get('Item'),
            dados.get('QntPecas'),
            dados.get('Maquina'),
            dados.get('Setor'),
            dados.get('NomeCracha'),

            #Campos não conformidade
            dados.get('Montagem', False),
            dados.get('Regulagem', False),
            dados.get('MarcaRetifica', False),
            dados.get('Empenamento', False),
            dados.get('FalhaRaio', False),
            dados.get('FalhaZinco', False),
            dados.get('Rebarba', False),
            dados.get('Batida', False), 
            dados.get('Risco', False),
            dados.get('Trepidacao', False),
            dados.get('Ressalto', False),
            dados.get('Oxidacao', False),

            #Campos Dimensão
            dados.get('DiametroInt', False),
            dados.get('DiametroIntDimensao'),
            dados.get('DiametroExt', False),
            dados.get('DiametroExtDimensao'),
            dados.get('Comprimento', False),
            dados.get('ComprimentoDimensao'),
            dados.get('DimensaoMaior', False),
            dados.get('Menor', False),
            dados.get('Outros', False),
            dados.get('OutrosDescricao'),
            dados.get('Observacoes')
        )

        # No SQL
        sql = """
        INSERT INTO formularios (
            -- Colunas do cabeçalho
            Data, 
            Item,
            QntPecas,
            Maquina,
            Setor,
            NomeCracha,
            
            -- Colunas de não conformidade
            Montagem,
            Regulagem,
            MarcaRetifica,
            Empenamento,
            FalhaRaio,
            FalhaZinco,
            Rebarba,
            Batida, 
            Risco,
            Trepidacao,
            Ressalto,
            Oxidacao,

            -- Colunas de Dimensão
            DiametroInt,
            DiametroIntDimensao,
            DiametroExt,
            Comprimento,
            ComprimentoDimensao,
            DimensaoMaior,
            Menor,
            Outros,
            OutrosDescricao,
            Observacoes
        ) VALUES (
            %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        cursor.execute(sql, valores)
        conn.commit()
        print("Salvo com sucesso no banco de dados online!")

    except Exception as e:
        print(f"Erro ao salvar no banco online: {e}")
        if conn:
            conn.rollback()
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Conexão com o front-end
@app.route('/api/upload', methods=['POST'])
def handle_upload():
    print("Requisição recebida")
    try:
        #Arquivo do front, lê os bytes da imagem e verifica qual o tipo dela
        imagem_file = request.files['imagem']
        imagem_bytes = imagem_file.read() 
        mime_type_real = imagem_file.mimetype 
        print(f"O arquivo enviado é do tipo: {mime_type_real}")

        #Manda a imagem para o seu processador e manda os dados para o banco
        dados_processados = processar_documento(imagem_bytes, mime_type_real)
        salvar_no_banco(dados_processados)

        return jsonify({"status": "sucesso", "dados_lidos": dados_processados}), 200

    except Exception as e:
        print(f"Erro ao processar: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

#Iniciar o programa
if __name__ == '__main__':
    print("Iniciando o servidor...")
    app.run(debug=True, host='0.0.0.0', port=5000)