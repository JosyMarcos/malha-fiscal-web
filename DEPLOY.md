# Como fazer o deploy

## ✅ OPÇÃO 1 — Railway (Recomendado — mais simples)

### Passo a passo:

1. Acesse railway.app e crie uma conta (pode usar o GitHub)

2. Clique em "New Project" → "Deploy from GitHub repo"
   - Faça upload do projeto ou conecte o repositório

3. Adicione um banco PostgreSQL:
   - No projeto, clique em "+ New" → "Database" → "PostgreSQL"
   - O Railway gera a variável DATABASE_URL automaticamente

4. Configure as variáveis de ambiente (Settings → Variables):
   ```
   SECRET_KEY=coloque-uma-chave-longa-aqui
   DEBUG=False
   ALLOWED_HOSTS=suaapp.up.railway.app
   CSRF_TRUSTED_ORIGINS=https://suaapp.up.railway.app
   ```
   (DATABASE_URL já é gerado automaticamente pelo Railway)

5. O deploy acontece automaticamente. Após finalizar:
   - Acesse o link gerado (ex: malhafiscal.up.railway.app)
   - Crie o superusuário pelo Railway Shell:
     ```
     python manage.py createsuperuser
     ```

---

## OPÇÃO 2 — Vercel + Supabase (banco externo gratuito)

### Problema atual:
O Vercel não tem disco — SQLite não funciona lá.
A solução é usar o Supabase como banco PostgreSQL gratuito.

### Passo a passo:

1. **Criar banco no Supabase** (supabase.com):
   - Crie uma conta → New Project
   - Em Settings → Database → Connection string → URI mode
   - Copie a URL (começa com `postgresql://...`)

2. **Configurar variáveis no Vercel** (Settings → Environment Variables):
   ```
   DATABASE_URL=postgresql://postgres:[senha]@db.[id].supabase.co:5432/postgres
   SECRET_KEY=chave-secreta-aqui
   DEBUG=False
   ALLOWED_HOSTS=malhafiscalweb.vercel.app
   CSRF_TRUSTED_ORIGINS=https://malhafiscalweb.vercel.app
   ```

3. **Fazer novo deploy** no Vercel (redeploy após adicionar as variáveis)

4. **Rodar migrations** — no terminal local com DATABASE_URL configurado:
   ```bash
   DATABASE_URL=postgresql://... python manage.py migrate
   DATABASE_URL=postgresql://... python manage.py createsuperuser
   ```

---

## Desenvolvimento local (sem banco externo)

```bash
cd malha-fiscal-web
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Acesse: http://localhost:8000
