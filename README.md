Tech Challenge 2 – Pipeline Batch Bovespa

Este repositório contém a implementação completa do projeto da Fase 2 do Tech Challenge FIAP, que consiste na construção de um pipeline de dados em batch para ingestão, transformação e análise de dados do pregão da B3, utilizando serviços serverless da AWS.

Objetivo

Automatizar todo o processo de coleta, transformação e análise dos dados da carteira teórica do índice IBOV da B3, aplicando boas práticas de arquitetura de dados em nuvem com foco em escalabilidade, particionamento e performance.

Arquitetura

O pipeline foi desenvolvido com os seguintes componentes da AWS:
- AWS Lambda: função acionada por eventos no S3 para iniciar o processo ETL.
- AWS Glue Studio (modo visual): job de transformação dos dados com agregações, renomeio de colunas e cálculos com datas.
- AWS S3: armazenamento em duas camadas (raw e refined) com particionamento por data e código da ação.
- AWS Athena: consulta e análise dos dados refinados via SQL.
- Glue Data Catalog: metadados dos dados particionados, tornando-os acessíveis ao Athena.

Estrutura do Repositório

tech-challenge-2/
├── lambda/
│   └── lambda_function.py         # Código da função Lambda
├── glue/
│   └── python_shell_glue.py        # Script visual (export) do Glue Job
├── athena/
│   └── visualizacao_b3.ipynb        # Notebook para análises com SparkSQL no Athena
├── README.md

Funcionalidades

- Extração: realiza scraping dos dados do pregão da B3 (carteira teórica do IBOV).
- Ingestão: salva os dados em formato Parquet, particionado por data.
- Processamento: transforma os dados no Glue com agregações e cálculos temporais.
- Consulta: disponibiliza os dados no Athena para análise em SQL e Spark.
- Catalogação automática: os dados transformados são registrados no Glue Data Catalog.

Como Executar

1. Configurar Lambda
- Acesse o diretório lambda/ e implante a função no AWS Lambda.
- A função deve estar associada ao evento "PUT" do bucket S3 (raw/).
- Atualize o nome do job do Glue no script, se necessário.

2. Criar Glue python shell
- Colocar o código no corpo do glue.
- Ajuste as configurações de IAM e timeout.
- Configure o schedule, se necessário.

3. Rodar Notebook Athena
- Acesse o notebook athena/visualizacao_b3.ipynb via Athena for Spark (notebooks).
- Execute consultas e visualizações sobre os dados refinados.

Exemplo de Consulta Athena

SELECT data_pregao, COUNT(DISTINCT codigo) AS num_acoes
FROM b3_refined
GROUP BY data_pregao
ORDER BY data_pregao;

Resultados Esperados

- Pipeline automatizado e modular.
- Dados acessíveis via Athena, com particionamento eficiente.
- ETL visual no Glue com transformações claras.
- Análises rápidas por SQL ou Spark com baixo custo computacional.

Contribuição

Lucas Caique, Alexandre Lima, Thiago Ramos e Eduardo Barbosa 

Licença

Projeto acadêmico para fins educacionais.
