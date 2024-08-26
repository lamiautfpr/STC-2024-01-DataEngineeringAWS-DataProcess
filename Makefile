# Makefile para construir e gerenciar uma imagem e conteiner Docker para Python com a tag yubb

# Traz as variaveis de ambiente do arquivo .env
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Variaveis
CONTAINER_NAME = $(USER)_python

all: vars docker

# Construir a imagem Docker
docker: vars
	@echo "Construindo a imagem Docker..."
	@docker build \
	--build-arg AWS_ACCESS_KEY_ID=$(AWS_ACCESS_KEY_ID) \
	--build-arg AWS_SECRET_ACCESS_KEY=$(AWS_SECRET_ACCESS_KEY) \
	--build-arg AWS_REGION=$(AWS_REGION) \
	-t $(USER) .

# Executar o conteiner Docker
run:
	@echo "Executando o conteiner Docker..."
	@docker run -d --name $(CONTAINER_NAME) $(USER)
	#@docker exec -it $(CONTAINER_NAME) /bin/bash
	@docker logs -f $(CONTAINER_NAME)

# Limpar imagens e conteineres Docker
clean:
	@echo "Limpando imagens e conteineres Docker..."
	@docker stop $(CONTAINER_NAME)
	@echo "Removendo o conteiner Docker..."
	@docker rm $(CONTAINER_NAME)
	@echo "Removendo a imagem Docker..."
	@docker rmi $(USER)

# Enviar a imagem para o ECR
ecr: docker
	@echo "Enviando imagem $(USER) para o ECR (Elastic Container Registry)..."

	@aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_USER_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

	@docker tag $(USER):latest ${AWS_USER_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/$(REPOSITORY_NAME):$(USER)
	@docker push ${AWS_USER_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/$(REPOSITORY_NAME):$(USER)

# Executar o script Python para carregar variaveis de ambiente e exportar para um arquivo
vars:
	@echo "==================USER CONFIGS============================"
	@echo "USER=${USER}"
	@ECHO "BUCKET=${BUCKET}"
	@echo "===================AWS CONFIGS ==========================="
	@echo "AWS_REGION=${AWS_REGION}"
	@echo "AWS_USER=${AWS_USER}"
	@echo "AWS_USER_ID=${AWS_USER_ID}"
	@echo "=========================================================="
