import discord
from groq import Groq
import time

# 🔹 Coloque suas chaves direto aqui
DISCORD_TOKEN = ""
GROQ_API_KEY = ""

# 🔹 Inicializar cliente Groq
client = Groq(api_key=GROQ_API_KEY)

# 🔹 Configurar intents do Discord
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# =========================
# MEMÓRIA TEMPORÁRIA
# =========================

memoria = {}
TEMPO_MEMORIA = 20 * 60  # 20 minutos


@bot.event
async def on_ready():
    print(f'✅ Online como {bot.user}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!ia"):
        pergunta = message.content[3:].strip()

        if not pergunta:
            await message.channel.send("❌ Use: !ia **pergunta**")
            return

        user_id = str(message.author.id)
        agora = time.time()

        # =========================
        # NOME DO USUÁRIO
        # =========================

        nome_exibicao = message.author.display_name
        username = message.author.name

        # cria memória do usuário
        if user_id not in memoria:
            memoria[user_id] = {
                "historico": [],
                "ultimo_tempo": agora
            }

        # verifica se expirou
        tempo_passado = agora - memoria[user_id]["ultimo_tempo"]

        if tempo_passado > TEMPO_MEMORIA:
            memoria[user_id]["historico"] = []

        memoria[user_id]["ultimo_tempo"] = agora

        # =========================
        # PROMPT FIXO
        # =========================

        system_prompt = (
            " "
        )

        # adiciona mensagem do usuário
        memoria[user_id]["historico"].append({
            "role": "user",
            "content": pergunta
        })

        # limita histórico
        memoria[user_id]["historico"] = memoria[user_id]["historico"][-20:]

        mensagens = [
            {"role": "system", "content": system_prompt}
        ] + memoria[user_id]["historico"]

        try:
            resposta = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=mensagens
            )

            texto = resposta.choices[0].message.content

            # salva resposta da IA
            memoria[user_id]["historico"].append({
                "role": "assistant",
                "content": texto
            })

            if len(texto) > 2000:
                texto = texto[:1990] + "..."

            await message.channel.send(texto)

        except Exception as e:
            print("ERRO:", e)
            await message.channel.send(
                "❌ Erro:/ talvez eu esteja com problemas no codigo!!!!."
            )


bot.run(DISCORD_TOKEN)