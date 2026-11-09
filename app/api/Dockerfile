# =============================================================================
# Dockerfile – imagem da API da Loja
# -----------------------------------------------------------------------------
# O que faz: descreve, passo a passo, como construir a imagem Docker da API.
# Cada instrução cria uma "camada". O Docker guarda as camadas em cache, por
# isso a ORDEM das instruções importa: o que muda menos vai primeiro.
#
# Construir:  docker build -t loja-api:0.3 app/api
# Correr:     docker run -d -p 8000:8000 --name loja-api loja-api:0.3
# =============================================================================

# 1) Imagem de partida.
#    "slim" = versão pequena do Python (menos tamanho, menos superfície de
#    ataque). Fixamos a versão (3.12) para o resultado ser previsível.
FROM python:3.12-slim

# 2) Variáveis de ambiente do Python.
#    PYTHONDONTWRITEBYTECODE: não criar ficheiros .pyc (ficam inúteis no contentor).
#    PYTHONUNBUFFERED: mostrar os logs logo (sem os guardar em memória), para
#    aparecerem de imediato em `docker logs`.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3) Pasta de trabalho dentro do contentor. Os comandos seguintes correm aqui.
WORKDIR /app

# 4) Instalar dependências ANTES de copiar o código.
#    Porquê? Se só mudares o main.py, o Docker reutiliza esta camada em cache
#    e não volta a descarregar tudo (builds muito mais rápidos).
#    --no-cache-dir: não guarda a cache do pip dentro da imagem (mais pequena).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copiar o código da aplicação.
COPY main.py .

# 6) Segurança: não correr como administrador (root).
#    Se alguém explorar uma falha na aplicação, fica com poderes limitados.
RUN useradd --create-home --uid 1001 appuser
USER appuser

# 7) Documenta que a aplicação escuta na porta 8000.
#    ATENÇÃO: EXPOSE é só documentação; quem publica a porta é o `-p` no docker run.
EXPOSE 8000

# 8) Verificação de saúde: de 30 em 30 segundos, o Docker chama /saude.
#    Se falhar várias vezes, o contentor fica marcado como "unhealthy".
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/saude')" || exit 1

# 9) Comando que arranca a aplicação.
#    --host 0.0.0.0: escuta em todas as interfaces (necessário para se poder
#    aceder de fora do contentor; com 127.0.0.1 só funcionaria lá dentro).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]