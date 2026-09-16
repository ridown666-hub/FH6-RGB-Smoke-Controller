# Revisão de segurança — FH6 RGB Smoke Controller 5.11.1

## Escopo

Esta versão foi revista como pacote de código-fonte Python. O iniciador normal
é offline e não instala software, não descarrega ficheiros e não executa
PowerShell, `cmd`, tarefas agendadas ou serviços. O `build_exe.bat` incluído é
um construtor manual local: apenas chama o PyInstaller já instalado pelo
utilizador e cria uma pasta onedir com os recursos locais.

## Ações intencionais

- Ler os recursos visuais e as traduções incluídas na própria pasta.
- Guardar preferências e cópias de segurança em
  `%LOCALAPPDATA%\RicardoStonePT\FH6RGBSmoke`.
- Escrever apenas os overrides de fumo/escape dentro da pasta FH6 escolhida
  pelo utilizador; `RESTAURAR ORIGINAL` repõe ou remove esses overrides.
- Registar a abertura automática em `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
  apenas depois de o utilizador carregar em **Ativar**.
- Abrir o URI `steam://rungameid/2483190` apenas depois de o utilizador carregar
  em **Executar FH6**.

## Avisos do Windows

O ZIP não contém um EXE compilado; contém apenas o construtor manual. Um EXE
criado com PyInstaller é sem assinatura digital e pode gerar um aviso
SmartScreen mesmo sendo legítimo; isso não pode ser eliminado sem um
certificado de assinatura de código. Não desatives o Microsoft Defender nem
adiciones exclusões só para ultrapassar um aviso. Confirma a origem do ZIP e
compara o SHA-256 antes de o abrir.

O Acesso controlado a pastas é um bloqueio diferente do SmartScreen. Quando
carregas em APLICAR, a app escreve deliberadamente os overrides em
`media/Physics` e `MediaPC` da pasta FH6 escolhida. Se essa proteção estiver
ativa, o Windows pode bloquear uma app legítima porque o diretório do jogo está
protegido. Não há uma forma segura de a aplicação contornar essa política. O
utilizador deve permitir apenas o EXE verificado em Segurança do Windows >
Proteção contra vírus e ameaças > Gerir proteção contra ransomware > Permitir
uma aplicação através do acesso controlado a pastas. Nunca é necessário
desativar o Defender globalmente.

Para distribuição sem esse aviso de editor desconhecido, o EXE final tem de
ser assinado com um certificado Authenticode reconhecido. Um certificado
autoassinado apenas funciona depois de cada computador confiar nele, pelo que
não resolve a distribuição para o público em geral. As instruções completas
estão em `DISTRIBUIR_WINDOWS.txt`.
