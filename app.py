from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
import os
import uuid

BASE = Path(__file__).resolve().parent
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8090"))


class CatalogoHandler(SimpleHTTPRequestHandler):

    def do_POST(self):

        if self.path != "/api/anuncios":
            self.send_error(404, "Rota não encontrada")
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
            descricao = str(dados.get("descricao", "")).strip()
            contato = str(dados.get("contato", "")).strip()

            html = html.replace(
                "Smartphone Galaxy A54 128 GB",
                produto
            )
            html = html.replace(
                "R$ 1.499,00",
                preco
            )
            html = html.replace(
                "ANUNCIO-0001",
                codigo
            )
            html = html.replace(
                "Galaxy A54 em perfeito estado, 128GB, cor preta, sem marcas de uso.",
                descricao
            )
            html = html.replace(
                "5500000000000",
                contato
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

            anuncios.append(registro)

            arquivo_dados.parent.mkdir(parents=True, exist_ok=True)
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


    def do_GET(self):

        if self.path == "/api/anuncios":
            arquivo = BASE / "dados" / "anuncios.json"

            try:
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
