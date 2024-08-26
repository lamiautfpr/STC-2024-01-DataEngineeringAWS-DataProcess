<h1 align="center">
  <br>
  <a href="https://www.lamia.sh.utfpr.edu.br/">
    <img src="https://user-images.githubusercontent.com/26206052/86039037-3dfa0b80-ba18-11ea-9ab3-7e0696b505af.png" alt="LAMIA - Laboratório de                  Aprendizagem de Máquina e Imagens Aplicados à Indústria" width="400"></a>
<br> <br>
Pipeline AWS com Docker e Lambda


</h1>
<p align="center">
  <a href="https://www.lamia-edu.com/">
    <img src="https://img.shields.io/badge/Follow-Lab%20Page-blue" alt="Lab">
  </a> 
</p>

<p align="center">
<b>Equipe:</b>  
<br>
Thiago Naves <a href="https://github.com/tfnaves" target="_blank"> (Naves, T. F.)</a> - Coordenador   <br>
Erik Henrique dos Santos Nascimento <a href="https://www.linkedin.com/in/erik-henrique-177388234/" target="_blank">(Nascimento, E. H. S.)</a> - Membro <br>
Felipe Lapa Nascimento <a href="https://www.linkedin.com/in/felipelapadn/" target="_blank">(Felipe, L. N.)</a> - Gerente
</p>

<p align="center">  
<b>Grupo</b>: <a href="https://www.lamia.sh.utfpr.edu.br/" target="_blank">LAMIA - Laboratório de Aprendizado de Máquina e Imagens Aplicados à Indústria </a> <br>
<b>Email</b>: <a href="mailto:lamia-sh@utfpr.edu.br" target="_blank">lamia-sh@utfpr.edu.br</a> <br>
<b>Organização</b>: <a href="http://portal.utfpr.edu.br" target="_blank">Universidade Tecnológica Federal do Paraná</a> <a href="http://www.utfpr.edu.br/campus/santahelena" target="_blank"> - Campus Santa Helena</a> <br>
</p>

<p align="center">
<br>
Status do Projeto: Em fase de teste :warning:
</p>

# Resumo

Este repositório contém o código e as instruções para configurar e executar um pipeline simples na AWS, utilizando Python, Docker, AWS Lambda, e AWS S3. O objetivo desta prática é permitir que você aprenda a integrar diferentes serviços da AWS para automatizar o processamento de dados.

## Visão Geral

![Pipeline Overview](./assets/pipeline-overview.png)

## Componentes do Pipeline

1. **Data Sources**: Fonte dos arquivos que serão processados.
2. **Amazon S3**: Armazenamento de arquivos que ativará o pipeline.
3. **AWS Lambda**: Função que processará os arquivos.
4. **Docker**: Imagem Docker usada para rodar o código na Lambda.
5. **Amazon ECR**: Repositório para armazenar a imagem Docker.
6. **Buckets DL e DW**: Buckets de destino no S3 para armazenamento dos dados processados.

## Pré-requisitos / Tecnologias

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas e configuradas no seu computador:

- **Git**: Para clonar este repositório.
- **Docker**: Para construir e rodar a imagem Docker.
- **AWS CLI**: Para interagir com os serviços da AWS.
- **PyCharm** (ou outro editor de código): Para editar e gerenciar o código.
- **Conta AWS**: Acesse a conta AWS fornecida ou crie a sua própria.

## Passo a Passo

### 1. Clonar o Repositório

Primeiro, clone este repositório para o seu computador:

```bash
git clone https://github.com/seu-usuario/nome-do-repo.git  
cd nome-do-repo
```

### 2. Construir a Imagem Docker

Em seguida, construa a imagem Docker que será usada na função Lambda:

```bash
docker build -t nome-da-imagem .
```

### 3. Configurar o AWS CLI
para interagir com a AWS via linha de comandos precisamos utilizar a CLI ( Command Line Interface ) disponibilizada pela propria AWS
```bash
aws configure
```

### 4. Fazer o Push da Imagem para o ECR

Agora, faça o push da imagem Docker para o Amazon ECR (São varios passos, então sumarizamos com um Makefile :

1. **Autentique o Docker no ECR**:
2. **Crie o repositório no ECR**:
3. **Marque a imagem e faça o push para o ECR**:

```bash
make ecr
```

### 5. Configurar a Função Lambda

1. **Alterar a Função Lambda do seu usuario**:
   - No console da AWS, vá para o serviço Lambda.
   - Em “Funções” selecione a lambda com seu nome de usuário
   - Abra a seção "imagem" e escolha "implantar nova imagem".
   - Selecione a imagem que você acabou de fazer o push para o ECR.

2. **Configurar o Trigger**: 
   - Clique em “Adicionar gatilho”
   - Adicione um trigger do tipo S3 para ativar a Lambda quando um arquivo for carregado em um bucket específico.
   - Preencha as informações
     - `Bucket: data-engineering-setac`
     - `Tipos de evento: marque o evento “PUT” apenas`
     - `Prefixo: seu_username/datalake/lol_`
     - `Sufixo: .parquet`
   - Assinale a caixinha de reconhecimento do risco das funções recursivas
   - Finalize a criação

### 5. Testar o Pipeline

1. Faça o upload de um arquivo de teste no bucket S3 configurado.  
2. Verifique se a função Lambda foi acionada e processou o arquivo corretamente.  
3. Confira o arquivo processado no bucket de destino (DL ou DW).

## Conclusão

Este pipeline demonstra como integrar Docker, Lambda e S3 na AWS para criar um processo automatizado de processamento de dados

---

**Happy coding!** 🚀
