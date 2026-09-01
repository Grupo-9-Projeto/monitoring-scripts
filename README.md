# 🖥️ Hardware Monitor CLI

Um monitor de hardware em tempo real leve e eficiente para terminal, desenvolvido em Python utilizando a biblioteca `psutil`.

---

## 🚀 Funcionalidades

* **Monitoramento de CPU:** Uso percentual por núcleo e frequência atual.
* **Consumo de Memória:** Gráfico simples de uso da RAM e Swap.
* **Status do Disco:** Espaço livre, utilizado e taxa de leitura/escrita.
* **Rede:** Monitoramento de upload e download em tempo real.
* **Alertas:** Avisos visuais quando o uso de componentes passa de 80%.

---

## 📦 Pré-requisitos

Antes de começar, você precisa ter instalado em sua máquina:
* **Python 3.8** ou superior
* **PIP** (Gerenciador de pacotes do Python)

---

## 🛠️ Instalação e Execução

Siga os passos abaixo para rodar o projeto localmente:

### 1. Clonar o repositório
```bash
git clone https://github.com
cd hardware-monitor-psutil
```

### 2. Criar e ativar um ambiente virtual (Opcional, mas recomendado)
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Executar a aplicação
```bash
python main.py
```

---

## 🛠️ Tecnologias Utilizadas

* [Python](https://python.org) - Linguagem base do projeto.
* [psutil](https://github.com) - Biblioteca para recuperação de informações do sistema.

---

## 🤝 Como Contribuir

1. Faça um **Fork** do projeto.
2. Crie uma nova **Branch** com sua modificação (`git checkout -b feature/NovaFeature`).
3. Faça o **Commit** das suas alterações (`git commit -m 'Adiciona nova funcionalidade'`).
4. Envie para o repositório remoto (`git push origin feature/NovaFeature`).
5. Abra um **Pull Request**.

---

## 📝 Licença

Este projeto está sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---
Desenvolvido com ☕ por [Seu Nome](https://github.com)
