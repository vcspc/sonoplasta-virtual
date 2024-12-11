# Sonoplasta Virtual

Um aplicativo web profissional para controle de reprodução de vídeos e apresentações, ideal para sonoplastia, eventos ao vivo, igrejas, teatros e apresentações em geral.

## 🎯 Funcionalidades Principais

### 🎵 Controle de Mídia
- Reprodução de vídeos, áudios e apresentações
- Controle de volume (aumentar/diminuir)
- Função mudo/desmudo
- Play/Pause
- Integração com YouTube para busca e reprodução de vídeos

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
```
3. Instale as dependências:
```bash
pip install -r requirements.txt
```
4. Inicie o servidor:
```bash
python app.py
```

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