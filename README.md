🛍️ Nexus Catálogo

Catálogo online de anúncios desenvolvido para publicação, divulgação e gerenciamento de produtos e serviços.

O Nexus Catálogo permite que usuários autenticados criem seus próprios anúncios, visualizem os produtos cadastrados e removam apenas os anúncios que pertencem à própria conta.

✨ Recursos

- 🔐 Login com Google
- 👤 Autenticação anônima inicial
- 🔗 Vinculação da conta anônima com Google
- 🚪 Logout da conta Google
- ➕ Criação de anúncios
- 📋 Listagem de anúncios
- 🗑️ Exclusão dos próprios anúncios
- 🖼️ Cadastro de fotos
- 🎥 Cadastro de vídeo
- 💰 Preço
- 🆕 Produto novo ou usado
- 📞 Contato do vendedor
- 📍 Endereço para retirada
- 🚚 Taxa de entrega
- 💳 Forma de pagamento
- 📱 Carrossel de botões no celular
- 🛍️ Acesso à vitrine pública
- 🔏 Termos, Política de Privacidade e Desenvolvimento
- 🤖 Desenvolvimento com auxílio de ferramentas de Inteligência Artificial
- 🔥 Firebase Realtime Database
- ☁️ Hospedagem no Render

🔏 Termos, Privacidade e Desenvolvimento

O projeto disponibiliza uma página institucional com:

- 📋 Termos e Condições
- 🔐 Política de Privacidade
- 👨‍💻 Informações sobre o desenvolvimento do projeto
- 🤖 Informação sobre o uso de ferramentas de Inteligência Artificial

O Nexus Catálogo foi desenvolvido por Olnair Gonzaga Pereira, com auxílio de ferramentas de Inteligência Artificial.

🔐 Segurança

A autenticação utiliza o Firebase Authentication.

Cada anúncio recebe o "uid" do usuário que o criou.

Quando um usuário tenta excluir um anúncio, o backend verifica se o "uid" do anúncio corresponde ao "uid" autenticado.

Dessa forma:

- cada usuário pode excluir seus próprios anúncios;
- um usuário não pode excluir anúncios de outra conta;
- a identidade do usuário é validada pelo backend.

O Realtime Database utiliza regras de produção que bloqueiam o acesso direto por clientes:

{
  "rules": {
    ".read": false,
    ".write": false
  }
}

As operações do banco são realizadas pelo backend através do Firebase Admin SDK.

👑 Administrador

O administrador atual do sistema é:

"olnairpereira@gmail.com"

A autorização das operações utiliza a identidade autenticada pelo Firebase e o respectivo "uid".

🗄️ Estrutura do Firebase

Os anúncios são armazenados em:

nexus_catalogo/
└── anuncios/
    └── {id_do_anuncio}

Cada anúncio pode conter:

id
uid
nome
codigo
preco
condicao
vendedor
contato
endereco
taxa
pagamento
video
descricao
fotos

🧩 Tecnologias

- Python
- HTML
- CSS
- JavaScript
- Firebase Authentication
- Firebase Realtime Database
- Firebase Admin SDK
- Render
- GitHub

🌐 Produção

Aplicação:

https://nexus-catalogo.onrender.com

Vitrine pública:

https://ia-termux.web.app

Repositório:

https://github.com/Olnair2932/Nexus-Catalogo

⚙️ Execução local

Clone o projeto:

git clone https://github.com/Olnair2932/Nexus-Catalogo.git

Entre na pasta:

cd Nexus-Catalogo

Execute:

python3 app.py

🔑 Credenciais

Informações sensíveis não devem ser armazenadas no GitHub.

Nunca publique:

- Chaves privadas do Firebase
- Service Account JSON
- Senhas
- Tokens
- Segredos de autenticação

As credenciais de produção devem ser configuradas através das variáveis de ambiente do servidor.

📁 Estrutura básica

Nexus-Catalogo/
├── app.py
├── index.html
├── termos.html
├── dados/
├── anuncios/
└── README.md

🛡️ Princípios de segurança

1. A identidade do usuário é validada pelo Firebase Authentication.
2. O backend verifica o token de autenticação.
3. Cada anúncio registra o "uid" do proprietário.
4. A exclusão verifica o proprietário antes de remover o anúncio.
5. O Realtime Database não fica aberto para acesso direto do cliente.
6. Credenciais privadas não devem ser versionadas no GitHub.

📌 Status

Nexus Catálogo — em produção

O projeto continua em desenvolvimento.

---

Nexus

🛍️ Nexus Catálogo
Catálogo online de anúncios.
