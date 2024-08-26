# Usar a imagem base fornecida pela AWS para funções Lambda Python
FROM public.ecr.aws/lambda/python:3.12

# Copiar o restante do código da aplicação
COPY . ${LAMBDA_TASK_ROOT}

# Instalar dependências (se houver um requirements.txt)
RUN pip install -r requirements.txt

# Executar a aplicação
CMD ["main.lambda_handler"]
