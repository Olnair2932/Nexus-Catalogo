from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
import os

BASE = Path(__file__).resolve().parent
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8090"))


class CatalogoHandler(SimpleHTTPRequestHandler):

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
