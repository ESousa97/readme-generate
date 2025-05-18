# Gerador de README.md Inteligente v1.0.1

Bem-vindo ao Gerador de README.md Inteligente! Esta aplicação desktop foi criada para simplificar a criação de arquivos README.md de alta qualidade para os seus projetos de software. Utilizamos a Inteligência Artificial do Google Gemini para gerar documentação que seja ao mesmo tempo profissional e fácil de entender.

## Sobre a Aplicação

Um bom arquivo README.md é fundamental para qualquer projeto de software. Ele serve como a primeira impressão do seu projeto, fornecendo informações essenciais para quem deseja entender, usar ou contribuir com o seu trabalho. No entanto, criar um README completo e informativo pode ser uma tarefa demorada. Esta ferramenta foi desenvolvida para resolver este problema, automatizando o processo de geração do README:

* **Entrada**: Você fornece um arquivo .zip contendo todos os arquivos e pastas do seu projeto.
* **Análise**: A aplicação analisa a estrutura do seu projeto e o conteúdo dos arquivos relevantes.
* **Processamento**: As informações coletadas são enviadas para a API do Google Gemini.
* **Geração**: A IA do Google Gemini processa os dados e gera um rascunho completo do seu README.md.
* **Saída**: O arquivo README.md é salvo no seu computador, pronto para você revisar, editar e adicionar ao seu projeto.

## Funcionalidades Principais

* **Interface Gráfica Intuitiva**: A aplicação possui uma interface amigável, tornando-a acessível mesmo para usuários sem experiência em desenvolvimento.
* **Geração Inteligente de Documentação**: A API do Google Gemini é utilizada para gerar conteúdo relevante e adequado ao contexto do seu projeto.
* **Análise Detalhada de Projetos**: A aplicação examina a estrutura de pastas e o conteúdo dos arquivos dentro do seu arquivo .zip.
* **Configuração Flexível**: Você pode configurar sua própria API Key do Google Gemini e selecionar o modelo de IA a ser utilizado.
* **Temas Visuais**: A aplicação oferece temas claro e escuro, permitindo que você escolha a opção mais confortável para os seus olhos.
* **Registro de Operações (Log)**: Acompanhe o progresso da geração do README em tempo real através do log de operações.
* **Portátil (com Python)**: A aplicação é executada em sistemas Windows, macOS e Linux, desde que o Python e as dependências estejam instaladas.

## Para Quem é Esta Ferramenta?

Esta ferramenta é útil para:

* **Desenvolvedores Individuais**: Que desejam gerar rapidamente documentação inicial de alta qualidade para projetos pessoais ou open source.
* **Pequenas Equipes de Desenvolvimento**: Que precisam padronizar a documentação inicial de seus projetos.
* **Estudantes de Programação**: Que estão aprendendo sobre boas práticas de documentação e querem uma maneira fácil de começar.
* **Qualquer Pessoa**: Que queira criar um README.md bem escrito sem gastar horas escrevendo tudo do zero.

## Como Usar a Aplicação (Guia Detalhado)

Aqui está um guia passo a passo sobre como usar o Gerador de README.md Inteligente:

### 1. Pré-requisitos

Antes de começar, você precisa ter o seguinte instalado:

