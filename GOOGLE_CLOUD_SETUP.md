# Guia de Setup - Google Cloud Console

## Passo 1: Criar Projeto

1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. No topo, clique no seletor de projetos
3. Clique em **"Novo Projeto"**
4. Nome: `imagineread-lite`
5. Clique em **"Criar"**

---

## Passo 2: Ativar APIs

No menu lateral, vá em **APIs e Serviços > Biblioteca** e ative:

- ✅ Cloud Storage API
- ✅ Cloud Firestore API
- ✅ Cloud Run API
- ✅ Cloud Build API

---

## Passo 3: Criar Bucket para Uploads

1. Menu lateral: **Cloud Storage > Buckets**
2. Clique **"Criar"**
3. Configure:
   - Nome: `imagineread-lite-uploads`
   - Região: `southamerica-east1` (São Paulo)
   - Classe: **Standard**
4. Clique **"Criar"**

### Configurar Lifecycle (auto-delete 24h):
1. Abra o bucket criado
2. Aba **"Lifecycle"**
3. **"Adicionar regra"**
   - Ação: **Excluir objeto**
   - Condição: **Idade > 1 dia**
   - Prefixo: `free/`
4. Salvar

---

## Passo 4: Criar Bucket para Frontend

1. Menu lateral: **Cloud Storage > Buckets**
2. Clique **"Criar"**
3. Configure:
   - Nome: `imagineread-lite-web`
   - Região: `southamerica-east1`
   - Classe: **Standard**
4. Depois de criar, vá em **"Permissões"**
5. Clique **"Conceder acesso"**
   - Principal: `allUsers`
   - Função: **Storage Object Viewer**
6. Confirme para tornar público

---

## Passo 5: Ativar Firestore

1. Menu lateral: **Firestore**
2. Clique **"Criar banco de dados"**
3. Modo: **Native** (não Datastore)
4. Localização: `southamerica-east1`
5. Clique **"Criar"**

---

## Passo 6: Criar Service Account

1. Menu: **IAM e Administrador > Contas de Serviço**
2. Clique **"Criar conta de serviço"**
3. Nome: `imagineread-lite-backend`
4. Clique **"Criar e Continuar"**
5. Adicione as funções:
   - **Storage Admin**
   - **Cloud Datastore User**
6. Clique **"Concluído"**
7. Clique nos 3 pontinhos → **"Gerenciar chaves"**
8. **"Adicionar chave" > "Criar nova chave"**
9. Tipo: **JSON**
10. Salve o arquivo como `credentials.json`

---

## Passo 7: Configurar Local

Mova o `credentials.json` para o backend:

```bash
mv ~/Downloads/imagineread-lite-*.json \
   /Users/jp/Documents/APP/ImagineRead/imagineread-lite/backend/credentials.json
```

Atualize o `.env`:

```bash
cd /Users/jp/Documents/APP/ImagineRead/imagineread-lite/backend
cp .env.example .env
```

Edite `.env` com:
```
GOOGLE_CLOUD_PROJECT=imagineread-lite
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
GCS_BUCKET_NAME=imagineread-lite-uploads
ENVIRONMENT=production
```

---

## ✅ Verificação

Após completar, você terá:
- [ ] Projeto `imagineread-lite` criado
- [ ] 2 buckets: `uploads` e `web`
- [ ] Firestore ativo
- [ ] Service account com credenciais
