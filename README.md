# Sonoplasta Virtual

Um aplicativo web profissional para controle de reprodução de vídeos e apresentações, ideal para sonoplastia, eventos ao vivo, igrejas, teatros e apresentações em geral.

## 🎯 Funcionalidades Principais

### 🎵 Controle de Mídia
- Reprodução de vídeos, áudios e apresentações
- Controle de volume (aumentar/diminuir)
- Função mudo/desmudo
- Play/Pause
- Integração com YouTube para busca e reprodução de vídeos
- Geração de QR Code para compartilhamento rápido
- Reprodução de vídeos em tela cheia
- Controle de apresentações de slides
- Reprodução de áudio
- Upload de arquivos com categorização
  - Suporte para vídeos, áudios, apresentações e imagens
  - Categorias disponíveis: Ofertório, Entrada da Plataforma, Despedida, Adoração Infantil
  - Acesse em: https://localhost:5000/upload-page

### 🎞️ Gerenciamento de Apresentações
- Navegação entre slides (anterior/próximo)
- Modo apresentação (F5)
- Suporte a múltiplos formatos

### 🎨 Interface
- Design responsivo e moderno
- Modo escuro/claro
- Tela cheia
- Controles ocultáveis
- Menu lateral com acesso rápido
- Busca integrada de arquivos

### 🖥️ Controles do Sistema
- Minimizar janela (Win+D)
- Maximizar janela (Win+↑)
- Alternar entre aplicativos (Alt+Tab)
- Fechar aplicativo atual (Alt+F4)

## 📁 Formatos Suportados

### Áudio
- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- M4A (.m4a)
- WMA (.wma)

### Vídeos
- MP4 (.mp4)
- AVI (.avi)
- MKV (.mkv)
- MOV (.mov)

### Apresentações
- PowerPoint (.ppt, .pptx)
- LibreOffice (.odp)
- Keynote (.key)
- PDF (.pdf)

## 🚀 Instalação

### Pré-requisitos
- Python 3.7 ou superior
- Navegador web moderno (Chrome, Firefox, Edge, etc.)
- Chave de API do YouTube (para funcionalidades do YouTube)

### Instalação
1. Clone este repositório
2. Crie um arquivo `.env` e adicione sua chave API do YouTube:
```
YOUTUBE_API_KEY=sua_chave_aqui
UPLOAD_PASSWORD=sua_senha_de_upload
```
3. Instale as dependências:
```bash
pip install -r requirements.txt
```
4. Configure o Firewall do Windows:
   - Pressione `Win + R`
   - Digite `wf.msc` e pressione Enter
   - Clique em "Regras de Entrada" no painel esquerdo
   - Clique em "Nova Regra..." no painel direito
   - Selecione "Porta" e clique em "Próximo"
   - Selecione "TCP" e digite "5000" em "Portas locais específicas"
   - Clique em "Próximo" e selecione "Permitir a conexão"
   - Siga as etapas restantes mantendo as opções padrão
   - Nomeie a regra como "Sonoplasta Virtual"

5. Inicie o servidor:
```bash
python app.py
```

### 💡 Dicas para Melhor Experiência
- Use o Git Bash como terminal padrão para melhor compatibilidade
- Configure seu navegador para abrir em uma nova aba ao iniciar
- Mantenha os arquivos de mídia organizados em subpastas para facilitar a busca
- Use o QR Code para compartilhar rapidamente o acesso com outros dispositivos na rede
- A senha padrão para upload de arquivos é definida na variável de ambiente `UPLOAD_PASSWORD`

## 📱 Uso

### Atalhos de Teclado
- `Espaço`: Play/Pause
- `↑`: Aumentar volume
- `↓`: Diminuir volume
- `M`: Mudo/Desmudo
- `F11`: Tela cheia
- `H`: Ocultar controles
- `←/→`: Navegar entre slides
- `F5`: Modo apresentação
- `Alt+F4`: Fechar aplicativo
- `Win+D`: Mostrar área de trabalho
- `Win+↑`: Maximizar janela
- `Alt+Tab`: Alternar aplicativos

### Organização
- Coloque seus arquivos na pasta `files`
- Use a busca integrada para encontrar arquivos
- Arquivos são categorizados automaticamente por tipo

## ⚠️ Solução de Problemas

### Certificado SSL
O sistema usa HTTPS com certificado auto-assinado. Na primeira execução:
1. O certificado será gerado automaticamente
2. Aceite o certificado no navegador quando solicitado

### Arquivos não Aparecem
- Verifique se os arquivos estão na pasta `files`
- Verifique se o formato é suportado
- Certifique-se que o nome do arquivo contém o termo buscado

### YouTube
- Verifique se a chave API está configurada no arquivo `.env`
- Certifique-se de ter conexão com internet
- A busca retorna os 10 primeiros resultados

## 🔧 Requisitos do Sistema
- Sistema operacional: Windows/Linux
- Navegador web moderno
- Python 3.7+
- Conexão com internet (para funcionalidades do YouTube)