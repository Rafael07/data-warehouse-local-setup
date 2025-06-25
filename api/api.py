from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any
import uvicorn
from data_generator_api import gerar_dados_periodo, salvar_dados_csv

# Criar aplicação FastAPI
app = FastAPI(
    title="DW Data API",
    description="API para geração de dados incrementais para o Data Warehouse",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir acesso do Power BI e outras ferramentas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="Página inicial da API")
async def root():
    """Endpoint raiz com informações básicas da API."""
    return {
        "message": "DW Data API - Geração de dados incrementais",
        "version": "1.0.0",
        "endpoints": {
            "dados_periodo": "/dados/periodo",
            "dados_recentes": "/dados/recentes",
            "documentacao": "/docs"
        },
        "exemplo_uso": "/dados/periodo?data_inicio=2025-06-10&data_fim=2025-06-24"
    }

@app.get("/dados/periodo", summary="Gerar dados para período específico")
async def get_dados_periodo(
    data_inicio: date = Query(
        ..., 
        description="Data de início do período (YYYY-MM-DD)",
        example="2025-06-10"
    ),
    data_fim: date = Query(
        default=None,
        description="Data de fim do período (YYYY-MM-DD). Se não informada, usa data atual",
        example="2025-06-24"
    ),
    salvar_csv: bool = Query(
        default=False,
        description="Se True, salva os dados em arquivos CSV para integração com dbt"
    ),
    seed: Optional[int] = Query(
        default=None,
        description="Seed para reprodutibilidade dos dados (útil para testes)"
    )
) -> Dict[str, Any]:
    """
    Gera dados de cadastros e pedidos para um período específico.
    
    **Volumes gerados automaticamente:**
    - Cadastros: entre 2 e 20 (randomizado)
    - Pedidos: entre 40 e 90 (randomizado)
    
    **Retorna:**
    - Dados em formato JSON
    - Estatísticas do período
    - Opcionalmente salva em CSV para integração com dbt
    """
    
    try:
        # Validações
        if data_fim is None:
            data_fim = date.today()
        
        if data_inicio > data_fim:
            raise HTTPException(
                status_code=400, 
                detail="Data de início deve ser anterior à data de fim"
            )
        
        if data_inicio > date.today():
            raise HTTPException(
                status_code=400, 
                detail="Data de início não pode ser futura"
            )
        
        # Gerar dados
        dados = gerar_dados_periodo(
            data_inicio=data_inicio.isoformat(),
            data_fim=data_fim.isoformat(),
            seed=seed
        )
        
        # Salvar CSV se solicitado
        arquivos_csv = None
        if salvar_csv:
            arquivos_csv = salvar_dados_csv(dados)
            dados["arquivos_csv"] = arquivos_csv
        
        # Adicionar metadados da API
        dados["api_info"] = {
            "gerado_em": datetime.now().isoformat(),
            "endpoint": "/dados/periodo",
            "parametros": {
                "data_inicio": data_inicio.isoformat(),
                "data_fim": data_fim.isoformat(),
                "salvar_csv": salvar_csv,
                "seed": seed
            }
        }
        
        return dados
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno do servidor: {str(e)}"
        )

@app.get("/dados/recentes", summary="Gerar dados dos últimos dias")
async def get_dados_recentes(
    dias: int = Query(
        default=7,
        ge=1,
        le=30,
        description="Número de dias anteriores para gerar dados (máximo 30)"
    ),
    salvar_csv: bool = Query(
        default=False,
        description="Se True, salva os dados em arquivos CSV"
    )
) -> Dict[str, Any]:
    """
    Gera dados dos últimos N dias (útil para atualizações incrementais).
    
    **Exemplo de uso:**
    - `/dados/recentes?dias=7` - dados dos últimos 7 dias
    - `/dados/recentes?dias=14&salvar_csv=true` - últimos 14 dias + salvar CSV
    """
    
    try:
        data_fim = date.today()
        data_inicio = data_fim - timedelta(days=dias)
        
        # Reutilizar a função principal
        return await get_dados_periodo(
            data_inicio=data_inicio,
            data_fim=data_fim,
            salvar_csv=salvar_csv
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno do servidor: {str(e)}"
        )

@app.get("/dados/desde-junho", summary="Dados desde 10 de junho (para o projeto)")
async def get_dados_desde_junho(
    salvar_csv: bool = Query(
        default=True,
        description="Salvar dados em CSV para integração com dbt"
    )
) -> Dict[str, Any]:
    """
    Endpoint específico para o projeto: gera dados desde 10/06/2025 até hoje.
    
    **Uso recomendado para integração com dbt.**
    """
    
    return await get_dados_periodo(
        data_inicio=date(2025, 6, 10),
        data_fim=date.today(),
        salvar_csv=salvar_csv
    )

@app.get("/health", summary="Verificação de saúde da API")
async def health_check():
    """Endpoint para verificar se a API está funcionando."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "API funcionando corretamente"
    }

# Função para executar a API
def run_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Executa a API FastAPI."""
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    print("🚀 Iniciando DW Data API...")
    print("📖 Documentação disponível em: http://localhost:8000/docs")
    print("🔄 Endpoint principal: http://localhost:8000/dados/periodo")
    print("📊 Dados do projeto: http://localhost:8000/dados/desde-junho")
    
    run_api()