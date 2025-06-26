import pandas as pd
import glob
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SeedsConsolidator:
    def __init__(self, 
                 api_seeds_path="../api/seeds/",  # Relativo a 1_local_setup/scripts
                 dbt_seeds_path="../../2_data_warehouse/dw_dbt_airflow/seeds/"):  # Relativo a 1_local_setup/scripts
        
        # Converte para caminhos absolutos
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.api_seeds_path = os.path.abspath(os.path.join(script_dir, api_seeds_path))
        self.dbt_seeds_path = os.path.abspath(os.path.join(script_dir, dbt_seeds_path))
        
        logger.info(f"📂 Script localizado em: {script_dir}")
        logger.info(f"📂 API Seeds: {self.api_seeds_path}")
        logger.info(f"📂 dbt Seeds: {self.dbt_seeds_path}")
        
        # Verifica se os diretórios existem
        if not os.path.exists(self.api_seeds_path):
            logger.error(f"Diretório da API não encontrado: {self.api_seeds_path}")
            raise FileNotFoundError(f"Diretório da API não encontrado: {self.api_seeds_path}")
            
        if not os.path.exists(self.dbt_seeds_path):
            logger.error(f"Diretório do dbt não encontrado: {self.dbt_seeds_path}")
            raise FileNotFoundError(f"Diretório do dbt não encontrado: {self.dbt_seeds_path}")
        
    def consolidate_table(self, table_name):
        """
        Consolida arquivos CSV de uma tabela específica
        """
        try:
            # Arquivo principal (no dbt seeds)
            main_file = os.path.join(self.dbt_seeds_path, f"{table_name}.csv")
            
            # Arquivos da API (no diretório da API)
            api_pattern = os.path.join(self.api_seeds_path, f"{table_name}_api_*.csv")
            api_files = glob.glob(api_pattern)
            
            if not api_files:
                logger.info(f"Nenhum arquivo da API encontrado para {table_name}")
                logger.info(f"Padrão buscado: {api_pattern}")
                return
                
            logger.info(f"=== Consolidando {table_name} ===")
            logger.info(f"Arquivo principal: {main_file}")
            logger.info(f"Arquivos da API encontrados: {len(api_files)}")
            for api_file in api_files:
                logger.info(f"  - {os.path.basename(api_file)}")
            
            # Lista para armazenar todos os DataFrames
            dataframes = []
            
            # Carrega arquivo principal se existir
            if os.path.exists(main_file):
                df_main = pd.read_csv(main_file)
                dataframes.append(df_main)
                logger.info(f"✓ Carregado arquivo principal: {len(df_main)} registros")
            else:
                logger.warning(f"⚠️ Arquivo principal não encontrado: {main_file}")
            
            # Carrega arquivos da API
            for api_file in api_files:
                try:
                    df_api = pd.read_csv(api_file)
                    dataframes.append(df_api)
                    logger.info(f"✓ Carregado {os.path.basename(api_file)}: {len(df_api)} registros")
                except Exception as e:
                    logger.error(f"❌ Erro ao carregar {api_file}: {str(e)}")
                    continue
            
            if not dataframes:
                logger.warning(f"Nenhum DataFrame carregado para {table_name}")
                return
            
            # Consolida todos os DataFrames
            df_consolidated = pd.concat(dataframes, ignore_index=True)
            logger.info(f"📊 Total de registros antes da deduplicação: {len(df_consolidated)}")
            
            # Remove duplicatas (ajuste as colunas conforme necessário)
            if table_name == 'cadastros':
                # Para cadastros, remove duplicatas por ID e CPF, mantendo o mais recente
                if 'data_cadastro' in df_consolidated.columns:
                    df_consolidated = df_consolidated.sort_values('data_cadastro', ascending=False)
                df_consolidated = df_consolidated.drop_duplicates(subset=['id', 'cpf'], keep='first')
                logger.info(f"🔍 Deduplicação por: id, cpf")
                
            elif table_name == 'pedidos':
                # Para pedidos, remove duplicatas por ID do pedido, mantendo o mais recente
                if 'data_pedido' in df_consolidated.columns:
                    df_consolidated = df_consolidated.sort_values('data_pedido', ascending=False)
                df_consolidated = df_consolidated.drop_duplicates(subset=['id'], keep='first')
                logger.info(f"🔍 Deduplicação por: id")
            
            logger.info(f"📊 Total de registros após deduplicação: {len(df_consolidated)}")
            
            # Backup do arquivo original
            if os.path.exists(main_file):
                backup_file = f"{main_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(main_file, backup_file)
                logger.info(f"💾 Backup criado: {os.path.basename(backup_file)}")
            
            # Salva arquivo consolidado
            df_consolidated.to_csv(main_file, index=False)
            logger.info(f"✅ Arquivo consolidado salvo: {os.path.basename(main_file)}")
            
            # Remove arquivos temporários da API
            for api_file in api_files:
                try:
                    os.remove(api_file)
                    logger.info(f"🗑️ Arquivo temporário removido: {os.path.basename(api_file)}")
                except Exception as e:
                    logger.error(f"❌ Erro ao remover {api_file}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao consolidar {table_name}: {str(e)}")
            raise
    
    def list_files(self):
        """
        Lista arquivos encontrados para debug
        """
        logger.info("=== LISTAGEM DE ARQUIVOS ===")
        
        logger.info(f"📁 Diretório API: {self.api_seeds_path}")
        if os.path.exists(self.api_seeds_path):
            api_files = glob.glob(os.path.join(self.api_seeds_path, "*.csv"))
            if api_files:
                for file in api_files:
                    logger.info(f"  - {os.path.basename(file)}")
            else:
                logger.info("  (vazio)")
        else:
            logger.error("  (diretório não existe)")
        
        logger.info(f"📁 Diretório dbt: {self.dbt_seeds_path}")
        if os.path.exists(self.dbt_seeds_path):
            dbt_files = glob.glob(os.path.join(self.dbt_seeds_path, "*.csv"))
            if dbt_files:
                for file in dbt_files:
                    logger.info(f"  - {os.path.basename(file)}")
            else:
                logger.info("  (vazio)")
        else:
            logger.error("  (diretório não existe)")
    
    def consolidate_all(self):
        """
        Consolida todas as tabelas
        """
        tables = ['cadastros', 'pedidos']
        
        logger.info("🚀 Iniciando consolidação de seeds...")
        
        # Lista arquivos para debug
        self.list_files()
        
        success_count = 0
        for table in tables:
            try:
                self.consolidate_table(table)
                success_count += 1
            except Exception as e:
                logger.error(f"❌ Falha ao consolidar {table}: {str(e)}")
        
        logger.info(f"🎉 Consolidação completa! {success_count}/{len(tables)} tabelas processadas com sucesso")

if __name__ == "__main__":
    try:
        consolidator = SeedsConsolidator()
        consolidator.consolidate_all()
        
    except Exception as e:
        logger.error(f"💥 Erro crítico: {str(e)}")
        exit(1)