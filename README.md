# Sonoplasta Virtual

Um aplicativo web para controle de reprodução de vídeos, ideal para sonoplastia em apresentações, eventos ou uso pessoal.

## 🚀 Instalação

### Pré-requisitos
- Python 3.7 ou superior
- Navegador web moderno (Chrome, Firefox, Edge, etc.)

### Instalação Rápida
1. Baixe ou clone este repositório
2. Coloque seus vídeos na pasta `videos`
3. Dê duplo clique no arquivo `run.bat`

### Instalação Manual
1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Inicie o servidor:
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
- 🔍 **Busca**: Digite o nome do vídeo na caixa de pesquisa
- ⏯️ **Play/Pause**: Botão central ou tecla Espaço
- 🔊 **Volume**: Botões de volume ou teclas ↑/↓
- 🔇 **Mudo**: Botão de mudo ou tecla M
- 📺 **Tela Cheia**: Botão de expandir ou tecla F11
- 👁️ **Ocultar Controles**: Botão de olho ou tecla H

### Atalhos de Teclado
- `Espaço`: Play/Pause
- `↑`: Aumentar volume
- `↓`: Diminuir volume
- `M`: Mudo/Desmudo
- `F11`: Tela cheia
- `H`: Ocultar controles do player

## 📁 Formatos Suportados
- MP4 (.mp4)
- AVI (.avi)
- MKV (.mkv)
- MOV (.mov)

## 💡 Dicas
1. Coloque seus vídeos na pasta `videos` antes de iniciar
2. Use nomes descritivos para facilitar a busca
3. Aceite o certificado de segurança ao acessar via HTTPS
4. Para melhor experiência, use em tela cheia

## ⚠️ Solução de Problemas

### Certificado de Segurança
Se aparecer aviso de certificado:
1. Clique em "Avançado"
2. Clique em "Prosseguir para o site"

### Vídeos não Aparecem
- Verifique se os vídeos estão na pasta `videos`
- Verifique se o formato é suportado
- Tente reiniciar o servidor

### Controles não Funcionam
- Verifique se o vídeo está em foco
- Tente clicar na tela do vídeo primeiro
- Use os atalhos de teclado como alternativa

## 🔧 Requisitos do Sistema
- Windows 7/8/10/11
- 4GB RAM (mínimo)
- Espaço em disco suficiente para seus vídeos
- Conexão de rede (para acesso remoto)

## 📝 Notas
- O aplicativo usa HTTPS para segurança
- Os controles funcionam melhor em tela cheia
- Mantenha o Python e as dependências atualizados