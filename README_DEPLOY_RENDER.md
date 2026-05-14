# Deploy do FINANTEC no Render

## Configuração no Render

- Tipo: Web Service
- Language: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

## Variáveis de ambiente

Configure no Render em Environment:

- `SECRET_KEY`: uma chave grande e aleatória
- `DATABASE_URL`: URL do PostgreSQL/Neon com `sslmode=require`

## Observações

O `app.py` foi ajustado para não deixar senha do banco no código e para rodar com `debug=False`.
Os HTMLs devem ficar dentro da pasta `templates/`, pois o Flask usa `render_template()`.
