# FH6 RGB Smoke Controller

Aplicação Windows em Python para escolher e instalar cores de fumo de drift e de escape/backfire numa instalação local do FH6. A versão atual é a **5.11.1**.

> Projeto não oficial, sem associação à Microsoft, Xbox Game Studios, Playground Games ou Turn 10. Usa apenas numa cópia do jogo que te pertença e guarda sempre os backups.

## Funcionalidades

- 15 opções de fumo, incluindo cinco cores neon e o perfil RGB estático.
- 18 opções de escape/backfire, simples e duplas.
- Pastas independentes para fumo e escapes.
- Backup automático e opção **Restaurar original**.
- Português, inglês, espanhol, francês e alemão.
- Arranque com o Windows opcional, apenas para o utilizador atual.
- Interface redimensionável com o Nissan GT-R e ícone próprio.
- Funcionamento local: sem telemetria, publicidade ou downloads automáticos.

## Executar a partir do código

Requer Windows e Python 3.11 ou superior.

```powershell
py -m pip install --user -r requirements.txt
py app.py
```

Também podes abrir `INICIAR.bat`. O ficheiro apenas verifica Python/Pillow e inicia a aplicação; não instala nem descarrega componentes.

## Criar o EXE

Instala primeiro as dependências de compilação:

```powershell
py -m pip install --user -r requirements.txt
py -m pip install --user -r requirements-build.txt
```

Depois escolhe:

- `build_exe.bat` — pasta `onedir`, mais fácil de inspecionar e recomendada para testes.
- `build_portable.bat` — um único EXE portátil.

O resultado fica em `dist`. Um EXE criado localmente com PyInstaller não possui assinatura digital. Para distribuição pública sem aviso de editor desconhecido, assina o binário final com um certificado Authenticode reconhecido.

## Utilização

1. Fecha o FH6.
2. Em **Local do jogo**, escolhe a pasta principal do jogo para o fumo e a pasta `MediaPC` para os escapes.
3. Escolhe uma cor.
4. Carrega em **Aplicar no jogo** ou **Aplicar escape**.
5. Volta a abrir o jogo para ele recarregar os recursos.

O FH6 não recarrega estas texturas em tempo real. Esta versão não injeta DLLs, não cria hooks e não altera a memória do processo.

## Segurança e Microsoft Defender

A aplicação escreve deliberadamente os overrides escolhidos dentro da pasta do jogo. O **Acesso controlado a pastas** do Windows pode bloquear essa escrita mesmo quando o programa é legítimo. A aplicação não tenta contornar essa proteção.

Antes de distribuir:

1. Compila numa máquina limpa.
2. Calcula e publica o SHA-256 do ficheiro final.
3. Assina o EXE com Authenticode, se possível.
4. Não peças aos utilizadores para desativarem o Defender.

Consulta [SECURITY.md](SECURITY.md) e [DISTRIBUIR_WINDOWS.txt](DISTRIBUIR_WINDOWS.txt) para mais detalhes.

## Estrutura principal

| Caminho | Função |
|---|---|
| `app.py` | Interface principal e navegação |
| `controller.py` | Aplicação, validação, backup e restauro dos efeitos |
| `pages.py` | Páginas internas |
| `visuals.py` | Elementos visuais e efeitos neon |
| `startup.py` | Arranque opcional no Windows |
| `translations.json` | Traduções da interface |
| `assets/` | Ícones, imagens, cartões e recursos de efeitos |

## Limitações

- É necessário reiniciar o jogo depois de aplicar uma cor.
- O perfil RGB combina ciano, rosa e dourado; não é uma animação contínua de arco-íris.
- Atualizações do jogo podem alterar caminhos ou formatos e exigir uma nova versão da aplicação.

## Créditos

- Interface e aplicação: RicardoStonePT.
- Bandeiras: [flag-icons](https://github.com/lipis/flag-icons), licença MIT incluída em `assets/flags`.

