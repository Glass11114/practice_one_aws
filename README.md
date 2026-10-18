
# Práctica 1: Perfilamiento e Ingesta Multi-Fuente en AWS S3

## Descripción
Esta práctica implementa un proceso de ingesta y perfilamiento
de datos estructurados (CSV) y semiestructurados (JSON)
almacenados en Amazon S3 mediante Python.

El programa descarga los archivos en memoria y utiliza Pandas
para analizar su estructura y generar estadísticas descriptivas.

## Tecnologías utilizadas
- Python
- Amazon Web Services (AWS S3)
- Boto3
- Pandas
- PyYAML
- Git y GitHub

## Estructura del proyecto

practice_one_aws/
├── .gitignore
├── README.md
└── practica1/
    ├── conexion.py
    ├── perfilamiento.py
    ├── config.example.yaml
    └── requirements.txt

## Archivos procesados

- raw/transacciones.csv
- raw/logs_m2m.json

## Instalación

1. Clonar el repositorio:

   git clone https://github.com/Glass11114/practice_one_aws.git

2. Entrar a la práctica:

   cd practice_one_aws/practica1

3. Crear y activar un entorno virtual:

   python3 -m venv .venv
   source .venv/bin/activate

4. Instalar las dependencias:

   python -m pip install -r requirements.txt

## Configuración de AWS

Crear un archivo privado config.yaml tomando como referencia
config.example.yaml.

Configurar la región, el bucket y las credenciales temporales
proporcionadas por AWS Academy.

IMPORTANTE:
El archivo config.yaml contiene información sensible y está
excluido del repositorio mediante .gitignore.

Nunca publiques credenciales reales en GitHub.

## Ejecución

Desde la carpeta practica1:

   python perfilamiento.py

## Resultados

El programa realiza el perfilamiento de dos archivos:

CSV:
- 500 registros
- 7 columnas

JSON:
- 300 registros
- 9 columnas

Para cada archivo se muestran:
- Dimensiones del dataset
- Tipos de datos
- Estadísticas descriptivas

## Seguridad

Las credenciales se almacenan en un archivo YAML privado.
El módulo conexion.py utiliza esta configuración para
establecer la conexión con Amazon S3 mediante Boto3.

## Autor

Gladis Esther Vázquez Pérez

Universidad Tecnológica Bilingüe Internacional
y Sustentable de Puebla.
