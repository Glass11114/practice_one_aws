
import boto3
import yaml

def conectar_s3():
    with open("config.yaml", "r", encoding="utf-8") as archivo:
        config = yaml.safe_load(archivo)

    aws = config["aws"]

    credenciales = {
        "aws_access_key_id": aws["access_key_id"],
        "aws_secret_access_key": aws["secret_access_key"],
        "aws_session_token": aws["session_token"]
    }

    cliente = boto3.client(
        "s3",
        region_name=aws["region"],
        **credenciales
    )

    return cliente, aws["bucket_name"]
