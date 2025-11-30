# Robô Global de Afiliados – API (Render + Supabase)

API em **FastAPI** para servir produtos, ranking e pontuação global a partir de tabelas e views no **Supabase**.

Endpoints:

- `GET /` — mensagem inicial e lista de endpoints
- `GET /status` — status da API e checagem básica de config
- `GET /produtos` — lista de produtos da tabela principal
- `GET /ranking` — ranking global (view de ranking no Supabase)
- `GET /pontuacao` — detalhes de pontuação dos produtos
- `POST /atualizar` — dispara função RPC no Supabase para recalcular scores

---

## 1. Variáveis de ambiente

Defina estas variáveis no **Render** (Settings → Environment → Add Environment Variable):

Obrigatórias:

- `SUPABASE_URL` – URL do seu projeto Supabase
- `SUPABASE_KEY` – API key (service role ou anon key com permissões adequadas)

Opcionais (mas recomendadas para tudo funcionar certo):

- `SUPABASE_TABLE_PRODUTOS` – nome da tabela com os produtos (ex: `produtos`)
- `SUPABASE_VIEW_RANKING` – nome da view com o ranking global (ex: `vw_ranking_global`)
- `SUPABASE_VIEW_PONTUACAO` – nome da view com detalhes de pontuação (ex: `vw_pontuacao_produtos`)
- `SUPABASE_ORDER_PRODUTOS` – coluna usada pra ordenar produtos (ex: `score_global_final`)
- `SUPABASE_ORDER_RANKING` – coluna usada pra ordenar o ranking (ex: `score_global_final`)
- `SUPABASE_ORDER_PONTUACAO` – coluna usada pra ordenar a view de pontuação
- `SUPABASE_FUNCTION_ATUALIZAR` – nome da função RPC que recalcula/atualiza os scores no Supabase

Ajuste os nomes de acordo com o **schema real** que você já tem pronto no Supabase.

---

## 2. Rodar localmente (opcional)

1. Crie um arquivo `.env` na raiz do projeto com as mesmas variáveis de ambiente acima.
2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Inicie a API localmente:

   ```bash
   uvicorn main:app --reload
   ```

4. Acesse no navegador:

   - Documentação interativa: `http://127.0.0.1:8000/docs`
   - Status: `http://127.0.0.1:8000/status`

---

## 3. Deploy na Render (usando este repositório)

1. Suba estes arquivos para um repositório **limpo** no GitHub.
2. No painel da **Render**, clique em **New → Web Service**.
3. Conecte com sua conta do GitHub (se ainda não estiver conectada).
4. Selecione o repositório deste projeto.
5. A Render vai detectar o `render.yaml` automaticamente.
6. Confirme o nome do serviço e clique em **Create Web Service**.
7. Assim que o serviço estiver com status de deploy concluído, entre em:
   - Aba **Settings → Environment** e cadastre as variáveis de ambiente.

Depois de salvar as variáveis, você pode usar o botão **Manual Deploy → Clear build cache & deploy** para garantir que tudo suba com a nova configuração.

---

## 4. Testando a API em produção

Suponha que a URL do serviço na Render seja:

```text
https://robo-global-afiliados-api.onrender.com
```

Exemplos:

- Status:
  - `GET https://robo-global-afiliados-api.onrender.com/status`
- Produtos:
  - `GET https://robo-global-afiliados-api.onrender.com/produtos`
- Ranking:
  - `GET https://robo-global-afiliados-api.onrender.com/ranking`
- Pontuação:
  - `GET https://robo-global-afiliados-api.onrender.com/pontuacao`
- Atualizar (POST):

  ```bash
  curl -X POST \
    https://robo-global-afiliados-api.onrender.com/atualizar \
    -H "Content-Type: application/json" \
    -d '{"limite_produtos": 100, "forcar_recalculo": true}'
  ```

Você também pode usar a interface `/docs`:

- `https://robo-global-afiliados-api.onrender.com/docs`

---

Esse pacote já está pronto para ser usado como base do **Robô Global de Afiliados**, bastando alinhar:

1. Os nomes de tabelas/views/funções no Supabase.
2. As variáveis de ambiente na Render.
