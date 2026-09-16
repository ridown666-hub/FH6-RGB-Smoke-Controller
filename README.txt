FH6 RGB Smoke Controller 5.11.1 — FUMO + ESCAPES

REVISÃO DE SEGURANÇA — 5.11.1
O iniciador normal é agora totalmente local e offline: não executa pip, não
instala pacotes, não descarrega ficheiros e não chama PowerShell ou cmd. A app
apenas lê os seus recursos, guarda definições em %LOCALAPPDATA%/RicardoStonePT/
FH6RGBSmoke e, quando carregas em APLICAR, escreve os overrides selecionados na
pasta FH6 que escolheste, criando backups locais para RESTAURAR ORIGINAL.

O arranque automático é opcional e só usa a chave HKCU do utilizador atual,
quando o ativares na própria app. EXECUTAR FH6 só abre o URI oficial do Steam
depois de carregares nesse botão. Não há serviços, tarefas agendadas, código
obfuscado, rede ou recolha de dados.

O construtor de EXE incluído é manual, local e offline. Não instala
dependências, não descarrega ficheiros e cria apenas uma pasta onedir. Um EXE
sem certificado de assinatura pode continuar a mostrar um aviso SmartScreen;
isso é uma limitação da assinatura do Windows, não uma função da aplicação.
Não desatives o Defender nem cries exclusões sem confirmares primeiro a
origem e o hash do ficheiro.

Se o histórico da Segurança do Windows disser “Acesso a pasta protegida
bloqueado”, trata-se do Acesso controlado a pastas: ao aplicar, a app precisa
de escrever os overrides em media/Physics e MediaPC do FH6. O Defender pode
exigir que o utilizador permita explicitamente o EXE verificado. Isso não é
um vírus e não pode ser contornado de forma segura pelo programa. Para uma
distribuição pública sem aviso de editor desconhecido, assina o EXE com um
certificado Authenticode reconhecido. Consulta DISTRIBUIR_WINDOWS.txt para o
procedimento de partilha, hash e autorização mínima.

Se o arranque indicar que falta Pillow, instala-o uma única vez num terminal:
    py -m pip install --user -r requirements.txt

ILUMINAÇÃO — 5.11.1
O RGB fica integrado nas letras do logótipo e dos títulos de drift, escape,
local do jogo, idiomas, sobre, tamanhos e arranque. A coluna lateral voltou ao
texto simples e claro, mantendo o RGB apenas onde identifica o drift/Backfire.
A linha RGB animada foi removida. As bandeiras têm agora moldura escura,
reflexo de vidro, LEDs e identificação do país sem uma borda branca de foco.

O título principal usa apenas o logótipo RGB nítido fornecido na arte, sem
uma segunda camada desfocada por cima. Isto evita o efeito duplicado,
sobretudo nos tamanhos pequeno e médio.

O fundo é uma única fotografia contínua do Nissan GT-R R35 em toda a janela.
As páginas de escapes, pastas, idiomas, sobre, tamanhos e arranque usam apenas
um véu transparente por cima dessa fotografia, sem repetir a arte. O título
ESCOLHE A COR DO DRIFT recebeu uma presença RGB mais forte. A composição
antiga com a imagem duplicada não é incluída nesta versão.

NOVAS CORES NEON — 5.11.1
Foram acrescentados cinco cartões de drift: TURQUESA NEON, MAGENTA NEON,
LIMA NEON, AMARELO NEON e ULTRAVIOLETA NEON. Cada cartão instala o seu DDS
colorido e usa o mesmo rasto diurno/noturno reforçado das restantes cores.

LUZES DO GTR E TÍTULOS
Os quatro farolins vermelhos do Nissan GT-R recebem uma iluminação vermelha
suave, com uma pulsação lenta e discreta. ESCAPE / BACKFIRE e ESCOLHE A COR
DO ESCAPE usam agora títulos RGB integrados no próprio texto, sem uma linha
RGB separada.

ARTE DO FUNDO — 5.9.0
O fundo usa agora um Nissan GT-R R35 em drift, com quatro farolins redondos,
asa traseira e escapes duplos. A cidade, a estrada molhada e o fumo RGB foram
mantidos na mesma composição. A fotografia duplicada da versão anterior foi
retirada do pacote.

NOVIDADES — 5.3.7
O perfil RGB instala agora também a textura multicolorida `media/Tracks/Brio/smoke.dds`,
com backup e restauro, além dos efeitos XML. Assim o jogo não fica a usar a
textura branca empacotada. O pack de escapes inclui duas combinações neon novas:
CIANO NEON + ROSA e LIMA NEON + ROXO (18 opções no total).

