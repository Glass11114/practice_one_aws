
import pandas as pd
import json
import io

from conexion import conectar_s3

# Obtener conexión desde el archivo externo
s3_client, BUCKET_NAME = conectar_s3()

def cargar_y_perfilar_s3(file_key, is_json=False):
    """Descarga archivos de S3 y genera un perfilamiento."""

    print(f"\n=== Procesando objeto S3: {file_key} ===")

    response = s3_client.get_object(
        Bucket=BUCKET_NAME,
        Key=file_key
    )

    body = response["Body"].read()

    if is_json:
        data_json = json.loads(body.decode("utf-8"))
        df = pd.json_normalize(data_json)
    else:
        df = pd.read_csv(io.BytesIO(body))

    print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")

    print("\nTipos de datos:")
    print(df.dtypes)

    print("\nEstadísticos descriptivos:")
    print(df.describe().T)

    return df


if __name__ == "__main__":
    df_transacciones = cargar_y_perfilar_s3(
        "raw/transacciones.csv"
    )

    df_logs = cargar_y_perfilar_s3(
        "raw/logs_m2m.json",
        is_json=True
    )
