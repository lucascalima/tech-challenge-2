import json
import base64
import requests
import pandas as pd
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq
import io
import os
import boto3

# Variáveis de ambiente
BUCKET   = os.environ['BUCKET']       # ex: "meu-bucket-b3"
PAGE_SIZE = int(os.environ.get('PAGE_SIZE', 200))

s3 = boto3.client('s3')

def fetch_b3_portfolio(page_number: int = 1, page_size: int = PAGE_SIZE) -> pd.DataFrame:
    payload = {
        "pageNumber": page_number,
        "pageSize": page_size,
        "language": "pt-br",
        "index": "IBOV"
    }
    params_enc = base64.b64encode(json.dumps(payload).encode()).decode()
    url = f"https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetTheoricalPortfolio/{params_enc}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive"
    }

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results") or []
    if not results:
        raise RuntimeError("Nenhum resultado retornado pela API B3.")

    return pd.DataFrame(results)

def lambda_handler(event, context):
    # 1) Buscar dados
    df = fetch_b3_portfolio(page_number=1)

    # 2) Converter para Parquet em memória
    table = pa.Table.from_pandas(df)
    buf = io.BytesIO()
    pq.write_table(table, buf)
    buf.seek(0)

    # 3) Montar caminho e enviar para S3
    hoje = datetime.utcnow().strftime("%Y-%m-%d")
    key = f"raw/data_processamento={hoje}/b3_portfolio_ibov.parquet"
    s3.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue())

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Parquet gerado com sucesso",
            "s3_key": key
        })
    }