CORREÇÃO DE FUNDO — 5.3.6
O aspeto anterior foi reposto: a interface usa uma única imagem base e as
páginas internas recebem apenas uma camada de vidro transparente. A imagem
de referência da coluna não é usada como fundo; apenas os nove ícones PNG
transparentes são incluídos.

CORREÇÃO DE FUNDO E ÍCONES — 5.3.5
Na página ESCAPE / BACKFIRE é usada uma única camada da arte limpa. A
imagem da interface antiga, que continha cartões repetidos, não fica por
baixo da grelha. A coluna usa ficheiros PNG transparentes extraídos dos
ícones da referência enviada.

CORREÇÃO VISUAL 5.3.3
Removida a borda branca que vinha gravada no recorte do cartão RGB. O cartão
selecionado não mostra visto branco; a seleção é indicada apenas pelo halo
néon colorido. O nome do ZIP foi alterado para evitar abrir uma versão antiga.

CORREÇÃO RGB — 5.3.7
O RGB aplica agora a textura multicolorida e o perfil XML. Aplica três
efeitos diferentes, usando nomes e atributos existentes no XML fornecido:
- Surface_Offroad_Master: ciano, DustRGBDepth 0.000, 1.000, 0.882, 0.550.
- Surface_Dust_Trail: rosa, DustRGBDepth 1.000, 0.118, 0.608, 0.650.
- Surface_Dust_Debri_Wave: dourado, DustRGBDepth 1.000, 0.745, 0.098, 0.400.
A alteração afeta as mesmas superfícies de fumo das cores individuais.
A app valida o XML antes de escrever e confirma o conteúdo após a escrita.

RGB é aqui o nome do perfil multicolorido: uma combinação de ciano, rosa e
dourado na textura e nos efeitos. Não alterna automaticamente entre cores.
Se o FH6 limitar as camadas XML, a textura RGB continua a fornecer o visual
multicolorido; reinicia sempre o jogo depois de aplicar.

Para testar: fecha o FH6, abre esta versão, seleciona RGB, carrega em
APLICAR NO JOGO e volta a abrir o FH6. Testa um drift prolongado em asfalto.
Para voltar ao resultado já conhecido, aplica uma cor individual e reinicia
o jogo. Para recuperar os ficheiros anteriores, usa RESTAURAR ORIGINAL.
O visual da interface, os ícones e os packs do escape são os da 5.3.0.

COMO ABRIR
1. Extrai toda a pasta do ZIP para uma pasta definitiva no Windows.
2. Abre INICIAR.bat. Requer Python 3.11 ou superior com o comando py;
   o iniciador verifica Pillow, mas não instala nada automaticamente.
3. Para criar o EXE localmente, instala manualmente as dependências uma vez:
       py -m pip install --user -r requirements.txt
       py -m pip install --user pyinstaller
   Depois executa build_exe.bat. O resultado fica em
   dist\\FH6_RGB_Smoke_Controller_v5_11_1\\. O script não usa a rede nem
   descarrega componentes. O EXE gerado sem assinatura pode gerar aviso
   SmartScreen.

AS PASTAS CERTAS
Em LOCAL DO JOGO existem dois painéis independentes:
- PASTA DO FUMO: seleciona a pasta principal Forza Horizon 6.
- PASTA DOS ESCAPES: seleciona a pasta MediaPC da instalação.
Ao selecionar a raiz do jogo para os escapes, a app procura a MediaPC.
Se selecionares diretamente MediaPC, usa exatamente essa pasta, sem criar
outra MediaPC dentro dela. Os dois caminhos são guardados separadamente.

EXE PORTÁTIL (UM ÚNICO FICHEIRO)
--------------------------------
Se quiseres copiar apenas um EXE para outro PC, executa
`build_portable.bat`. Ele usa PyInstaller em modo `--onefile` e inclui o
Python, Pillow, traduções, imagens, DDS, bandeiras e ícone no próprio EXE.
O modo normal `build_exe.bat` continua a criar uma pasta `--onedir`, que é
mais simples de inspecionar e normalmente gera menos falsos positivos. Em
ambos os modos, o EXE continua sem assinatura até ser assinado com
Authenticode e o Acesso controlado a pastas pode exigir uma autorização para
escrever dentro da instalação do FH6.

