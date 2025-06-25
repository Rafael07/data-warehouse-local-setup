import numpy as np
from faker import Faker
import uuid
import random
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional
import json

# Configurações iniciais
fake = Faker('pt_BR')

def gerar_dados_periodo(
    data_inicio: str, 
    data_fim: str, 
    seed: Optional[int] = None
) -> Dict:
    """
    Gera dados para um período específico com volumes randomizados.
    
    Args:
        data_inicio (str): Data de início no formato 'YYYY-MM-DD'
        data_fim (str): Data de fim no formato 'YYYY-MM-DD'
        seed (int, optional): Seed para reprodutibilidade (útil para testes)
    
    Returns:
        dict: Dados gerados com cadastros e pedidos
    """
    
    # Configurar seed se fornecido
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
        Faker.seed(seed)  # Usar método estático do Faker
    
    # Volumes randomizados (mais realista)
    total_cadastros = random.randint(2, 20)
    total_pedidos = random.randint(40, 90)
    
    print(f"Gerando dados para período {data_inicio} a {data_fim}")
    print(f"Volumes: {total_cadastros} cadastros, {total_pedidos} pedidos")
    
    # Gerar cadastros
    cadastros_data = gerar_cadastros_periodo(data_inicio, data_fim, total_cadastros)
    
    # Extrair CPFs para gerar pedidos
    cpfs = [cadastro['cpf'] for cadastro in cadastros_data]
    
    # Gerar pedidos (pode usar CPFs existentes + alguns dos novos cadastros)
    pedidos_data = gerar_pedidos_periodo(data_inicio, data_fim, total_pedidos, cpfs)
    
    return {
        "periodo": {
            "data_inicio": data_inicio,
            "data_fim": data_fim
        },
        "estatisticas": {
            "total_cadastros": len(cadastros_data),
            "total_pedidos": len(pedidos_data),
            "cpfs_disponiveis": len(cpfs)
        },
        "dados": {
            "cadastros": cadastros_data,
            "pedidos": pedidos_data
        }
    }

def gerar_cadastros_periodo(data_inicio: str, data_fim: str, quantidade: int) -> List[Dict]:
    """Gera cadastros para o período especificado."""
    cadastros = []
    cpfs_gerados = set()
    
    for _ in range(quantidade):
        # Gerar CPF único
        tentativas = 0
        while tentativas < 100:  # Evitar loop infinito
            cpf = fake.bothify(text='###.###.###-##')
            if cpf not in cpfs_gerados:
                cpfs_gerados.add(cpf)
                break
            tentativas += 1
        
        cadastro = {
            'id': str(uuid.uuid4()),
            'nome': fake.name(),
            'data_nascimento': fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
            'cpf': cpf,
            'cep': fake.postcode(),
            'cidade': fake.city(),
            'estado': fake.state_abbr(),
            'pais': 'Brasil',
            'genero': random.choice(['M', 'F']),
            'telefone': fake.phone_number(),
            'email': f"{cpf.replace('.', '').replace('-', '')}@exemplo.com.br",
            'data_cadastro': fake.date_between(
                start_date=datetime.strptime(data_inicio, '%Y-%m-%d').date(),
                end_date=datetime.strptime(data_fim, '%Y-%m-%d').date()
            ).isoformat()
        }
        cadastros.append(cadastro)
    
    return cadastros

