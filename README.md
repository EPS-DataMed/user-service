# User Service

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=EPS-DataMed_user-service&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=EPS-DataMed_user-service) [![Coverage]([https://sonarcloud.io/api/project_badges/measure?project=EPS-DataMed_user-service&metric=coverage](https://sonarcloud.io/component_measures?id=EPS-DataMed_user-service&pullRequest=11&metric=new_coverage&view=list))](https://sonarcloud.io/summary/new_code?id=EPS-DataMed_user-service) [![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=EPS-DataMed_user-service&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=EPS-DataMed_user-service)

Serviço do DataMed responsável pelo gerenciamento de usuários

## Requisitos

- Python 3.9 ou superior
- SQLite (ou outro banco de dados de sua escolha)

## Instalação

1. Clone o repositório:

2. Crie um ambiente virtual
```
python -m venv venv
source venv/bin/activate 
```
Obs: No Windows use `venv\Scripts\activate`

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Rode o projeto
```
uvicorn app.main:app --reload
```


Obs: para rodar os testes:
```
pytest
```
