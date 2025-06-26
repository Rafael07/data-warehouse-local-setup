# Projeto de Portfólio: Construção de uma Solução de Business Intelligence Orientada a Dados e Autoatendimento

## Introdução

Este documento detalha um projeto de Business Intelligence (BI) que visa transformar dados brutos em informações acionáveis, capacitando usuários de negócio a tomar decisões estratégicas. O projeto demonstra proficiência em todo o ciclo de vida do BI, desde a engenharia de dados e modelagem informacional até a visualização e a aplicação de princípios de governança de dados, com foco na construção de uma solução de autoatendimento (Self-Service BI).

## 1. Descrição do Problema de Negócio

Em um cenário empresarial dinâmico, a capacidade de tomar decisões rápidas e baseadas em dados é um diferencial competitivo. No entanto, muitas organizações enfrentam desafios como:

*   **Dados Fragmentados e Inconsistentes:** Informações dispersas em diversas fontes, sem padronização ou qualidade garantida.
*   **Falta de Métricas Confiáveis:** Dificuldade em definir e calcular indicadores de desempenho (KPIs) de forma consistente e auditável.
*   **Dependência da TI:** Áreas de negócio dependem excessivamente da equipe de tecnologia para obter relatórios e análises, gerando gargalos e atrasos na tomada de decisão.
*   **Baixa Adoção de Dados:** Usuários de negócio não conseguem explorar os dados por conta própria, limitando o potencial de descoberta de insights.
*   **Desatualização:** Dados estáticos que não refletem a realidade mais recente do negócio.

O problema central é a **lacuna entre os dados operacionais e a inteligência de negócio**, impedindo que a empresa capitalize plenamente o valor de suas informações para impulsionar o crescimento e a eficiência.

## 2. Objetivos de Negócio

Para superar os desafios identificados, este projeto estabeleceu os seguintes objetivos de negócio:

*   **Democratizar o Acesso à Informação:** Capacitar usuários de negócio a acessar e analisar dados de forma autônoma, reduzindo a dependência da equipe de TI.
*   **Garantir a Confiabilidade dos Dados:** Fornecer métricas e KPIs consistentes, precisos e auditáveis, que sirvam como uma "fonte única da verdade" para toda a organização.
*   **Acelerar a Tomada de Decisão:** Reduzir o tempo entre a necessidade de uma informação e sua disponibilidade para análise, permitindo respostas mais ágeis às mudanças do mercado.
*   **Otimizar o Desempenho:** Identificar oportunidades de melhoria em processos de vendas e relacionamento com clientes através de análises detalhadas.
*   **Promover a Cultura Orientada a Dados:** Incentivar a experimentação e a descoberta de insights por parte dos usuários de negócio.

## 3. Processo Técnico Adotado

O projeto seguiu uma abordagem estruturada e baseada em melhores práticas de engenharia de dados e Business Intelligence, utilizando um conjunto de ferramentas modernas e eficientes:

### 3.1. Engenharia e Modelagem de Dados com dbt (Data Build Tool)

O dbt foi a **espinha dorsal** da camada de transformação e modelagem do Data Warehouse (DW), garantindo governança, qualidade e escalabilidade. A arquitetura de dados foi organizada em camadas lógicas:

*   **Staging (`stg_`):** Camada de dados brutos, onde os dados são carregados de suas fontes originais (simuladas por seeds e API) e passam por uma limpeza mínima (tipagem, renomeação de colunas). O foco aqui é a fidelidade à fonte e a preparação para transformações subsequentes.
*   **Intermediate (`int_`):** Camada de transformações intermediárias, onde a lógica de negócio complexa é aplicada e os dados são enriquecidos. Esta camada serve como um hub para reutilização de modelos e garante que cálculos complexos sejam feitos uma única vez e de forma consistente. Exemplos incluem a criação de dimensões (`int_dim_date`, `int_dim_clientes`) e fatos (`int_fact_pedidos`).
*   **Mart (`mart_`):** A camada de consumo final, otimizada para ferramentas de BI e para as necessidades específicas das áreas de negócio. As tabelas `mart` contêm as métricas e KPIs pré-agregados e prontos para uso, como `mart_metricas_clientes` (métricas por cliente) e `mart_vendas_por_periodo` (vendas agregadas por data).

**Benefícios do dbt para o Projeto:**

*   **Governança de Dados:**
    *   **Linhagem de Dados (Data Lineage):** O dbt gera automaticamente um grafo de dependências que visualiza o fluxo de dados, desde a origem até o `mart`. Isso permite rastrear a proveniência de cada métrica, essencial para auditoria e compreensão do impacto de mudanças.
    *   **Versionamento de Código:** Todos os modelos dbt são escritos em SQL e versionados (via Git), garantindo controle de alterações, colaboração e a capacidade de reverter para versões anteriores das definições de métricas.
    *   **Testes de Qualidade de Dados:** O dbt permite a criação de testes automatizados (ex: unicidade de IDs, não-nulidade de colunas críticas) para garantir a integridade e a qualidade dos dados em cada etapa da transformação.
    *   **Documentação Automática:** O dbt gera uma documentação web interativa a partir dos modelos e descrições. Isso facilita o compartilhamento do conhecimento sobre as métricas e a lógica de negócio com toda a equipe, incluindo usuários de negócio, promovendo a transparência e a cultura de dados.
*   **Modelagem Informacional:** A estrutura em camadas do dbt reflete uma modelagem informacional robusta, transformando dados brutos em informações orientadas à decisão. As tabelas `mart` são projetadas para serem intuitivas e de fácil consumo pelas áreas de negócio.
*   **Reutilização e Manutenibilidade:** A modularidade dos modelos dbt promove a reutilização de código e facilita a manutenção do pipeline de dados.

