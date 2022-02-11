import os, sys, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler

class Server(BaseHTTPRequestHandler):
    # respond to all get requests with the content of this file
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(open("main.py").read().encode("utf8"))

    # treat all post requests as an attempt to patch this server,
    # using the body of the request as the patch
    def do_POST(self):
        try:
            content_len = int(self.headers.get('Content-Length'))
            patch = self.rfile.read(content_len)
            self.try_patch(patch)
        except Exception as e:
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write((str(e)+"\n").encode("utf8"))
            return

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write("OK\n".encode("utf8"))

        # restart server in place after the response is written
        print("Restarting server...")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # applies the patch if it passes verification
    def try_patch(self, patch):
        self.verify(patch)
        self.apply(patch)

    # raises an exception if the patch should not be applied
    def verify(self, patch):
        pass # always accept

    # applies the patch to the source code in this directory
    def apply(self, patch):
        process = subprocess.Popen(["git", "am"], stdin=subprocess.PIPE)
        process.communicate(patch)
        process.wait()
        if process.returncode != 0:
            raise Exception("git am: return code: %i" % (process.returncode, ))

if __name__ == "__main__":
    print("Starting server...")
    HTTPServer(("localhost", 8080), Server).serve_forever()