* **Python**: A aplicação é escrita em Python, então você precisa tê-lo instalado no seu sistema.
    * Você pode baixar o Python em [python.org](https://www.python.org/downloads/).
    * Recomendamos usar o Python 3.8 ou superior.
* **API Key do Google Gemini**: A aplicação utiliza a API do Google Gemini, que requer uma chave de API.
    * Você pode obter uma API Key gratuitamente no [Google AI Studio](https://aistudio.google.com/app/apikey).
    * Guarde esta chave em um local seguro, pois você precisará dela para configurar a aplicação.

### 2. Instalação

Siga estas etapas para instalar a aplicação:

1.  **Baixe os Arquivos do Projeto**:
    * Você pode baixar os arquivos do projeto como um arquivo .zip ou clonar o repositório (se estiver disponível no GitHub, por exemplo).
2.  **Abra um Terminal ou Prompt de Comando**:
    * No Windows: Pressione a tecla do Windows, digite `cmd` ou `PowerShell` e pressione Enter.
    * No macOS: Abra o aplicativo "Terminal" (você pode encontrá-lo em Aplicativos/Utilitários).
    * No Linux: Abra o seu terminal preferido.
3.  **Navegue até a Pasta do Projeto**:
    * Use o comando `cd` no terminal para ir para a pasta onde você salvou os arquivos do projeto.
        * Por exemplo: `cd C:\Users\SeuNome\Downloads\README-GENERATE`
4.  **Instale as Dependências**:
    * No terminal, execute o seguinte comando:
        ```bash
        pip install -r requirements.txt
        ```
    * Este comando instala todas as bibliotecas Python necessárias para a aplicação funcionar.
    * Se você não tiver o `pip` instalado, verifique se ele está incluído na sua instalação do Python ou consulte a documentação do Python para instalá-lo.

### 3. Executando a Aplicação

1.  **Abra o Terminal**: Se você fechou o terminal, abra-o novamente e navegue até a pasta do projeto (como explicado na seção anterior).
2.  **Execute o Script**: No terminal, execute o seguinte comando:
    ```bash
    python run_app.py
    ```
3.  **A Aplicação Inicia**: A janela principal do "Gerador de README.md Inteligente" será exibida.

### 4. Configurando a API Key do Google Gemini

1.  **Abra as Configurações**: Na aplicação, vá para `Arquivo` > `Configurar API Key...`.
2.  **Insira a API Key**: Uma pequena janela será aberta.
    * Cole a sua API Key do Google Gemini no campo fornecido.
    * Clique em "OK".
3.  **Verifique a Conexão**: A aplicação tentará se conectar à API do Google Gemini.
    * Você pode verificar o status da conexão na barra inferior da janela da aplicação.

    (Opcional: Adicione uma captura de tela da janela de configuração da API Key)

### 5. Selecionando o Modelo do Gemini (Opcional)

1.  **Abra as Configurações do Modelo**: Por padrão, a aplicação usa o modelo `gemini-1.5-flash-latest`.
2.  **Selecione um Modelo Diferente**: Se você quiser usar um modelo diferente:
    * Vá para `Arquivo` > `Selecionar Modelo Gemini...`.
    * Digite o nome do modelo que você deseja usar (por exemplo, `gemini-1.5-pro-latest`).
    * Clique em "OK".

### 6. Gerando o seu README.md

1.  **Prepare o seu Projeto**:
    * Coloque todos os arquivos e pastas do seu projeto em um único arquivo `.zip`.
    * Por exemplo, se o seu projeto se chama "MeuProjetoIncrivel", você deve criar um arquivo chamado "MeuProjetoIncrivel.zip" contendo tudo.
2.  **Escolha o Diretório de Saída (Opcional)**:
    * Por padrão, o arquivo `README.md` gerado será salvo na sua pasta de usuário.
    * Se você quiser salvar o arquivo em um local diferente:
        * Vá para `Arquivo` > `Selecionar Diretório de Saída...`.
        * Escolha a pasta onde você deseja salvar o arquivo.
3.  **Selecione o Arquivo .zip do Projeto**:
    * Na aplicação, clique no botão **"Selecionar Arquivo .zip do Projeto"**.
    * Navegue até o seu arquivo `.zip` e selecione-o.
    * A aplicação exibirá uma mensagem no "Log de Operações" para confirmar que o arquivo foi selecionado.
4.  **Gere o README.md**:
    * Depois de selecionar o arquivo `.zip` e configurar a API Key, o botão **"Gerar README.md"** será habilitado.
    * Clique neste botão para iniciar o processo de geração.
    * A aplicação irá:
        * Extrair as informações do seu arquivo `.zip`.
        * Enviar essas informações para a API do Google Gemini.
        * Aguardar até que a IA gere o conteúdo do README.
    * Você pode acompanhar o progresso na barra de status na parte inferior da janela e no "Log de Operações".
    * O tempo necessário para gerar o README pode variar dependendo do tamanho do seu projeto e da velocidade da IA.

    (Opcional: Adicione uma captura de tela da aplicação durante o processo de geração do README)

5.  **Arquivo README Gerado**:
    * Quando a geração estiver concluída, a aplicação exibirá uma notificação.
    * O arquivo `README.md` será salvo no diretório de saída que você escolheu (ou no diretório padrão, se você não tiver especificado um).
    * A aplicação tentará abrir a pasta onde o arquivo foi salvo, e também abrir o próprio arquivo `README.md`.
    * **Importante**: Lembre-se que o README gerado pela IA é um **ponto de partida**.
        * É essencial que você revise o conteúdo gerado, adicione detalhes específicos do seu projeto, corrija quaisquer imprecisões e personalize o arquivo para atender às suas necessidades.

### 7. Alterando o Tema da Aplicação (Opcional)

* A aplicação oferece diferentes temas visuais. Para mudar o tema:
    * Vá para o menu `Visual`.
    * Escolha entre "Tema Claro", "Tema Escuro" ou "Padrão do Sistema".

## Entendendo a Interface da Aplicação

Aqui está uma breve descrição dos principais elementos da interface da aplicação:

* **Barra de Menu**:
    * `Arquivo`: Este menu contém opções para:
        * `Configurar API Key...`: Inserir ou alterar a sua API Key do Google Gemini.
        * `Selecionar Modelo Gemini...`: Escolher qual modelo de IA Gemini usar.
        * `Selecionar Diretório de Saída...`: Escolher onde o arquivo README.md será salvo.
        * `Sair`: Fechar a aplicação.
    * `Visual`: Este menu permite que você altere o tema visual da aplicação.
* **Botão "Selecionar Arquivo .zip do Projeto"**: Clique neste botão para selecionar o arquivo .zip que contém os arquivos do seu projeto.
* **Botão "Gerar README.md"**: Este botão inicia o processo de geração do arquivo README.md. Ele só estará habilitado depois que você selecionar um arquivo .zip e configurar a API Key.
* **Log de Operações**: Esta área da janela exibe mensagens sobre as ações que a aplicação está realizando.
    * Por exemplo, você verá mensagens quando um arquivo .zip é selecionado, quando a aplicação se conecta à IA e quando o README é gerado.
* **Barra de Status**: Localizada na parte inferior da janela, a barra de status exibe mensagens rápidas sobre o estado da aplicação e mostra o progresso de operações demoradas.

## Dicas para Obter um Melhor README

Para obter um README.md gerado da melhor forma possível, considere as seguintes dicas:

* **Organize o seu Projeto**: Uma estrutura de pastas clara e nomes de arquivos descritivos ajudam a IA a entender o seu projeto com mais facilidade.
* **Inclua Arquivos de Configuração**: Se o seu projeto utiliza arquivos como `requirements.txt` (Python), `package.json` (Node.js) ou `Dockerfile`, inclua-os no arquivo `.zip`.
    * A IA pode usar essas informações para sugerir seções relevantes sobre instalação e configuração.
* **Comente o seu Código**: Inclua comentários no seu código, especialmente em funções e classes.
    * Em Python, use docstrings para documentar suas funções. Quanto mais informações a IA tiver sobre o seu código, melhor será o README gerado.
* **Personalize o Prompt (Avançado)**: Se você tiver conhecimento em Python, pode modificar o prompt usado para gerar o README.
    * O prompt padrão está localizado no arquivo `gerador_readme_ia/constants.py` na variável `PROMPT_README_GENERATION`.
    * Você pode adicionar instruções mais específicas ao prompt para direcionar a IA de acordo com as suas necessidades.

## Estrutura do Código da Aplicação (Para Desenvolvedores)

```plaintext
README-GENERATE/
├── gerador_readme_ia/        # Pacote principal da aplicação
│   ├── init.py
│   ├── config_manager.py      # Gerencia a API Key e o modelo do Gemini
│   ├── constants.py          # Define constantes globais e o prompt principal da IA
│   ├── logger_setup.py       # Configura o sistema de logging da aplicação
│   ├── gui/
│   │   ├── init.py
│   │   └── app_gui.py       # Contém a lógica e a interface gráfica da aplicação (PyQt5)
│   ├── ia_client/
│   │   ├── init.py
│   │   └── gemini_client.py   # Implementa a interação com a API do Google Gemini
│   └── utils/
│       ├── init.py
│       └── file_helper.py       # Funções utilitárias para manipulação de arquivos
├── run_app.py                # Script para iniciar a aplicação
└── requirements.txt            # Lista as dependências do projeto (bibliotecas Python)
```

## Como Contribuir

Contribuições são sempre bem-vindas! Se você tiver ideias de melhorias, encontrar algum bug ou quiser adicionar novas funcionalidades, siga estas etapas:

1.  **Faça um Fork do Projeto**: Crie uma cópia do projeto na sua própria conta do GitHub (ou plataforma similar).
2.  **Crie uma Branch**: Crie uma nova branch para as suas alterações:
    * `git checkout -b feature/sua-funcionalidade`
3.  **Faça as Alterações**: Implemente as suas melhorias ou correções.
4.  **Faça Commit**: Salve as suas alterações com uma mensagem descritiva:
    * `git commit -am 'Adiciona nova funcionalidade'`
5.  **Envie para o Repositório**: Envie as suas alterações para a sua branch no seu fork:
    * `git push origin feature/sua-funcionalidade`
6.  **Crie um Pull Request**: Envie um Pull Request para que as suas alterações sejam revisadas e incorporadas ao projeto principal.

## Autores

* Enoque Sousa - [LinkedIn](https://www.linkedin.com/in/enoque-sousa-bb89aa168/)

## Agradecimentos

* À equipe do Google pelo desenvolvimento da API Gemini.
* À comunidade PyQt e aos desenvolvedores das bibliotecas de código aberto utilizadas neste projeto.
* À Equipe da Alura por proporcionar um curso tão importante.

## Obtendo sua Chave de API do Google Gemini

Para obter uma chave de API do Google Gemini, siga estes passos:

1.  **Acesse o Google AI Studio**:
    * Vá para o site do Google AI Studio: [https://aistudio.google.com/](https://aistudio.google.com/)
2.  **Faça login na sua Conta Google**:
    * Se ainda não estiver logado, faça login com a sua Conta Google.
3.  **Obtenha a Chave de API**:
    * No Google AI Studio, procure a opção para obter uma chave de API. O local exato pode mudar ligeiramente com as atualizações da interface, mas geralmente há um botão ou link claro para isso.
    * Você pode encontrar um botão como "Obter chave de API" ou algo semelhante.
4.  **Aceite os Termos de Serviço**:
    * Leia e aceite os Termos de Serviço da API do Google e os Termos de Serviço Adicionais da API Gemini.
5.  **Crie a sua Chave de API**:
    * Clique na opção para criar uma nova chave de API.
    * O Google AI Studio irá gerar uma chave de API para você.
6.  **Copie e Guarde a sua Chave de API**:
    * Copie a chave de API e guarde-a num local seguro. Você precisará desta chave para usar a API do Google Gemini no seu código.
7.  **Informações Importantes**:
    * **Segurança**: Mantenha a sua chave de API em segurança e não a partilhe publicamente. Se alguém obtiver acesso à sua chave de API, poderá usar a sua quota da API e possivelmente incorrer em custos.
    * **Faturação**: Se a sua utilização da API exceder o nível de utilização gratuito, poderá incorrer em custos. Consulte a documentação de preços da API Google Gemini para obter mais detalhes.
    * Se tiver alguma dificuldade, a documentação oficial do Google AI Studio e da API Gemini é o melhor recurso para obter informações mais detalhadas e atualizadas.