APLICAR E RESTAURAR
Fecha o FH6, escolhe a cor e carrega em APLICAR NO JOGO. Depois abre o jogo.
Fumo: usa CORES DO FUMO. Escape: abre ESCAPE / BACKFIRE.
RESTAURAR ORIGINAL recupera os ficheiros guardados antes da primeira
alteração e remove os overrides criados pela app quando não existia ficheiro
solto. Não apagues os backups se quiseres conservar essa possibilidade.

COMO FUNCIONAM AS CORES
O drift usa a alteração XML da versão em que confirmaste que a cor já era
visível durante o dia. Troca Surface_Smoke por um efeito de poeira colorida,
com DustRGBDepth reforçado e Surface_Dust_Trail. Atua no ficheiro
media/Physics/TireEffectsDefinitions.xml. Pode deixar um rasto breve depois
do drift. O cartão RGB usa o novo perfil experimental descrito no início
deste documento. Os valores das cores individuais continuam iguais.

Os escapes têm 18 conjuntos de cores simples e duplas. Aplicam seis
ficheiros .swatchbin em MediaPC/Particles/Textures/fire/swatches. Alteram a
cor das chamas de backfire existentes; não alteram o som nem tornam as
chamas permanentes. O carro tem de produzir backfire para veres o efeito.

NOVIDADES VISUAIS DA 5.3.0
- Os cartões do escape usam o mesmo acabamento dos cartões do fumo.
  As 18 opções aparecem na mesma janela, sem páginas 1/2 e 2/2.
- Os oito botões da barra lateral têm ícones e moldura néon ciano/magenta,
  incluindo ARRANQUE WINDOWS e TAMANHO DA APP.
- LOCAL DO JOGO usa o fundo completo com a proporção preservada.
  Os painéis e botões das pastas têm o efeito do botão APLICAR NO JOGO.
- SOBRE explica fumo, escapes, caminhos e restauro em quatro painéis.
  O texto ajusta-se ao espaço disponível.
- Português, inglês, espanhol, francês e alemão. A nova janela usa uma coluna
  vertical com bandeiras circulares, moldura neon e indicador de seleção. A
  escolha do idioma fica guardada.
- TAMANHO DA APP permite escolher 1100x619, 1400x788, 1672x941 ou ajustar
  ao ecrã. A dimensão é limitada pelo espaço disponível no monitor.
- O símbolo do pneu enviado por ti é usado na janela e no ícone do EXE;
  o ICO contém os tamanhos necessários para a barra de tarefas do Windows.
- O X de cada painel regressa ao início. O X superior fecha a app.
  Arrasta o cabeçalho para mover; duplo clique maximiza/restaura.

ARRANQUE WINDOWS
A opção está desligada por defeito. O painel permite ativar/desativar a
abertura da app ao iniciar sessão no Windows, apenas para o utilizador atual.
Não inicia o FH6 nem aplica cores automaticamente. Coloca a app numa pasta
definitiva antes de ativar; se a moveres, ativa novamente para atualizar o
caminho. Desativa antes de apagar a app. Sem EXE, mantém Python e a pasta
completa da aplicação.

DEFINIÇÕES E BACKUPS
Continuam em %LOCALAPPDATA%/RicardoStonePT/FH6RGBSmoke.
A nova versão reutiliza as definições e os backups existentes.

VALIDAÇÃO
Passaram 14 testes locais. Cobrem também RGB: seleção pelo cartão, aplicação dos três
efeitos, troca RGB/cor única/RGB, recuperação do original ou remoção do
override novo, rejeição de XML inválido e preservação das cores individuais.
Os oito testes de regressão da interface e do escape também estão incluídos,
com aplicação/restauro em pastas
temporárias, caminhos independentes, MediaPC direta e arranque simulado.
A interface foi renderizada e os limites do texto verificados em 9 páginas,
4 idiomas e 4 dimensões (144 combinações). Foram inspecionadas as imagens
resultantes. A renderização local usa fontes de substituição; não equivale
a um teste da interface no Windows. Não foi possível testar dentro do FH6
nem executar o EXE Windows neste ambiente.

PARA DESENVOLVIMENTO
O ZIP contém os módulos Python necessários, o construtor manual build_exe.bat
e os recursos usados offline. Os testes, pré-visualizações e geradores de
imagens ficam fora do pacote para reduzir a superfície de execução. Os PNG,
DDS, bandeiras e ícone já estão incluídos.

CRÉDITOS DAS BANDEIRAS
flag-icons, https://github.com/lipis/flag-icons — licença MIT.
SVG originais e licença incluídos em assets/flags.
