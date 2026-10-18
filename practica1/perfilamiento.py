
import pandas as pd
import json
import io

# Importar excepciones de AWS y Pandas
from botocore.exceptions import ClientError, BotoCoreError
from pandas.errors import ParserError, EmptyDataError

# Importar conexión desde archivo externo
from conexion import conectar_s3


def cargar_y_perfilar_s3(s3_client, bucket_name, file_key, is_json=False):
    """
    Descarga archivos CSV o JSON desde AWS S3,
    genera un perfilamiento y controla posibles errores.
    """

    print(f"\n=== Procesando objeto S3: {file_key} ===")

    try:
        # 1. Descargar el archivo desde S3
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=file_key
        )

        body = response["Body"].read()

        # 2. Convertir el archivo en DataFrame
        if is_json:
            data_json = json.loads(body.decode("utf-8"))
            df = pd.json_normalize(data_json)
        else:
            df = pd.read_csv(io.BytesIO(body))

        # 3. Perfilamiento de los datos
        print(
            f"Dimensiones: {df.shape[0]} filas x "
            f"{df.shape[1]} columnas"
        )

        print("\nTipos de datos:")
        print(df.dtypes)

        print("\nEstadísticos descriptivos:")
        print(df.describe().T)

        print(f"\nArchivo {file_key} procesado correctamente.")

        return df

    # Error de AWS: credenciales, permisos o archivo inexistente
    except ClientError as error:
        codigo = error.response["Error"]["Code"]

        if codigo == "NoSuchKey":
            print(f"Error: El archivo {file_key} no existe en S3.")

        elif codigo == "ExpiredToken":
            print(
                "Error: Las credenciales de AWS Academy "
                "han expirado."
            )

        elif codigo == "AccessDenied":
            print(
                "Error: No tienes permisos para "
                "acceder al archivo."
            )

        else:
            print(f"Error de AWS S3: {codigo}")

    # Error de comunicación con AWS
    except BotoCoreError as error:
        print(f"Error de comunicación con AWS: {error}")

    # Error en la estructura del CSV
    except (ParserError, EmptyDataError):
        print("Error: El archivo CSV está vacío o tiene un formato inválido.")

    # Error en el formato JSON
    except json.JSONDecodeError:
        print("Error: El archivo JSON contiene datos inválidos.")

    # Error al decodificar el contenido
    except UnicodeDecodeError:
        print("Error: No se pudo decodificar el archivo.")

    return None


if __name__ == "__main__":

    try:
        # Obtener conexión desde el archivo YAML
        s3_client, BUCKET_NAME = conectar_s3()

    except (OSError, KeyError, ValueError, BotoCoreError) as error:
        print(f"Error al configurar la conexión: {error}")
        raise SystemExit(1)

    # Procesar archivo CSV
    df_transacciones = cargar_y_perfilar_s3(
        s3_client,
        BUCKET_NAME,
        "raw/transacciones.csv"
    )

    # Procesar archivo JSON
    df_logs = cargar_y_perfilar_s3(
        s3_client,
        BUCKET_NAME,
        "raw/logs_m2m.json",
        is_json=True
    )

    # Comprobar los resultados
    if df_transacciones is not None and df_logs is not None:
        print("\n=== PRÁCTICA FINALIZADA CORRECTAMENTE ===")
    else:
        print("\n=== PRÁCTICA FINALIZADA CON ERRORES ===")
        raise SystemExit(1)
