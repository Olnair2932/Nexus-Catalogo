from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
import os
import uuid
import base64
import urllib.parse
import urllib.request
from email.parser import BytesParser
from email.policy import default
import firebase_admin
from firebase_admin import credentials, db, auth

BASE = Path(__file__).resolve().parent
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8090"))


FIREBASE_SERVICE_ACCOUNT_JSON = os.environ.get(
    "FIREBASE_SERVICE_ACCOUNT_JSON"
)

if FIREBASE_SERVICE_ACCOUNT_JSON:
    cred = credentials.Certificate(
        json.loads(FIREBASE_SERVICE_ACCOUNT_JSON)
    )

    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": "https://ia-termux-default-rtdb.firebaseio.com"
        }
    )


def enviar_imagem_cloudinary(nome_arquivo, conteudo):
    cloudinary_url = os.environ.get("CLOUDINARY_URL")

    if not cloudinary_url:
        raise RuntimeError("CLOUDINARY_URL não configurada")

    dados_url = cloudinary_url.replace(
        "cloudinary://",
        "",
        1
    )

    credenciais, cloud_name = dados_url.split("@", 1)
    api_key, api_secret = credenciais.split(":", 1)

    timestamp = str(int(__import__("time").time()))

    assinatura_base = (
        f"timestamp={timestamp}{api_secret}"
    )

    import hashlib

    assinatura = hashlib.sha1(
        assinatura_base.encode("utf-8")
    ).hexdigest()

    endpoint = (
        f"https://api.cloudinary.com/v1_1/"
        f"{cloud_name}/image/upload"
    )

    extensao = Path(nome_arquivo).suffix.lower()

    tipos = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }

    tipo_mime = tipos.get(
        extensao,
        "application/octet-stream"
    )

    formulario = {
        "file": (
            f"data:{tipo_mime};base64,"
            + base64.b64encode(conteudo).decode("ascii")
        ),
        "api_key": api_key,
        "timestamp": timestamp,
        "signature": assinatura,
    }

    corpo = urllib.parse.urlencode(formulario).encode("utf-8")

    requisicao = urllib.request.Request(
        endpoint,
        data=corpo,
        method="POST"
    )

    with urllib.request.urlopen(requisicao, timeout=60) as resposta:
        resultado = json.loads(
            resposta.read().decode("utf-8")
        )

    return resultado["secure_url"]


def enviar_video_cloudinary(nome_arquivo, conteudo):
    cloudinary_url = os.environ.get("CLOUDINARY_URL")

    if not cloudinary_url:
        raise RuntimeError("CLOUDINARY_URL não configurada")

    dados_url = cloudinary_url.replace(
        "cloudinary://",
        "",
        1
    )

    credenciais, cloud_name = dados_url.split("@", 1)
    api_key, api_secret = credenciais.split(":", 1)

    timestamp = str(int(__import__("time").time()))

    assinatura_base = (
        f"timestamp={timestamp}{api_secret}"
    )

    import hashlib

    assinatura = hashlib.sha1(
        assinatura_base.encode("utf-8")
    ).hexdigest()

    endpoint = (
        f"https://api.cloudinary.com/v1_1/"
        f"{cloud_name}/video/upload"
    )

    extensao = Path(nome_arquivo).suffix.lower()

    tipos = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mov": "video/quicktime",
        ".m4v": "video/x-m4v",
        ".avi": "video/x-msvideo",
    }

    tipo_mime = tipos.get(
        extensao,
        "application/octet-stream"
    )

    formulario = {
        "file": (
            f"data:{tipo_mime};base64,"
            + base64.b64encode(conteudo).decode("ascii")
        ),
        "api_key": api_key,
        "timestamp": timestamp,
        "signature": assinatura,
    }

    corpo = urllib.parse.urlencode(formulario).encode("utf-8")

    requisicao = urllib.request.Request(
        endpoint,
        data=corpo,
        method="POST"
    )

    with urllib.request.urlopen(requisicao, timeout=120) as resposta:
        resultado = json.loads(
            resposta.read().decode("utf-8")
        )

    return resultado["secure_url"]