def gerar_pedidos_periodo(data_inicio: str, data_fim: str, quantidade: int, cpfs_disponiveis: List[str]) -> List[Dict]:
    """Gera pedidos para o período especificado."""
    pedidos = []
    
    # Se não temos CPFs suficientes, gerar alguns extras
    if len(cpfs_disponiveis) < quantidade // 2:
        cpfs_extras = []
        for _ in range(quantidade // 2):
            cpf_extra = fake.bothify(text='###.###.###-##')
            cpfs_extras.append(cpf_extra)
        cpfs_disponiveis.extend(cpfs_extras)
    
    for _ in range(quantidade):
        # Selecionar CPF aleatório
        cpf = random.choice(cpfs_disponiveis)
        
        # Gerar dados do pedido
        valor_total = round(random.uniform(50, 2000), 2)
        tem_desconto = random.random() < 0.2  # 20% de chance de ter desconto
        valor_desconto = round(valor_total * random.uniform(0.05, 0.2), 2) if tem_desconto else 0.0
        
        # Gerar cupom se houver desconto
        cupom = f"CUPOM{str(uuid.uuid4())[:8].upper()}" if tem_desconto else None
        
        pedido = {
            'id_pedido': str(uuid.uuid4()),
            'cpf': cpf,
            'valor_pedido': valor_total,
            'valor_frete': round(random.uniform(5, 100), 2),
            'valor_desconto': valor_desconto,
            'cupom': cupom,
            'endereco_entrega_logradouro': fake.street_name(),
            'endereco_entrega_numero': fake.building_number(),
            'endereco_entrega_bairro': fake.neighborhood(),
            'endereco_entrega_cidade': fake.city(),
            'endereco_entrega_estado': fake.state_abbr(),
            'endereco_entrega_pais': 'Brasil',
            'status_pedido': random.choice(['pendente', 'pago', 'enviado', 'entregue', 'cancelado']),
            'data_pedido': fake.date_between(
                start_date=datetime.strptime(data_inicio, '%Y-%m-%d').date(),
                end_date=datetime.strptime(data_fim, '%Y-%m-%d').date()
            ).isoformat()
        }
        pedidos.append(pedido)
    
    return pedidos

def salvar_dados_csv(dados: Dict, pasta_destino: str = "./seeds_api/") -> Dict[str, str]:
    """
    Salva os dados gerados em arquivos CSV para integração com dbt.
    
    Args:
        dados (dict): Dados gerados pela função gerar_dados_periodo
        pasta_destino (str): Pasta onde salvar os CSVs
    
    Returns:
        dict: Caminhos dos arquivos gerados
    """
    import os
    
    # Criar pasta se não existir
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Converter para DataFrames
    df_cadastros = pd.DataFrame(dados['dados']['cadastros'])
    df_pedidos = pd.DataFrame(dados['dados']['pedidos'])
    
    # Gerar nomes de arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_cadastros = f"{pasta_destino}cadastros_api_{timestamp}.csv"
    arquivo_pedidos = f"{pasta_destino}pedidos_api_{timestamp}.csv"
    
    # Salvar CSVs
    df_cadastros.to_csv(arquivo_cadastros, index=False)
    df_pedidos.to_csv(arquivo_pedidos, index=False)
    
    return {
        "cadastros": arquivo_cadastros,
        "pedidos": arquivo_pedidos,
        "timestamp": timestamp
    }

# Função de teste/exemplo
if __name__ == "__main__":
    # Teste da função
    dados = gerar_dados_periodo("2025-06-10", "2025-06-24", seed=42)
    
    print("\n=== RESULTADO DO TESTE ===")
    print(f"Período: {dados['periodo']['data_inicio']} a {dados['periodo']['data_fim']}")
    print(f"Cadastros gerados: {dados['estatisticas']['total_cadastros']}")
    print(f"Pedidos gerados: {dados['estatisticas']['total_pedidos']}")
    
    # Exemplo de cadastro
    if dados['dados']['cadastros']:
        print(f"\nExemplo de cadastro:")
        print(json.dumps(dados['dados']['cadastros'][0], indent=2, ensure_ascii=False))
    
    # Exemplo de pedido
    if dados['dados']['pedidos']:
        print(f"\nExemplo de pedido:")
        print(json.dumps(dados['dados']['pedidos'][0], indent=2, ensure_ascii=False))
    
    # Salvar em CSV para teste
    arquivos = salvar_dados_csv(dados)
    print(f"\nArquivos CSV gerados:")
    for tipo, caminho in arquivos.items():
        if tipo != 'timestamp':
            print(f"- {tipo}: {caminho}")