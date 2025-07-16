import requests
import json
import base64
import pandas as pd
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq
import os

# 1. Função que busca o JSON da Carteira Teórica IBOV
def fetch_b3_portfolio(page_number: int = 1, page_size: int = 100) -> pd.DataFrame:
    payload = {
        "pageNumber": page_number,
        "pageSize": page_size,
        "language": "pt-br",
        "index": "IBOV"
    }
    # codifica o JSON em Base64
    params_enc = base64.b64encode(json.dumps(payload).encode()).decode()
    url = f"https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetTheoricalPortfolio/{params_enc}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive"
    }

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()  # lança erro se status != 200

    data = resp.json()
    results = data.get("results") or []
    if not results:
        raise Exception("Nenhum resultado retornado no JSON.")

    df = pd.DataFrame(results)
    return df

# 2. Função para salvar o DataFrame como Parquet localmente
def save_to_parquet(df: pd.DataFrame, base_dir: str = "b3_parquet_output") -> str:
    hoje = datetime.now().strftime("%Y-%m-%d")
    out_dir = os.path.join(base_dir, f"data_processamento={hoje}")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "b3_portfolio_ibov.parquet")

    table = pa.Table.from_pandas(df)
    pq.write_table(table, out_path)

    print(f"✅ Parquet salvo em: {out_path}")
    return out_path

# 3. Teste completo
if __name__ == "__main__":
    # busca os 100 primeiros itens (ajuste page_size se quiser mais)
    df = fetch_b3_portfolio(page_number=1, page_size=200)
    print("📊 Head do DataFrame retornado:")
    print(df.head())

    path = save_to_parquet(df)

    # leitura de verificação
    df2 = pd.read_parquet(path)
    print("✅ Head do Parquet lido:")
    print(df2.head())
