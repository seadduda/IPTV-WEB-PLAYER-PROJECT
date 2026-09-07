from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urljoin, urlparse
from urllib.request import HTTPError, Request, build_opener, HTTPRedirectHandler


class LocalPlayerHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        request_url = urlparse(self.path)
        if request_url.path != '/proxy':
            return super().do_GET()

        target_url = parse_qs(request_url.query).get('url', [''])[0]
        if urlparse(target_url).scheme not in ('http', 'https'):
            self.send_error(400, 'A valid HTTP or HTTPS stream URL is required.')
            return

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            range_header = self.headers.get('Range')
            if range_header:
                headers['Range'] = range_header

            request = Request(target_url, headers=headers)
            opener = build_opener(HTTPRedirectHandler())
            response = None
            for attempt in range(3):
                try:
                    response = opener.open(request, timeout=15)
                    break
                except HTTPError as error:
                    if error.code < 500 or attempt == 2:
                        raise

            if response is None:
                raise RuntimeError('The provider did not return a response.')
            content_type = response.headers.get('Content-Type', 'video/mp2t')
            target_path = urlparse(response.geturl()).path.lower()
            # Only trust the extension when the provider didn't already send a real video/* type,
            # otherwise an HTML error page would be mislabeled as playable video.
            if content_type.lower().startswith('text/html'):
                pass
            elif target_path.endswith('.mp4'):
                content_type = 'video/mp4'
            elif target_path.endswith('.webm'):
                content_type = 'video/webm'
            elif target_path.endswith('.ogg'):
                content_type = 'video/ogg'
            elif target_path.endswith('.mkv'):
                content_type = 'video/x-matroska'
            is_manifest = 'mpegurl' in content_type.lower() or urlparse(response.geturl()).path.lower().endswith('.m3u8')
            if is_manifest:
                manifest = response.read().decode('utf-8', errors='replace')
                manifest_base = response.geturl()
                rewritten_lines = []
                for line in manifest.splitlines():
                    stripped_line = line.strip()
                    if stripped_line and not stripped_line.startswith('#'):
                        segment_url = urljoin(manifest_base, stripped_line)
                        line = f"/proxy?url={quote(segment_url, safe='')}"
                    rewritten_lines.append(line)
                manifest = '\n'.join(rewritten_lines) + '\n'
                manifest_bytes = manifest.encode('utf-8')
                self.send_response(response.status)
                self.send_header('Content-Type', 'application/vnd.apple.mpegurl')
                self.send_header('Content-Length', str(len(manifest_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache, no-store')
                self.end_headers()
                self.wfile.write(manifest_bytes)
                return

            self.send_response(response.status)
            self.send_header('Content-Type', content_type)
            self.send_header('Accept-Ranges', 'bytes')
            content_length = response.headers.get('Content-Length')
            if content_length:
                self.send_header('Content-Length', content_length)
            content_range = response.headers.get('Content-Range')
            if content_range:
                self.send_header('Content-Range', content_range)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store')
            self.send_header('Connection', 'close')
            self.end_headers()

            while True:
                chunk = response.read(64 * 1024)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return
        except Exception as error:
            if not self.wfile.closed:
                self.send_error(502, f'Upstream stream error: {error}')


if __name__ == '__main__':
    ThreadingHTTPServer(('localhost', 8000), LocalPlayerHandler).serve_forever()
