# =============================================================================
# Dockerfile – imagem do frontend da Loja
# -----------------------------------------------------------------------------
# O que faz: constrói uma imagem nginx que serve a página e faz proxy para a API.
#
# Construir isolado (opcional): docker build -t loja-frontend:0.2 app/frontend
# Normalmente é o docker compose que o constrói.
# =============================================================================

# 1) Imagem base: nginx "unprivileged".
#    É a variante oficial da nginx Inc. que corre SEM ser root (menor
#    privilégio, tal como na imagem da API). Escuta na porta 8080.
#    "alpine" = distribuição Linux mínima (imagem pequena).
FROM nginxinc/nginx-unprivileged:1.27-alpine

# 2) Configuração do nginx, como TEMPLATE.
#    Ao arrancar, a imagem processa os ficheiros de /etc/nginx/templates/ e
#    gera /etc/nginx/conf.d/default.conf, preenchendo ${NGINX_LOCAL_RESOLVERS}
#    (precisa de NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1, definido no Compose e no
#    Kubernetes). Ver explicação no nginx.conf.
COPY nginx.conf /etc/nginx/templates/default.conf.template

# 3) A página estática.
COPY index.html /usr/share/nginx/html/index.html

# 4) Documenta a porta (a publicação real faz-se no docker-compose).
EXPOSE 8080

# 5) Verificação de saúde através do endereço /healthz definido no nginx.conf.
#    O wget do Alpine (BusyBox) chega para isto; não é preciso instalar nada.
#    Usamos 127.0.0.1 e NÃO "localhost": dentro do contentor o nome "localhost"
#    pode ser traduzido para o endereço IPv6 (::1), onde o nginx não escuta
#    (só escuta em IPv4), e o wget recebia "Connection refused" mesmo com o
#    nginx a funcionar (Passo 6, Parte E).
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1

# O comando de arranque (nginx em primeiro plano) já vem definido na imagem base.