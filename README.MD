# 📊 Social Media Views Counter

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Selenium](https://img.shields.io/badge/Selenium-Latest-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Descrição
Sistema automatizado para análise de visualizações em redes sociais, utilizando Selenium para web scraping e gerando relatórios detalhados de YouTube Shorts, TikTok, Instagram Reels e Facebook.

## ✨ Funcionalidades Principais

### 🤖 Coleta Automatizada
- Extração de dados em tempo real
- Sistema de cache inteligente
- Validação automática de dados
- Sistema multi-threading para coletas paralelas

### 🌐 Plataformas Suportadas
- YouTube Shorts
- TikTok
- Instagram Reels
- Facebook Videos

### 📊 Relatórios e Análises
- Exportação em HTML interativo
- Planilhas Excel detalhadas
- Gráficos de desempenho
- Métricas comparativas

### 🔍 Monitoramento
- Sistema de logs em tempo real
- Alertas de erros via email
- Dashboard de status
- Histórico de execuções

## 🛠️ Requisitos
- Python 3.x
- Selenium
- undetected-chromedriver
- pandas
- requests
- tiktok-captcha-solver

## 📁 Estrutura do Projeto
```
counter/
├── database/
│   ├── cookies/
│   │   ├── facebook.json
│   │   ├── instagram.json
│   │   └── tiktok.json
│   ├── logs/
│   ├── results/
│   └── users/
│       ├── usersYt.txt
│       ├── usersTtk.txt
│       ├── usersIg.txt
│       └── usersFace.txt
├── scraping/
│   ├── youtube.py
│   ├── tiktok.py
│   ├── instagram.py
│   └── facebook.py
└── ranking.py
```

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/social-media-counter.git
cd social-media-counter
```

2. Instale as dependências:
```bash
pip install selenium undetected-chromedriver pandas requests tiktok-captcha-solver
```

## ⚙️ Configuração

1. Configure os arquivos de cookies nas respectivas pastas
2. Adicione os usernames nos arquivos:
    - `usersYt.txt`
    - `usersTtk.txt`
    - `usersIg.txt`
    - `usersFace.txt`

## 📱 Uso

1. Execute o script da plataforma desejada:
```bash
python scraping/youtube.py
python scraping/tiktok.py
python scraping/instagram.py
python scraping/facebook.py
```

2. Para gerar o ranking final:
```bash
python ranking.py
```

## 🔍 Recursos Avançados
- ⚡ Múltiplas instâncias do Chrome
- 🔄 Sistema de retry para falhas
- 📅 Validação de datas personalizável
- 📊 Relatórios detalhados
- 🔎 Verificação de contas inativas
- 📈 Suporte a diferentes formatos (K, M)

## 🤝 Contribuição
Contribuições são bem-vindas! Abra uma issue ou pull request.

## 📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
