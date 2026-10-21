
import pandas as pd
import json
import io

# Importar excepciones de AWS y Pandas
from botocore.exceptions import ClientError, BotoCoreError
from pandas.errors import ParserError, EmptyDataError

# Importar conexión desde archivo externo
from conexion import conectar_s3


# ============================================================
# FUNCIÓN PARA CARGAR Y PERFILAR ARCHIVOS DESDE AWS S3
# ============================================================

def cargar_y_perfilar_s3(s3_client, bucket_name, file_key, is_json=False):
    """
    Descarga archivos CSV o JSON desde AWS S3,
    realiza el perfilamiento de datos, identifica posibles
    inconsistencias y controla errores.
    """

    print("\n" + "=" * 65)
    print(f"PROCESANDO OBJETO S3: {file_key}")
    print("=" * 65)

    try:
        # ====================================================
        # 1. EXTRACCIÓN DE DATOS DESDE AWS S3
        # ====================================================

        print("\n=== 1. EXTRACCIÓN DE DATOS ===")

        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=file_key
        )

        body = response["Body"].read()

        print("Archivo descargado correctamente desde S3.")
        print(f"Tamaño del archivo: {len(body)} bytes")

        # ====================================================
        # 2. CONVERSIÓN DEL ARCHIVO A DATAFRAME
        # ====================================================

        print("\n=== 2. CONVERSIÓN A DATAFRAME ===")

        if is_json:

            print("Formato detectado: JSON")

            data_json = json.loads(body.decode("utf-8"))

            if isinstance(data_json, dict):
                data_json = [data_json]

            if not isinstance(data_json, list):
                raise ValueError(
                    "El JSON debe contener un objeto o una lista."
                )

            df = pd.json_normalize(data_json)

        else:

            print("Formato detectado: CSV")

            df = pd.read_csv(
                io.BytesIO(body),
                encoding="utf-8"
            )

        print("Conversión realizada correctamente.")

        # ====================================================
        # 3. VISUALIZACIÓN INICIAL
        # ====================================================

        print("\n=== 3. PRIMEROS REGISTROS ===")

        print(df.head())

        # ====================================================
        # 4. DIMENSIONES DEL DATASET
        # ====================================================

        print("\n=== 4. DIMENSIONES DEL DATASET ===")

        print(f"Número de filas: {df.shape[0]}")
        print(f"Número de columnas: {df.shape[1]}")

        if df.empty:
            print("ADVERTENCIA: El dataset no contiene registros.")

        # ====================================================
        # 5. IDENTIFICACIÓN DE TIPOS DE DATOS
        # ====================================================

        print("\n=== 5. TIPOS DE DATOS ORIGINALES ===")

        print(df.dtypes)

        # ====================================================
        # 6. DETECCIÓN DE VALORES NULOS
        # ====================================================

        print("\n=== 6. ANÁLISIS DE VALORES NULOS ===")

        valores_nulos = df.isnull().sum()

        print(valores_nulos)

        total_nulos = valores_nulos.sum()

        print(f"\nTotal de valores nulos: {total_nulos}")

        if total_nulos > 0:
            print("ADVERTENCIA: Se encontraron valores nulos.")
        else:
            print("No se encontraron valores nulos.")

        # ====================================================
        # 7. DETECCIÓN DE REGISTROS DUPLICADOS
        # ====================================================

        print("\n=== 7. ANÁLISIS DE DUPLICADOS ===")

        # Convertir estructuras complejas a texto únicamente
        # para poder comparar registros sin modificar el original.
        df_comparacion = df.copy()

        for columna in df_comparacion.columns:
            df_comparacion[columna] = df_comparacion[columna].map(
                lambda valor: json.dumps(
                    valor,
                    sort_keys=True,
                    ensure_ascii=False
                ) if isinstance(valor, (dict, list)) else valor
            )

        duplicados = df_comparacion.duplicated().sum()

        print(f"Registros duplicados: {duplicados}")

        if duplicados > 0:
            print("ADVERTENCIA: Existen registros duplicados.")
        else:
            print("No se encontraron registros duplicados.")

        # ====================================================
        # 8. DETECCIÓN Y CONVERSIÓN DE FECHAS
        # ====================================================

        print("\n=== 8. VALIDACIÓN DE FECHAS ===")

        columnas_fecha = [
            columna for columna in df.columns
            if any(
                palabra in columna.lower()
                for palabra in ["fecha", "date", "timestamp"]
            )
        ]

        if columnas_fecha:

            for columna in columnas_fecha:

                print(f"\nAnalizando columna: {columna}")

                if pd.api.types.is_datetime64_any_dtype(
                    df[columna]
                ):
                    print("La columna ya contiene fechas.")
                    continue

                fechas_convertidas = pd.to_datetime(
                    df[columna],
                    errors="coerce"
                )

                fechas_invalidas = (
                    df[columna].notna()
                    & fechas_convertidas.isna()
                ).sum()

                print(f"Fechas inválidas: {fechas_invalidas}")

                if fechas_invalidas > 0:
                    print(
                        "ADVERTENCIA: Se encontraron fechas "
                        "con formato inválido."
                    )

                df[columna] = fechas_convertidas

                print("Conversión de fechas finalizada.")

        else:
            print("No se identificaron columnas de fecha.")

        # ====================================================
        # 9. IDENTIFICACIÓN DE INCONSISTENCIAS
        # ====================================================

        print("\n=== 9. ANÁLISIS DE INCONSISTENCIAS ===")

        columnas_objeto = df.select_dtypes(
            include=["object", "string"]
        ).columns

        for columna in columnas_objeto:

            print(f"\nAnalizando columna: {columna}")

            valores = df[columna].dropna()

            if valores.empty:
                print("La columna no contiene valores válidos.")
                continue

            # Detectar cadenas vacías o espacios en blanco
            vacios = valores.map(
                lambda valor: (
                    isinstance(valor, str)
                    and not valor.strip()
                )
            ).sum()

            print(f"Valores vacíos: {vacios}")

            # Identificar columnas que podrían ser numéricas
            # sin modificar identificadores o códigos.
            if any(
                palabra in columna.lower()
                for palabra in [
                    "monto", "precio", "total",
                    "cantidad", "importe", "edad"
                ]
            ):

                numeros = pd.to_numeric(
                    valores,
                    errors="coerce"
                )

                invalidos = numeros.isna().sum()

                print(f"Valores no numéricos: {invalidos}")

                if invalidos == 0:

                    df[columna] = pd.to_numeric(
                        df[columna],
                        errors="coerce"
                    )

                    print(
                        "Columna convertida a tipo numérico."
                    )

                else:
                    print(
                        "ADVERTENCIA: La columna contiene "
                        "valores que requieren revisión."
                    )

        # ====================================================
        # 10. ESTADÍSTICAS DESCRIPTIVAS
        # ====================================================

        print("\n=== 10. ESTADÍSTICAS DESCRIPTIVAS ===")

        if not df.empty and len(df.columns) > 0:
            print(df.describe(include="all").T)
        else:
            print("No hay datos suficientes para describir.")

        # ====================================================
        # 11. VERIFICACIÓN FINAL DEL ESQUEMA
        # ====================================================

        print("\n=== 11. TIPOS DE DATOS ACTUALIZADOS ===")

        print(df.dtypes)

        print("\n=== VALORES NULOS FINALES ===")

        print(df.isnull().sum())

        print("\n=== PRIMEROS 5 REGISTROS FINALES ===")

        print(df.head())

        # ====================================================
        # 12. RESULTADO DEL PERFILAMIENTO
        # ====================================================

        print("\n" + "=" * 65)
        print(f"ARCHIVO PERFILADO CORRECTAMENTE: {file_key}")
        print("=" * 65)

        return df

    # ========================================================
    # MANEJO DE ERRORES AWS
    # ========================================================

    except ClientError as error:

        codigo = error.response["Error"]["Code"]

        if codigo in ("NoSuchKey", "404"):
            print(f"ERROR: El archivo {file_key} no existe en S3.")

        elif codigo == "ExpiredToken":
            print(
                "ERROR: Las credenciales de AWS Academy "
                "han expirado."
            )

        elif codigo in ("AccessDenied", "403"):
            print(
                "ERROR: No tienes permisos para "
                "acceder al archivo."
            )

        elif codigo == "NoSuchBucket":
            print(
                f"ERROR: El bucket {bucket_name} no existe."
            )

        else:
            print(f"ERROR de AWS S3: {codigo}")

    except BotoCoreError as error:
        print(f"ERROR de comunicación con AWS: {error}")

    except (ParserError, EmptyDataError):
        print(
            "ERROR: El archivo CSV está vacío "
            "o tiene un formato inválido."
        )

    except json.JSONDecodeError:
        print("ERROR: El archivo JSON contiene datos inválidos.")

    except UnicodeDecodeError:
        print("ERROR: No se pudo decodificar el archivo.")

    except (ValueError, TypeError, OverflowError) as error:
        print(f"ERROR al procesar los datos: {error}")

    return None


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 65)
    print("PRÁCTICA: INGESTA Y PERFILAMIENTO DE DATOS EN AWS S3")
    print("=" * 65)

    # ========================================================
    # 1. ESTABLECER CONEXIÓN CON AWS S3
    # ========================================================

    print("\n=== CONFIGURACIÓN DE CONEXIÓN ===")

    try:

        # Obtener cliente S3 y nombre del bucket
        # desde el archivo externo de configuración YAML.
        s3_client, BUCKET_NAME = conectar_s3()

        print("Conexión configurada correctamente.")
        print(f"Bucket seleccionado: {BUCKET_NAME}")

    except (
        OSError,
        KeyError,
        ValueError,
        ClientError,
        BotoCoreError
    ) as error:

        print(f"ERROR al configurar la conexión: {error}")
        raise SystemExit(1)

    # ========================================================
    # 2. CONFIGURAR RUTAS DE LOS ARCHIVOS
    # ========================================================

    print("\n=== CONFIGURACIÓN DE ARCHIVOS ===")

    FILE_KEY_CSV = "raw/transacciones.csv"
    FILE_KEY_JSON = "raw/logs_m2m.json"

    print(f"Ruta CSV: {FILE_KEY_CSV}")
    print(f"Ruta JSON: {FILE_KEY_JSON}")

    # ========================================================
    # 3. PROCESAR ARCHIVO CSV
    # ========================================================

    df_transacciones = cargar_y_perfilar_s3(
        s3_client,
        BUCKET_NAME,
        FILE_KEY_CSV
    )

    # ========================================================
    # 4. PROCESAR ARCHIVO JSON
    # ========================================================

    df_logs = cargar_y_perfilar_s3(
        s3_client,
        BUCKET_NAME,
        FILE_KEY_JSON,
        is_json=True
    )

    # ========================================================
    # 5. VERIFICACIÓN DE RESULTADOS
    # ========================================================

    print("\n" + "=" * 65)
    print("RESULTADOS FINALES DE LA PRÁCTICA")
    print("=" * 65)

    if df_transacciones is not None:
        print("\nCSV: Procesado correctamente.")
        print(f"Registros: {len(df_transacciones)}")
    else:
        print("\nCSV: Error durante el procesamiento.")

    if df_logs is not None:
        print("\nJSON: Procesado correctamente.")
        print(f"Registros: {len(df_logs)}")
    else:
        print("\nJSON: Error durante el procesamiento.")

    if df_transacciones is not None and df_logs is not None:

        print("\n" + "=" * 65)
        print("PRÁCTICA FINALIZADA CORRECTAMENTE")
        print("=" * 65)

    else:

        print("\n" + "=" * 65)
        print("PRÁCTICA FINALIZADA CON ERRORES")
        print("=" * 65)

        raise SystemExit(1)
