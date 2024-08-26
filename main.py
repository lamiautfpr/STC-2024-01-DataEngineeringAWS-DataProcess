import os
import logging
import pandas as pd
from typing import List
from dotenv import load_dotenv

# Definindo o nível de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregando o arquivo de variaveis de ambiente
load_dotenv()

# 1. Padronizar o nome das colunas: minúsculas e sem espaços
def padronizar_nomes_colunas(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Função para padronizar os nomes das colunas:
    - Converte todos os nomes para minúsculas.
    - Substitui espaços por underlines.
    - Corrige erros específicos de nomenclatura, como 'resourse_type' para 'resource_type'.

    Parâmetros:
    dataframe (pd.DataFrame): O dataframe cujas colunas serão padronizadas.

    Retorno:
    pd.DataFrame: O dataframe com os nomes das colunas padronizados e corrigidos.
    """
    # Converte os nomes das colunas para minúsculas e substitui espaços por underlines
    dataframe.columns = [col.lower().replace(' ', '_') for col in dataframe.columns]

    # Corrige o erro de nomenclatura específico da coluna 'resourse_type'
    dataframe.rename(columns={'resourse_type': 'resource_type'}, inplace=True)

    return dataframe

# 2. Tratar valores nulos na coluna 'resource_type'
def valores_nulos(dataframe: pd.DataFrame, column:str, subs_val:any) -> pd.DataFrame:
    """
    Função para identificar e substituir valores nulos em uma coluna específica de um dataframe.
    Os valores nulos são identificados e substituídos pelo valor definido em `subs_val`.

    Parâmetros:
    dataframe (pd.DataFrame): O dataframe que será analisado.
    column (str): O nome da coluna onde os valores nulos serão substituídos.
    subs_val (any): O valor que será utilizado para substituir os valores nulos.

    Retorno:
    pd.DataFrame: O dataframe com os valores nulos substituídos na coluna especificada.
    """
    # Este é apenas um processo simples, temos diversas tecnicas possiveis de acordo com o caso de uso
    dataframe[column] = dataframe[column].fillna(subs_val)
    return dataframe

# 3. Identificar colunas com múltiplos valores separados por vírgula
def identificar_colunas_multivalor(dataframe: pd.DataFrame) -> List[str]:
    """
    Função para identificar colunas que contêm múltiplos valores separados por vírgula.
    Um valor é considerado multivalor se:
    - O valor for uma string.
    - A string contiver uma vírgula.

    Parâmetros:
    dataframe (pd.DataFrame): O dataframe que será analisado para identificar colunas multivalor.

    Retorno:
    List[str]: Uma lista com os nomes das colunas que contêm múltiplos valores separados por vírgula.
    """
    colunas_multivalor = []
    for coluna in dataframe.columns:
        # Verifica se há algum valor na coluna que seja uma string contendo vírgula
        if dataframe[coluna].apply(lambda x: isinstance(x, str) and ',' in x).any():
            colunas_multivalor.append(coluna)
    return colunas_multivalor

# 4. Aplicar one-hot encoding para as colunas identificadas
def one_hot_encoding_multivalor(dataframe: pd.DataFrame, colunas_multivalor: List[str]) -> pd.DataFrame:
    """
    Função para realizar one-hot encoding em colunas com múltiplos valores separados por vírgula.
    Para cada coluna identificada:
    - Separa os valores em diferentes colunas, criando colunas dummy.
    - Renomeia as colunas dummy para incluir o nome da coluna original como prefixo.
    - Remove a coluna original após a codificação.

    Parâmetros:
    dataframe (pd.DataFrame): O dataframe que será transformado pelo one-hot encoding.
    colunas_multivalor (List[str]): Lista com os nomes das colunas que contêm múltiplos valores para codificação.

    Retorno:
    pd.DataFrame: O dataframe atualizado com as colunas originais substituídas por colunas dummy.
    """
    for coluna in colunas_multivalor:
        # Criar colunas dummy a partir dos valores separados por vírgula
        dummies = dataframe[coluna].str.get_dummies(sep=',')
        # Renomear as colunas dummy para incluir o nome da coluna original como prefixo
        dummies.columns = [f"{coluna}_{col.lower()}" for col in dummies.columns]
        # Concatenar as colunas dummy ao dataframe original
        dataframe = pd.concat([dataframe, dummies], axis=1)
        # Remover a coluna original após a codificação
        dataframe.drop(columns=[coluna], inplace=True)
    return dataframe

# Aplicar os processos necessarios reagindo a um evento de put no bucket S3, esta função é necessaria pois o lambda funciona por ela como padrão
def lambda_handler(event, context):
    """
    Função principal que será executada pela AWS Lambda em resposta a eventos.

    Parâmetros:
    event (dict): Dados do evento que acionou a função. Por exemplo, detalhes do arquivo S3.
    context (object): Informações de contexto sobre a execução da função.

    O objetivo desta função é carregar um arquivo CSV de um bucket S3, e realizar operações
    definidas no código, como padronização de nomes de colunas e tratamento de dados.
    """

    # Carrega as variáveis de ambiente
    BUCKET = event['Records'][0]['s3']['bucket']['name']
    OBJECT_PREFIX = event['Records'][0]['s3']['object']['key']

    # Define variaveis importantes
    READ_PATH = f's3://{BUCKET}/{OBJECT_PREFIX}'
    WRITE_PATH = f's3://{BUCKET}/{OBJECT_PREFIX}'.replace('datalake','datawarehouse')

    # Imprime as variáveis de ambiente para debug
    logger.info(f'Read Path: {READ_PATH}')
    logger.info(f'Write Path: {WRITE_PATH}')

    # O try except é bem especifico pois estamos lidando com varios participantes e cada um pode ter um erro diferente.
    try:

        # Ler o objeto do bucket como um dataframe, o pandas permite isso caso estejamos devidamente logados no AWS CLI
        df = pd.read_csv(READ_PATH)

        logger.info(f'Objeto carregado com sucesso! | colunas: {df.columns.tolist}')

        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= APLICA O PROCESSAMENTO -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

        # 1. Padronizar nomes de colunas
        df = padronizar_nomes_colunas(df)

        # 2. Tratar valores nulos
        df = valores_nulos(df, 'resource_type', 'NoResource')

        # 3. Identificar colunas com múltiplos valores separados por vírgula
        colunas_multivalor = identificar_colunas_multivalor(df)

        # 4. Aplicar one-hot encoding para as colunas identificadas
        df = one_hot_encoding_multivalor(df, colunas_multivalor)

        # Salvar o dataframe processado em um novo arquivo CSV
        df.to_csv(WRITE_PATH, index=False)

        logger.info(f"Processamento concluído! Arquivo salvo em {WRITE_PATH}| Colunas: {df.columns.tolist()}")
        print(f"Processamento concluído! Arquivo salvo em {WRITE_PATH}")

    except FileNotFoundError as e:
        # Captura específica do erro NoSuchKey
        print(f"Erro: A chave especificada ({READ_PATH}) não existe: {e}")
        # Trate o erro conforme necessário (por exemplo, log, retorno padrão, etc.)

    except PermissionError as e:
        print(f"Erro de credenciais: {e}")
        # Tratar erro de credenciais

    except Exception as e:
        # Captura de qualquer outro tipo de exceção
        print(f"Erro inesperado: {e.__str__()}")
        # Trate o erro conforme necessário