# Como instalar

## 1. Criar o repositório

Crie um repo **público** chamado exatamente `Fafarojas` (igual ao seu usuário).
Não marque "Add a README" — os arquivos já vêm prontos aqui.

## 2. Subir os arquivos

```bash
git init
git add .
git commit -m "feat: perfil pixel"
git branch -M main
git remote add origin https://github.com/Fafarojas/Fafarojas.git
git push -u origin main
```

Estrutura final:

```
README.md
SETUP.md
assets/
  hero.svg          # banner animado (gerado uma vez)
  commits.svg       # barra de commits (regenerada todo dia)
scripts/
  pixelfont.py      # fonte pixel 5x7 compartilhada
  gen_hero.py       # gera o banner
  gen_commits.py    # lê a API pública de contribuições e gera a barra
.github/workflows/
  pixel-stats.yml   # roda o gen_commits.py diariamente
```

## 3. Ligar a atualização automática

Em **Settings → Actions → General → Workflow permissions**, marque
*Read and write permissions*. Sem isso a Action não consegue commitar o SVG novo.

Depois vá em **Actions → pixel stats → Run workflow** para rodar a primeira vez.
Não precisa de token nem secret: o script lê o endpoint público
`github.com/users/Fafarojas/contributions`.

## 4. Regenerar localmente (opcional)

```bash
python3 scripts/gen_hero.py      # depois de mexer nas cores ou no mascote
python3 scripts/gen_commits.py   # puxa os commits na hora
```

## Ajustes rápidos

| O quê | Onde |
|---|---|
| Paleta | constantes no topo de `gen_hero.py` e `RAMP` em `gen_commits.py` |
| Mascote | lista `SPRITE` em `gen_hero.py` (mapa de 24x20 caracteres) |
| Janela do gráfico | `weekly(days, weeks=26)` em `gen_commits.py` |
| Altura máxima das barras | `MAX_BLOCKS` em `gen_commits.py` |
| Velocidade das animações | bloco `<style>` de cada gerador |

O mapa do mascote usa uma letra por cor: `K` contorno, `P`/`p` roxo, `M` menta,
`C` ciano, `N` rosa, `Y` pêssego, `W` branco, `.` transparente. Toda linha precisa
ter exatamente 24 caracteres.
