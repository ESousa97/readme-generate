# gerador_readme_ia/constants.py

APP_NAME = "GeradorREADME"
APP_AUTHOR = "SousaInfotec" # Mantendo o que você usou no log
APP_VERSION = "1.0.1" # Defina a versão aqui

DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
CONFIG_FILE_NAME = "settings_readme_generator.ini"
CONFIG_SECTION_API = "API_Gemini"
CONFIG_KEY_API_KEY = "google_api_key"
CONFIG_KEY_MODEL = "gemini_model"

# Novo Prompt para Geração de README.md
PROMPT_README_GENERATION = """
Você é um especialista em documentação de projetos de software e um desenvolvedor experiente.
Com base na seguinte estrutura de pastas e conteúdo de arquivos de um projeto fornecido em um arquivo .zip, gere um arquivo README.md profissional, didático e bem estruturado.

O README.md deve ser abrangente e útil para desenvolvedores e usuários. Inclua, mas não se limite aos seguintes tópicos, quando aplicável e inferível a partir dos dados fornecidos:

1.  **Título do Projeto:** Um título claro e conciso. Se possível, infira do nome da pasta raiz do zip ou de arquivos de configuração principais.
2.  **Descrição Curta:** Um parágrafo resumindo o propósito e a funcionalidade principal do projeto.
3.  **Status do Projeto:** (Opcional, se puder inferir, por exemplo, "Em Desenvolvimento", "Beta", "Estável").
4.  **Badges:** (Opcional, sugira badges comuns como build status, coverage, license, etc. Use placeholders como `[![Build Status](URL_PLACEHOLDER)](URL_PLACEHOLDER)`).
5.  **Tecnologias Utilizadas:** Liste as principais linguagens, frameworks, bibliotecas e ferramentas. Infira dos tipos de arquivo (ex: `.py`, `.js`, `.java`), arquivos de dependência (`requirements.txt`, `package.json`, `pom.xml`, `build.gradle`), e conteúdo do código.
6.  **Funcionalidades Principais:** Uma lista das características mais importantes do projeto.
7.  **Estrutura do Projeto:** Uma visão geral da organização das pastas e arquivos mais importantes.
    Exemplo:
    ```
    nome-do-projeto/
    ├── src/                # Código fonte principal
    │   ├── module1/
    │   └── main.py
    ├── tests/              # Testes unitários e de integração
    ├── docs/               # Documentação adicional
    ├── requirements.txt    # Dependências Python
    └── README.md
    ```
8.  **Pré-requisitos:** Softwares ou ferramentas que precisam estar instalados antes de usar o projeto.
9.  **Instalação:** Passos detalhados para configurar o ambiente de desenvolvimento e instalar as dependências. Se encontrar `requirements.txt`, `setup.py`, `package.json`, etc., sugira os comandos apropriados (ex: `pip install -r requirements.txt`).
10. **Uso/Como Executar:** Instruções sobre como iniciar e usar o projeto. Se houver um arquivo principal como `main.py` ou scripts em `package.json`, sugira como executá-los.
11. **Exemplos de Código:** (Opcional, se trechos de código relevantes forem identificados e puderem ilustrar o uso).
12. **Configuração:** Como configurar o projeto, incluindo variáveis de ambiente ou arquivos de configuração.
13. **Testes:** Como executar os testes (se houver uma pasta `tests` ou arquivos de teste).
14. **Como Contribuir:** Um guia para potenciais contribuidores (pode ser um texto padrão se não houver `CONTRIBUTING.md`).
15. **Licença:** Mencione a licença do projeto. Se um arquivo `LICENSE` ou `LICENSE.md` for encontrado, indique seu tipo (ex: MIT, GPL). Caso contrário, sugira adicionar uma.
16. **Autores e Agradecimentos:** (Opcional)
17. **Contato:** (Opcional)

Formate todo o conteúdo utilizando Markdown. Seja claro e objetivo.
Use blocos de código para comandos, estrutura de pastas e exemplos de código.

**Dados do Projeto (extraídos do arquivo .zip):**

{project_data}

Por favor, gere apenas o conteúdo do arquivo README.md.
Não inclua nenhuma introdução ou conclusão sua antes ou depois do conteúdo do README.
"""