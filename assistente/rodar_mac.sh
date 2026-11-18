#!/bin/bash
# Citizen Assist AI - Gustavo Zibini Belizario - RM 561376
# Prepara o ambiente Python e roda o assistente com o Ollama.
# Uso: bash rodar_mac.sh            (avaliação antes/depois)
#      bash rodar_mac.sh conversar  (menu para usar o assistente)
set -e
cd "$(dirname "$0")"
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
  echo "Precisa do Python 3.10 ou mais novo. Instale em https://www.python.org/downloads/ e rode de novo."
  exit 1
fi
if [ ! -x .venv/bin/python ]; then
  echo "Criando ambiente Python (só na primeira vez)..."
  python3 -m venv .venv
  .venv/bin/pip install -q --upgrade pip
  .venv/bin/pip install -q -r requirements.txt
fi
.venv/bin/python rodar_local.py "${1:-avaliar}"
