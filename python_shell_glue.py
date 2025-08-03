# script-b3-upload

import os
import json
import base64
import requests
import pandas as pd
from datetime import datetime, timedelta
import io
import boto3
import pyarrow as pa
import pyarrow.parquet as pq

# ---------- Configuração (via Glue Job Parameters) ----------
BUCKET = os.environ.get("BUCKET", "b3-pipeline-tc")
PREFIX = "raw"  # prefixo base no bucket

# ---------- 1. Busca da Carteira Teórica IBOV ----------
def fetch_b3_portfolio(page_number: int = 1, page_size: int = 200) -> pd.DataFrame:
    payload = {
        "pageNumber": page_number,
        "pageSize": page_size,
        "language": "pt-br",
        "index": "IBOV"
    }
    params_enc = base64.b64encode(json.dumps(payload).encode()).decode()
    url = f"https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetTheoricalPortfolio/{params_enc}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*"
    }

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results") or []
    if not results:
        raise RuntimeError("Nenhum resultado retornado no JSON.")
    return pd.DataFrame(results)

# ---------- 2. Escrita do Parquet direto no S3, com data_pregao ----------
def write_parquet_to_s3(df: pd.DataFrame) -> str:
    # adiciona a coluna data_pregao
    hoje = (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d")
    df["data_pregao"] = hoje

    # montar partições com data de processamento
    now = datetime.utcnow()
    yyyy = now.year
    mm = f"{now.month:02d}"
    dd = f"{now.day:02d}"
    filename = f"b3_portfolio_ibov_{hoje}.parquet"
    s3_key = f"{PREFIX}/year={yyyy}/month={mm}/day={dd}/{filename}"

    # converter DataFrame em Parquet em memória
    table = pa.Table.from_pandas(df)
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)

    # enviar para o S3
    s3 = boto3.client("s3")
    s3.upload_fileobj(buffer, BUCKET, s3_key)
    uri = f"s3://{BUCKET}/{s3_key}"
    print(f"Parquet enviado para: {uri}")
    return uri

# ---------- 3. Fluxo principal ----------
def main():
    print("Iniciando fetch da carteira IBOV...")
    df = fetch_b3_portfolio(page_number=1, page_size=200)
    print(f"Linhas retornadas: {len(df)}")
    uri = write_parquet_to_s3(df)
    print("Processo concluído.")

if __name__ == "__main__":
    main()
