"""Optional GUI (opens in your web browser): pick a task, press Run, see the output.
It just runs the three task scripts and shows what they print.
Only the Python standard library is used. Stop it with Ctrl+C."""
import os
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8000

# Task name shown in the dropdown -> script to run
TASKS = {
    "Word Count": "word-count/word_count.py",
    "Top-K Words": "top-k-words/top_k.py",
    "Inverted Index": "inverted-index/inverted_index.py",
}

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>MapReduce Tasks</title></head>
<body style="font-family: sans-serif; max-width: 800px; margin: 20px auto;">
<h2>MapReduce Tasks</h2>
Task: <select id="task">%s</select>
K (Top-K only): <input id="k" value="10" size="3">
<button onclick="run()">Run</button>
<pre id="out" style="border:1px solid #888; padding:8px; height:450px; overflow:auto;"></pre>
<script>
async function run() {
  const url = "/run?task=" + encodeURIComponent(document.getElementById("task").value)
            + "&k=" + encodeURIComponent(document.getElementById("k").value);
  document.getElementById("out").textContent = await (await fetch(url)).text();
}
</script></body></html>""" % "".join(f"<option>{name}</option>" for name in TASKS)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/run":
            query = parse_qs(url.query)
            name = query["task"][0]
            command = [sys.executable, os.path.join(ROOT, TASKS[name])]
            if name == "Top-K Words":
                command.append(query["k"][0])  # K is passed as the argument
            result = subprocess.run(command, capture_output=True, text=True)
            body = result.stdout + "\n--- threads (stderr) ---\n" + result.stderr
        else:
            body = PAGE
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8" if url.path != "/run" else "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, *args):  # keep the terminal quiet
        pass


print(f"Open http://localhost:{PORT} (Ctrl+C to stop)")
webbrowser.open(f"http://localhost:{PORT}")
HTTPServer(("localhost", PORT), Handler).serve_forever()
