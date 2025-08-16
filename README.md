🤖 bot-dd

Bot Discord em Python com mensagens visuais de boas‑vindas e despedida.







📌 O que ele faz

Dá boas‑vindas e despedidas com imagens personalizadas (avatar circular, fundo preto, fonte Anton).

Envia mensagens somente no servidor do evento (sem spam entre servidores).

Possui comando !testar para gerar amostras manuais.

✨ Destaques

🖼️ Avatar recortado + título branco + nome em vermelho com emoji.

🔧 Textos, cores, fontes e canais configuráveis.

🧪 Comando de teste para validar sem precisar entrada/saída real.

📂 Estrutura simples: main.py, fonts/, requirements.txt.

⚠️ Importante: nunca exponha seu DISCORD_TOKEN. Use variáveis de ambiente.

📂 Estrutura

bot-dd/
├── fonts/               # Anton-Regular.ttf
├── main.py              # Código principal do bot
├── requirements.txt     # Dependências
└── .gitignore

🚀 Como rodar

1. Requisitos

Python 3.11+

Bot criado no Discord Developer Portal com Server Members Intent habilitado.

2. Instalação

git clone https://github.com/therunnas/bot-dd.git
cd bot-dd
python -m pip install -r requirements.txt

3. Configuração

Crie um arquivo .env na raiz:

DISCORD_TOKEN=SEU_TOKEN_AQUI
GUILD_ID=0
LOG_CHANNEL_ID=0

4. Executar

python main.py

⚙️ Tecnologias

discord.py 2.x

Pillow (PIL)

🗺️ Roadmap



🤝 Contribuição

Faça um fork

Crie sua branch: git checkout -b feat/nova-feature

Commit: git commit -m "feat: nova feature"

Push: git push origin feat/nova-feature

Abra um Pull Request

📜 Licença

MIT. Veja o arquivo LICENSE para mais detalhes.

Feito com ☕ + discord.py. Se curtir, deixe uma ⭐ no repo!
