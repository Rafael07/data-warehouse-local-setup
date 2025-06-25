# Usar Python 3.12.8 para manter consistência com o projeto
FROM python:3.12.8-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para CSVs se necessário
RUN mkdir -p /app/seeds_api

# Expor porta 8000
EXPOSE 8000

# Comando para iniciar a API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

