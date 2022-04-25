from functools import partial
import http.server
import socketserver
import os , re, ssl, socket 


'''
openssl req -new -x509 -keyout localhost.pem -out localhost.pem -days 365 -nodes

openssl req -new -x509 -keyout localhost.pem -out localhost.pem -days 365 -nodes


'''


PORT = 7113
DIRECTORY = "geodraw_tileset/"
# DIRECTORY = '../LSOA/'

info = os.popen('lsof -i :{PORT}'.format(PORT=PORT)).read()
if info:
    pid = int(re.split('\s+', info)[10])
    stat = os.popen('kill -9 {pid}'.format(pid=pid)).read()

# class Handler(http.server.SimpleHTTPRequestHandler):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, directory=DIRECTORY, **kwargs)

# Handler = partial(http.server.SimpleHTTPRequestHandler, directory=DIRECTORY)

# Handler = http.server.SimpleHTTPRequestHandler

# CORS
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def send_head(self):
        """Common code for GET and HEAD commands.
        This sends the response code and MIME headers.
        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File (really) not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        return f



def serve():
    with socketserver.ThreadingTCPServer(("localhost", PORT), Handler) as httpd:
        httpd.allow_reuse_address = True
        print(f"serving {DIRECTORY}  @ port {PORT}")
        print(f'http://localhost:{PORT}/')


        # httpd.socket = ssl.wrap_socket(httpd.socket,
        #                        server_side=True,
        #                        keyfile='localhost.pem',
        #                        certfile='localhost.pem')


        httpd.serve_forever()


if __name__ == "__main__": 
    try:serve()
    except KeyboardInterrupt:pass
    except: 
        print('----  retrying  ----')
        import time
        time.sleep(10)
        serve()