### 3.2. Integração de Dados com API (FastAPI)

Para garantir que o Data Warehouse reflita os dados mais recentes e demonstrar proficiência em integração via APIs, foi desenvolvida uma API RESTful utilizando **FastAPI**.

*   **Propósito:** Fornecer dados incrementais (cadastros e pedidos) de forma programática, simulando a ingestão de dados em tempo quase real ou de sistemas transacionais.
*   **Funcionalidades:** A API permite a geração de dados para períodos específicos, com volumes randomizados para simular cenários reais de negócio. Inclui endpoints para dados diários, dados de um período específico e um endpoint dedicado para os dados do projeto (desde 10 de junho até a data atual).
*   **Benefícios:** Demonstra a capacidade de manipular e integrar dados de diversas fontes, incluindo APIs, um requisito chave para Analistas de BI. A documentação interativa gerada automaticamente pelo FastAPI (`/docs`) é um diferencial para a demonstração.

### 3.3. Visualização e Self-Service BI (Bricks)

O **Bricks** foi a ferramenta escolhida para a camada de visualização e para a implementação do Self-Service BI. O dashboard foi construído com foco na capacitação do usuário final:

*   **Modelagem de Dados no Bricks:** As tabelas `mart_metricas_clientes`, `mart_vendas_por_periodo` e `int_dim_date` foram carregadas e modeladas, estabelecendo relacionamentos claros para garantir a integridade e a capacidade de análise cruzada dos dados.
*   **Medidas DAX Explícitas:** Métricas chave (ex: Receita Total, Total de Pedidos, Ticket Médio) foram criadas como medidas DAX explícitas. Isso garante consistência nos cálculos, facilita a reutilização e permite a aplicação de funções avançadas de inteligência de tempo.
*   **Design Orientado ao Usuário:** O dashboard foi projetado com um layout limpo e intuitivo, utilizando segmentadores (slicers) para filtros dinâmicos (data, segmento de cliente, estado), e funcionalidades de drill-down/drill-through para permitir que os usuários explorem os dados em diferentes níveis de granularidade.
*   **Self-Service BI:** O objetivo principal é que o usuário de negócio possa interagir com o dashboard, fazer suas próprias perguntas aos dados e obter insights sem depender de um analista para cada nova consulta. Isso é alcançado através da combinação de um modelo de dados robusto, medidas claras e uma interface interativa.

### 3.4. Ferramentas e Tecnologias Utilizadas

*   **Orquestração/Transformação:** dbt (Data Build Tool)
*   **Banco de Dados:** PostgreSQL (rodando em Docker)
*   **Geração de Dados/API:** Python, FastAPI, Faker
*   **Visualização/BI:** Bricks Desktop
*   **Containerização:** Docker, Docker Compose

## 4. Resultados Obtidos

Este projeto resultou na criação de uma solução de Business Intelligence que:

*   **Fornece Métricas Confiáveis:** Através do dbt, estabeleceu uma "fonte única da verdade" para KPIs de vendas e clientes, garantindo consistência e precisão.
*   **Permite Análise de Autoatendimento:** O dashboard Bricks capacita os usuários de negócio a explorar dados de forma independente, aplicando filtros e detalhando informações conforme suas necessidades.
*   **Demonstra Governança de Dados:** A utilização do dbt para linhagem, versionamento, testes e documentação automática evidencia a aplicação de princípios de governança na construção de indicadores.
*   **Integra Dados de Múltiplas Fontes:** A API FastAPI demonstra a capacidade de integrar dados de sistemas transacionais ou outras fontes em tempo quase real, mantendo o DW atualizado.
*   **Otimiza a Tomada de Decisão:** Ao fornecer acesso rápido e intuitivo a informações estratégicas, táticas e operacionais, o projeto contribui para decisões mais ágeis e embasadas.
*   **Cria um Portfólio Abrangente:** O projeto serve como uma demonstração prática de habilidades em engenharia de dados, modelagem informacional, visualização de dados, Self-Service BI e governança, alinhado diretamente aos requisitos de uma vaga de Analista de BI.

## 5. Ferramentas de Visualização: Uma Perspectiva Estratégica

É fundamental ressaltar que, embora o edital mencione ferramentas específicas como Qlik Sense e NPrinting, a **proficiência em ferramentas de visualização de dados é uma competência transferível**. O principal valor de um Analista de BI reside na sua capacidade de:

*   **Compreender o Problema de Negócio:** Traduzir desafios empresariais em perguntas que podem ser respondidas por dados.
*   **Definir e Modelar Indicadores:** Transformar dados brutos em KPIs significativos e confiáveis, aplicando lógica de negócio e princípios de modelagem informacional (como demonstrado com o dbt).
*   **Garantir a Qualidade e Governança dos Dados:** Assegurar que os dados sejam precisos, consistentes e bem documentados, independentemente da ferramenta de visualização.
*   **Capacitar o Usuário Final:** Construir soluções que permitam o autoatendimento, focando na usabilidade e na interatividade.

O Bricks, neste projeto, serve como uma **prova de conceito** da capacidade de criar dashboards interativos e orientados ao Self-Service BI. A habilidade de trabalhar com Qlik Sense ou NPrinting é uma questão de adaptação à sintaxe e interface da ferramenta, uma vez que os princípios subjacentes de modelagem, governança e compreensão de negócio já estão solidamente demonstrados. O foco está na **estruturação da informação** e na **capacidade analítica**, que são independentes da ferramenta de front-end utilizada.



