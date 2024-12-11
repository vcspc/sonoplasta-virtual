import os
import sys
import subprocess
import time
import venv
from pathlib import Path

def print_colored(text, color):
    """Imprime texto colorido"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'blue': '\033[94m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def print_header():
    """Imprime o cabeçalho"""
    print("\n===================================")
    print("      Sonoplasta Virtual")
    print("===================================\n")

def check_python():
    """Verifica se o Python está instalado corretamente"""
    print_colored("[INFO] Verificando instalação do Python...", "blue")
    if sys.version_info < (3, 7):
        print_colored("[ERRO] Python 3.7 ou superior é necessário!", "red")
        print("Você pode baixar em: https://www.python.org/downloads/")
        return False
    return True

def setup_venv():
    """Configura o ambiente virtual"""
    venv_path = Path('.venv')
    if not venv_path.exists():
        print_colored("[INFO] Criando ambiente virtual...", "blue")
        try:
            venv.create('.venv', with_pip=True)
        except Exception as e:
            print_colored(f"[ERRO] Falha ao criar ambiente virtual: {e}", "red")
            return False
    
    # Ativa o ambiente virtual
    if sys.platform == 'win32':
        activate_script = venv_path / 'Scripts' / 'activate.bat'
    else:
        activate_script = venv_path / 'bin' / 'activate'
    
    if not activate_script.exists():
        print_colored("[ERRO] Script de ativação não encontrado!", "red")
        return False
    
    print_colored("[INFO] Ambiente virtual configurado com sucesso!", "green")
    return True

def install_dependencies():
    """Instala as dependências necessárias"""
    print_colored("[INFO] Instalando dependências...", "blue")
    
    pip_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    try:
        subprocess.run(pip_cmd, check=True)
        print_colored("[INFO] Dependências instaladas com sucesso!", "green")
        return True
    except subprocess.CalledProcessError:
        print_colored("[ERRO] Falha ao instalar dependências", "red")
        print_colored("[INFO] Tentando instalar uma por uma...", "blue")
        
        dependencies = [
            "flask==2.0.1",
            "pyautogui==0.9.53",
            "python-dotenv==0.19.0",
            "cryptography==41.0.7"
        ]
        
        for dep in dependencies:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
                print_colored(f"[INFO] {dep} instalado com sucesso!", "green")
            except subprocess.CalledProcessError:
                print_colored(f"[ERRO] Falha ao instalar {dep}", "red")
                return False
    return True

def setup_files():
    """Configura a estrutura de arquivos"""
    files_dir = Path('files')
    if not files_dir.exists():
        print_colored("[INFO] Criando pasta files...", "blue")
        files_dir.mkdir(exist_ok=True)
        print_colored("[INFO] Por favor, coloque seus arquivos (vídeos e apresentações) na pasta 'files'", "blue")

def run_server():
    """Executa o servidor Flask"""
    print_colored("\n[INFO] Iniciando servidor...", "blue")
    print_colored("\nServidor iniciado! Acesse:", "green")
    print("- Local: https://localhost:5000")
    print("- Rede:  https://{seu-ip}:5000\n")
    print_colored("[INFO] Pressione Ctrl+C para encerrar o servidor\n", "blue")
    
    while True:
        try:
            subprocess.run([sys.executable, "app.py"], check=True)
            break
        except subprocess.CalledProcessError:
            print_colored("\n[ERRO] Falha ao iniciar o servidor", "red")
            print("Possíveis causas:")
            print("- Porta 5000 em uso")
            print("- Falta de permissões")
            print("- Erro nas dependências\n")
            
            retry = input("Tentar novamente? (S/N): ").lower()
            if retry != 's':
                break
            print_colored("\n[INFO] Tentando novamente...", "blue")
            time.sleep(2)
        except KeyboardInterrupt:
            print_colored("\n\n[INFO] Servidor encerrado pelo usuário", "blue")
            break

def main():
    """Função principal"""
    print_header()
    
    if not check_python():
        return
    
    setup_files()
    
    if not setup_venv():
        return
    
    if not install_dependencies():
        return
    
    run_server()
    
    print_colored("\n[INFO] Pressione Enter para sair...", "blue")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n[INFO] Programa encerrado pelo usuário", "blue")
    except Exception as e:
        print_colored(f"\n[ERRO] Erro inesperado: {e}", "red")
        print("\nPressione Enter para sair...")
        input() 