class CatalogoHandler(SimpleHTTPRequestHandler):

    def autenticar_usuario(self):
        if not FIREBASE_SERVICE_ACCOUNT_JSON:
            return None

        cabecalho = self.headers.get("Authorization", "")
        if not cabecalho.startswith("Bearer "):
            self.send_error(401, "Autenticação necessária")
            return None

        token = cabecalho[7:].strip()

        if not token:
            self.send_error(401, "Token de autenticação ausente")
            return None

        try:
            token_verificado = auth.verify_id_token(token)
            return token_verificado.get("uid")
        except Exception:
            self.send_error(401, "Token de autenticação inválido")
            return None

    def do_POST(self):

        if self.path == "/api/comentarios":
            self._rota_comentarios_post()
            return

        if self.path == "/api/upload-imagem":
            content_type = self.headers.get("Content-Type", "")

            if "multipart/form-data" not in content_type:
                self.send_error(
                    400,
                    "Upload deve usar multipart/form-data"
                )
                return

            tamanho = int(
                self.headers.get("Content-Length", "0")
            )

            corpo = self.rfile.read(tamanho)

            try:
                mensagem = BytesParser(
                    policy=default
                ).parsebytes(
                    (
                        f"Content-Type: {content_type}\r\n"
                        f"MIME-Version: 1.0\r\n\r\n"
                    ).encode("utf-8") + corpo
                )

                arquivo = None

                for parte in mensagem.iter_parts():
                    if parte.get_filename():
                        arquivo = parte
                        break

                if arquivo is None:
                    self.send_error(
                        400,
                        "Nenhuma imagem enviada"
                    )
                    return

                conteudo = arquivo.get_payload(
                    decode=True
                )

                if not conteudo:
                    self.send_error(
                        400,
                        "Imagem vazia"
                    )
                    return

                url = enviar_imagem_cloudinary(
                    arquivo.get_filename(),
                    conteudo
                )

            except Exception as erro:
                self.send_error(
                    500,
                    f"Erro no upload da imagem: {erro}"
                )
                return

            resposta = json.dumps(
                {
                    "ok": True,
                    "url": url
                },
                ensure_ascii=False
            ).encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.send_header(
                "Content-Length",
                str(len(resposta))
            )
            self.end_headers()
            self.wfile.write(resposta)
            return

        if self.path == "/api/upload-video":
            content_type = self.headers.get("Content-Type", "")

            if "multipart/form-data" not in content_type:
                self.send_error(
                    400,
                    "Upload deve usar multipart/form-data"
                )
                return

            tamanho = int(
                self.headers.get("Content-Length", "0")
            )

            corpo = self.rfile.read(tamanho)

            try:
                mensagem = BytesParser(
                    policy=default
                ).parsebytes(
                    (
                        f"Content-Type: {content_type}\r\n"
                        f"MIME-Version: 1.0\r\n\r\n"
                    ).encode("utf-8") + corpo
                )

                arquivo = None

                for parte in mensagem.iter_parts():
                    if parte.get_filename():
                        arquivo = parte
                        break

                if arquivo is None:
                    self.send_error(
                        400,
                        "Nenhum vídeo enviado"
                    )
                    return

                conteudo = arquivo.get_payload(
                    decode=True
                )

                if not conteudo:
                    self.send_error(
                        400,
                        "Vídeo vazio"
                    )
                    return

                url = enviar_video_cloudinary(
                    arquivo.get_filename(),
                    conteudo
                )

            except Exception as erro:
                self.send_error(
                    500,
                    f"Erro no upload do vídeo: {erro}"
                )
                return

            resposta = json.dumps(
                {
                    "ok": True,
                    "url": url
                },
                ensure_ascii=False
            ).encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.send_header(
                "Content-Length",
                str(len(resposta))
            )
            self.end_headers()
            self.wfile.write(resposta)
            return

        if self.path != "/api/anuncios":
            self.send_error(404, "Rota não encontrada")
            return

        uid_usuario = self.autenticar_usuario()
        if FIREBASE_SERVICE_ACCOUNT_JSON and not uid_usuario:
            return

        tamanho = int(self.headers.get("Content-Length", "0"))
        corpo = self.rfile.read(tamanho)

        try:
            dados = json.loads(corpo.decode("utf-8"))
        except Exception:
            self.send_error(400, "JSON inválido")
            return

        if not isinstance(dados, dict):
            self.send_error(400, "Dados inválidos")
            return

        nome = str(dados.get("nome", "")).strip()

        if not nome:
            self.send_error(400, "Nome do produto é obrigatório")
            return

        anuncio_id = uuid.uuid4().hex[:8]

        template = BASE / "templates" / "anuncio_padrao.html"
        pasta_anuncio = BASE / "anuncios" / anuncio_id
        pagina = pasta_anuncio / "index.html"

        try:
            html = template.read_text(encoding="utf-8")

            produto = nome
            preco = str(dados.get("preco", "")).strip()
            codigo = str(dados.get("codigo", "")).strip()

            if not codigo:
                codigo = f"ANUNCIO-{anuncio_id.upper()}"

            descricao = str(dados.get("descricao", "")).strip()
            contato = str(dados.get("contato", "")).strip()
            fotos = str(dados.get("fotos", "")).strip()
            video = str(dados.get("video", "")).strip()

            lista_fotos = [
                foto.strip()
                for foto in fotos.split(",")
                if foto.strip()
            ]

            if lista_fotos:
                foto_principal = lista_fotos[0]

                html = html.replace(
                    "https://via.placeholder.com/600x400",
                    foto_principal,
                    1
                )

                for foto in lista_fotos[:4]:
                    html = html.replace(
                        "https://via.placeholder.com/100",
                        foto,
                        1
                    )

            condicao = str(dados.get("condicao", "")).strip()
            vendedor = str(dados.get("vendedor", "")).strip()
            endereco = str(dados.get("endereco", "")).strip()
            taxa = str(dados.get("taxa", "")).strip()
            pagamento = str(dados.get("pagamento", "")).strip()

            html = html.replace(
                "{{NOME_ANUNCIO}}",
                produto
            )
            html = html.replace(
                "{{PRECO_ANUNCIO}}",
                preco
            )
            html = html.replace(
                "{{CODIGO_ANUNCIO}}",
                codigo
            )
            html = html.replace(
                "{{CONDICAO_ANUNCIO}}",
                condicao
            )
            html = html.replace(
                "{{DESCRICAO_ANUNCIO}}",
                descricao
            )
            numero_whatsapp = "".join(
                caractere
                for caractere in contato
                if caractere.isdigit()
            )

            if numero_whatsapp.startswith("55"):
                numero_whatsapp = numero_whatsapp[2:]

            numero_whatsapp = "55" + numero_whatsapp

            html = html.replace(
                "{{CONTATO_ANUNCIO}}",
                numero_whatsapp
            )
            html = html.replace(
                "{{VIDEO_ANUNCIO}}",
                video
            )

            html = html.replace(
                '<img src="https://via.placeholder.com/100" alt="Foto">',
                ""
            )

            pasta_anuncio.mkdir(parents=True, exist_ok=False)
            pagina.write_text(html, encoding="utf-8")

            arquivo_dados = BASE / "dados" / "anuncios.json"

            try:
                anuncios = json.loads(
                    arquivo_dados.read_text(encoding="utf-8")
                )
                if not isinstance(anuncios, list):
                    anuncios = []
            except Exception:
                anuncios = []

            registro = {
                "id": anuncio_id,
                "uid": uid_usuario,
                "nome": produto,
                "codigo": codigo,
                "preco": preco,
                "condicao": str(dados.get("condicao", "")).strip(),
                "vendedor": str(dados.get("vendedor", "")).strip(),
                "contato": contato,
                "endereco": str(dados.get("endereco", "")).strip(),
                "taxa": str(dados.get("taxa", "")).strip(),
                "pagamento": str(dados.get("pagamento", "")).strip(),
                "video": str(dados.get("video", "")).strip(),
                "descricao": descricao,
                "fotos": str(dados.get("fotos", "")).strip()
            }

            if FIREBASE_SERVICE_ACCOUNT_JSON:
                referencia = db.reference(
                    "nexus_catalogo/anuncios"
                )
                referencia.child(anuncio_id).set(registro)
            else:
                anuncios.append(registro)

                arquivo_dados.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )
                arquivo_dados.write_text(
                    json.dumps(
                        anuncios,
                        ensure_ascii=False,
                        indent=2
                    ),
                    encoding="utf-8"
                )

        except Exception as erro:
            self.send_error(500, f"Erro ao criar anúncio: {erro}")
            return

        resposta = json.dumps(
            {
                "ok": True,
                "id": anuncio_id,
                "url": f"/anuncios/{anuncio_id}/"
            },
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(201)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(resposta))
        )
        self.end_headers()
        self.wfile.write(resposta)


    def _responder_json(self, dados, status=200):
        resposta = json.dumps(
            dados,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(resposta))
        )
        self.end_headers()
        self.wfile.write(resposta)


    def _ler_corpo_json(self):
        tamanho = int(
            self.headers.get("Content-Length", "0")
        )

        if tamanho <= 0 or tamanho > 10000:
            return None

        corpo = self.rfile.read(tamanho)

        try:
            return json.loads(
                corpo.decode("utf-8")
            )
        except Exception:
            return None


    def _rota_comentarios_post(self):
        dados = self._ler_corpo_json()

        if not isinstance(dados, dict):
            self._responder_json(
                {
                    "ok": False,
                    "erro": "Dados inválidos."
                },
                400
            )
            return

        nome = str(
            dados.get("nome", "")
        ).strip()

        comentario = str(
            dados.get("comentario", "")
        ).strip()

        if not nome:
            self._responder_json(
                {
                    "ok": False,
                    "erro": "Informe seu nome."
                },
                400
            )
            return

        if not comentario:
            self._responder_json(
                {
                    "ok": False,
                    "erro": "Informe seu comentário."
                },
                400
            )
            return

        if len(nome) > 80:
            self._responder_json(
                {
                    "ok": False,
                    "erro": "O nome deve ter no máximo 80 caracteres."
                },
                400
            )
            return

        if len(comentario) > 500:
            self._responder_json(
                {
                    "ok": False,
                    "erro": "O comentário deve ter no máximo 500 caracteres."
                },
                400
            )
            return

        try:
            registro = {
                "nome": nome,
                "comentario": comentario,
                "criado_em": __import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ).isoformat()
            }

            if FIREBASE_SERVICE_ACCOUNT_JSON:
                referencia = db.reference(
                    "nexus_catalogo/comentarios"
                )

                novo = referencia.push(
                    registro
                )

                registro["id"] = novo.key

            else:
                pasta = BASE / "dados"
                arquivo = pasta / "comentarios.json"

                pasta.mkdir(
                    parents=True,
                    exist_ok=True
                )

                try:
                    comentarios = json.loads(
                        arquivo.read_text(
                            encoding="utf-8"
                        )
                    )

                    if not isinstance(comentarios, list):
                        comentarios = []

                except Exception:
                    comentarios = []

                registro["id"] = str(
                    uuid.uuid4()
                )

                comentarios.append(
                    registro
                )

                arquivo.write_text(
                    json.dumps(
                        comentarios,
                        ensure_ascii=False,
                        indent=2
                    ),
                    encoding="utf-8"
                )

        except Exception as erro:
            self._responder_json(
                {
                    "ok": False,
                    "erro": f"Erro ao salvar comentário: {erro}"
                },
                500
            )
            return

        self._responder_json(
            {
                "ok": True,
                "comentario": registro
            },
            201
        )


    def _rota_comentarios_get(self):
        try:
            if FIREBASE_SERVICE_ACCOUNT_JSON:
                dados = db.reference(
                    "nexus_catalogo/comentarios"
                ).get()

                if isinstance(dados, dict):
                    comentarios = []

                    for chave, valor in dados.items():
                        if isinstance(valor, dict):
                            item = dict(valor)
                            item["id"] = chave
                            comentarios.append(item)
                else:
                    comentarios = []

            else:
                arquivo = (
                    BASE
                    / "dados"
                    / "comentarios.json"
                )

                if arquivo.exists():
                    comentarios = json.loads(
                        arquivo.read_text(
                            encoding="utf-8"
                        )
                    )

                    if not isinstance(comentarios, list):
                        comentarios = []
                else:
                    comentarios = []

            comentarios.sort(
                key=lambda item: str(
                    item.get("criado_em", "")
                ),
                reverse=True
            )

        except Exception as erro:
            self._responder_json(
                {
                    "ok": False,
                    "erro": f"Erro ao carregar comentários: {erro}"
                },
                500
            )
            return

        self._responder_json(
            {
                "ok": True,
                "comentarios": comentarios
            }
        )


    def do_DELETE(self):

        prefixo = "/api/anuncios/"

        if not self.path.startswith(prefixo):
            self.send_error(404, "Rota não encontrada")
            return

        anuncio_id = self.path[len(prefixo):].strip("/")

        if not anuncio_id:
            self.send_error(400, "ID do anúncio não informado")
            return

        uid_usuario = self.autenticar_usuario()
        if FIREBASE_SERVICE_ACCOUNT_JSON and not uid_usuario:
            return

        arquivo_dados = BASE / "dados" / "anuncios.json"

        try:
            if FIREBASE_SERVICE_ACCOUNT_JSON:
                referencia = db.reference(
                    "nexus_catalogo/anuncios"
                ).child(anuncio_id)

                anuncio = referencia.get()

                if not isinstance(anuncio, dict):
                    self.send_error(
                        404,
                        "Anúncio não encontrado"
                    )
                    return

                if anuncio.get("uid") != uid_usuario:
                    self.send_error(
                        403,
                        "Você não tem permissão para excluir este anúncio"
                    )
                    return

                referencia.delete()

            else:
                anuncios = json.loads(
                    arquivo_dados.read_text(encoding="utf-8")
                )

                if not isinstance(anuncios, list):
                    anuncios = []

                encontrados = [
                    anuncio for anuncio in anuncios
                    if str(anuncio.get("id", "")) == anuncio_id
                ]

                if not encontrados:
                    self.send_error(
                        404,
                        "Anúncio não encontrado"
                    )
                    return

                anuncio_local = encontrados[0]

                if anuncio_local.get("uid") != uid_usuario:
                    self.send_error(
                        403,
                        "Você não tem permissão para excluir este anúncio"
                    )
                    return

                anuncios = [
                    anuncio for anuncio in anuncios
                    if str(anuncio.get("id", "")) != anuncio_id
                ]

                arquivo_dados.write_text(
                    json.dumps(
                        anuncios,
                        ensure_ascii=False,
                        indent=2
                    ),
                    encoding="utf-8"
                )

        except Exception as erro:
            self.send_error(
                500,
                f"Erro ao excluir anúncio: {erro}"
            )
            return

        pasta_anuncio = BASE / "anuncios" / anuncio_id

        if pasta_anuncio.exists():
            import shutil
            shutil.rmtree(pasta_anuncio)

        resposta = json.dumps(
            {
                "ok": True,
                "mensagem": "Anúncio excluído com sucesso."
            },
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(resposta))
        )
        self.end_headers()
        self.wfile.write(resposta)


    def do_GET(self):

        if self.path == "/api/comentarios":
            self._rota_comentarios_get()
            return

        if self.path.startswith("/anuncios/"):

            caminho = urllib.parse.urlparse(
                self.path
            ).path

            partes = caminho.strip("/").split("/")

            anuncio_id = (
                partes[1]
                if len(partes) == 2
                else ""
            )

            if anuncio_id:

                try:
                    if FIREBASE_SERVICE_ACCOUNT_JSON:
                        anuncio = db.reference(
                            "nexus_catalogo/anuncios"
                        ).child(anuncio_id).get()
                    else:
                        arquivo_dados = BASE / "dados" / "anuncios.json"
                        anuncios = json.loads(
                            arquivo_dados.read_text(
                                encoding="utf-8"
                            )
                        )

                        anuncio = next(
                            (
                                item for item in anuncios
                                if str(item.get("id", "")) == anuncio_id
                            ),
                            None
                        )

                    if not isinstance(anuncio, dict):
                        self.send_error(
                            404,
                            "Anúncio não encontrado"
                        )
                        return

                    template = BASE / "templates" / "anuncio_padrao.html"
                    html = template.read_text(
                        encoding="utf-8"
                    )

                    produto = str(
                        anuncio.get("nome", "")
                    ).strip()

                    preco = str(
                        anuncio.get("preco", "")
                    ).strip()

                    codigo = str(
                        anuncio.get("codigo", "")
                    ).strip()

                    if not codigo:
                        codigo = f"ANUNCIO-{anuncio_id.upper()}"

                    condicao = str(
                        anuncio.get("condicao", "")
                    ).strip()

                    descricao = str(
                        anuncio.get("descricao", "")
                    ).strip()

                    contato = str(
                        anuncio.get("contato", "")
                    ).strip()

                    video = str(
                        anuncio.get("video", "")
                    ).strip()

                    fotos = str(
                        anuncio.get("fotos", "")
                    ).strip()

                    lista_fotos = [
                        foto.strip()
                        for foto in fotos.split(",")
                        if foto.strip()
                    ]

                    if lista_fotos:
                        html = html.replace(
                            "https://via.placeholder.com/600x400",
                            lista_fotos[0],
                            1
                        )

                        for foto in lista_fotos[:4]:
                            html = html.replace(
                                "https://via.placeholder.com/100",
                                foto,
                                1
                            )

                    html = html.replace(
                        "{{NOME_ANUNCIO}}",
                        produto
                    )
                    html = html.replace(
                        "{{PRECO_ANUNCIO}}",
                        preco
                    )
                    html = html.replace(
                        "{{CODIGO_ANUNCIO}}",
                        codigo
                    )
                    html = html.replace(
                        "{{CONDICAO_ANUNCIO}}",
                        condicao
                    )
                    html = html.replace(
                        "{{DESCRICAO_ANUNCIO}}",
                        descricao
                    )
                    numero_whatsapp = "".join(
                        caractere
                        for caractere in contato
                        if caractere.isdigit()
                    )

                    if numero_whatsapp.startswith("55"):
                        numero_whatsapp = numero_whatsapp[2:]

                    numero_whatsapp = "55" + numero_whatsapp

                    html = html.replace(
                        "{{CONTATO_ANUNCIO}}",
                        numero_whatsapp
                    )
                    html = html.replace(
                        "{{VIDEO_ANUNCIO}}",
                        video
                    )

                    html = html.replace(
                        '<img src="https://via.placeholder.com/100" alt="Foto">',
                        ""
                    )

                    corpo = html.encode("utf-8")

                    self.send_response(200)
                    self.send_header(
                        "Content-Type",
                        "text/html; charset=utf-8"
                    )
                    self.send_header(
                        "Content-Length",
                        str(len(corpo))
                    )
                    self.end_headers()
                    self.wfile.write(corpo)
                    return

                except Exception as erro:
                    self.send_error(
                        500,
                        f"Erro ao abrir anúncio: {erro}"
                    )
                    return

        if self.path == "/api/anuncios":
            arquivo = BASE / "dados" / "anuncios.json"

            try:
                if FIREBASE_SERVICE_ACCOUNT_JSON:
                    dados_firebase = db.reference(
                        "nexus_catalogo/anuncios"
                    ).get()

                    if isinstance(dados_firebase, dict):
                        dados = list(dados_firebase.values())
                    else:
                        dados = []
                else:
                    dados = json.loads(
                        arquivo.read_text(encoding="utf-8")
                    )
            except Exception:
                dados = []

            corpo = json.dumps(
                dados,
                ensure_ascii=False
            ).encode("utf-8")

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8"
            )
            self.send_header(
                "Content-Length",
                str(len(corpo))
            )
            self.end_headers()
            self.wfile.write(corpo)
            return

        super().do_GET()


if __name__ == "__main__":

    print("🌐 NEXUS CATÁLOGO")
    print(f"Pasta: {BASE}")
    print(f"Servidor: http://{HOST}:{PORT}")
    print("Catálogo online em construção.")

    servidor = ThreadingHTTPServer(
        (HOST, PORT),
        lambda *args, **kwargs:
            CatalogoHandler(
                *args,
                directory=str(BASE),
                **kwargs
            )
    )

    servidor.serve_forever()
