import discord
import random
import aiohttp
import os

async def tabela_brasileirao():
    URL = 'https://api.football-data.org/v4/competitions/BSA/standings'
    headers = {'X-Auth-Token': os.environ['FOOTBALL_TOKEN']}

    async with aiohttp.ClientSession() as session:
        async with session.get(URL, headers=headers) as response:
            if response.status != 200:
                return None
            dados = await response.json()

    rodada = dados['season']['currentMatchday']
    tabela = dados['standings'][0]['table']

    cabecalho = f'{"Pos":>3}│ {"Time":<10}│{"Pts":>4}│{"J":>3}│{"V":>3}│{"E":>3}│{"D":>3}│{"SG":>4}'
    divisoria = '┼'.join('─' * n for n in (3, 11, 4, 3, 3, 3, 3, 4))
    linhas = [cabecalho, divisoria]

    for time in tabela:
        posicao = time['position']
        nome_time = time['team']['shortName'][:10]
        pontos = time['points']
        jogos = time['playedGames']
        vitorias = time['won']
        empates = time['draw']
        derrotas = time['lost']
        saldo_gols = time['goalDifference']
        linha_formatada = f'{posicao:>3}│ {nome_time:<10}│{pontos:>4}│{jogos:>3}│{vitorias:>3}│{empates:>3}│{derrotas:>3}│{saldo_gols:>4}'
        linhas.append(linha_formatada)

    return "\n".join(linhas), rodada

SUBREDDITS = ['MemesBrasil', 'MemesBR', 'MemesFutebol', 'ShitpostBR']
async def get_meme():
  async with aiohttp.ClientSession() as session:
    async with session.get(f'https://meme-api.com/gimme/{random.choice(SUBREDDITS)}') as response:
      if response.status == 200:
        json_data = await response.json()
        return json_data.get('url')
      else:
        return None

class MyClient(discord.Client):
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))

  async def on_message(self, message):
    if message.author == self.user:
      return
    elif message.content.startswith('!meme'):
       meme = await get_meme()
       if meme:
        await message.channel.send(meme)
       else:
        await message.channel.send('Não consegui pegar um meme agora, tenta de novo!')
    elif message.content.startswith('!fala'):
      await message.channel.send('Fala irmão, posso te ajudar com o que hoje?')
    elif message.content.startswith('!perfil'):
      if message.mentions:
        user = message.mentions[0]
      else:
        user = message.author
      embed = discord.Embed(title="Informações do usuário", color=discord.Color.blue())
      embed.add_field(name="Nome de usuário", value=user.name, inline=True)
      embed.add_field(name="ID do usuário", value=user.id, inline=True)
      embed.add_field(name="Conta criada em", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
      if message.guild and hasattr(user, 'joined_at'):
        embed.add_field(name="Entrou no servidor em", value=user.joined_at.strftime("%d/%m/%Y"), inline=True)
      await message.channel.send(embed=embed)
    elif message.content.startswith('!tabela'):
      resultado = await tabela_brasileirao()
      if resultado is None:
        await message.channel.send('Não consegui buscar a tabela agora, tenta de novo em instantes!')
      else:
        texto, rodada = resultado
        embed = discord.Embed(title="🏆 Tabela do Brasileirão", description=f'```\n{texto}\n```', color=discord.Color.green())
        embed.set_footer(text=f'Rodada {rodada}')
        await message.channel.send(embed=embed)
    elif message.content.startswith('!help'):
      await message.channel.send('Comandos disponíveis: !meme, !fala, !help, !tabela, !perfil')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(os.environ['DISCORD_TOKEN'])