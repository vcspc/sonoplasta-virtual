# Sonoplasta Virtual

Um aplicativo web para controle de reprodução de vídeos e apresentações, ideal para sonoplastia e apresentações em eventos.

## 🚀 Instalação

### Pré-requisitos
- Python 3.7 ou superior
- Navegador web moderno (Chrome, Firefox, Edge, etc.)

### Instalação Rápida
1. Baixe ou clone este repositório
2. Coloque seus arquivos (vídeos e apresentações) na pasta `files`
3. Dê duplo clique no arquivo `run.bat`

### Instalação Manual
1. Ative o ambiente virtual:
```bash
.venv\Scripts\activate.bat
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Inicie o servidor:
```bash
python app.py
```

## 📱 Uso

### Acesso Local
- Abra https://localhost:5000 no navegador

### Acesso Remoto
- Abra https://[IP-DO-COMPUTADOR]:5000 em qualquer dispositivo na mesma rede
- Exemplo: https://192.168.1.100:5000

### Controles
- 🔍 **Busca**: Digite o nome do arquivo na caixa de pesquisa
- ⏯️ **Play/Pause**: Botão central ou tecla Espaço
- 🔊 **Volume**: Botões de volume ou teclas ↑/↓
- 🔇 **Mudo**: Botão de mudo ou tecla M
- 📺 **Tela Cheia**: Botão de expandir ou tecla F11
- 👁️ **Ocultar Controles**: Botão de olho ou tecla H
- ⬅️ **Slide Anterior**: Botão esquerdo ou tecla ←
- ➡️ **Próximo Slide**: Botão direito ou tecla →
- 🖥️ **Modo Apresentação**: Botão desktop ou tecla F5

### Atalhos de Teclado
- `Espaço`: Play/Pause
- `↑`: Aumentar volume
- `↓`: Diminuir volume
- `←`: Slide anterior
- `→`: Próximo slide
- `M`: Mudo/Desmudo
- `F5`: Modo apresentação
- `F11`: Tela cheia
- `H`: Ocultar controles do player

## 📁 Formatos Suportados

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

## 💡 Dicas
1. Coloque seus arquivos na pasta `files` antes de iniciar
2. Use nomes descritivos para facilitar a busca
3. Aceite o certificado de segurança ao acessar via HTTPS
4. Para melhor experiência, use em tela cheia

## ⚠️ Solução de Problemas

### Certificado de Segurança
Se aparecer aviso de certificado:
1. Clique em "Avançado"
2. Clique em "Prosseguir para o site"

### Arquivos não Aparecem
- Verifique se os arquivos estão na pasta `files`
- Verifique se o formato é suportado
- Tente reiniciar o servidor

### Controles não Funcionam
- Verifique se o arquivo está em foco
- Tente clicar na tela primeiro
- Use os atalhos de teclado como alternativa

## 🔧 Requisitos do Sistema
- Windows 7/8/10/11
- 4GB RAM (mínimo)
- Espaço em disco suficiente para seus arquivos
- Conexão de rede (para acesso remoto)

## 📝 Notas
- O aplicativo usa HTTPS para segurança
- Os controles funcionam melhor em tela cheia
- Mantenha o Python e as dependências atualizados
- O ambiente virtual (.venv) mantém as dependências isoladas