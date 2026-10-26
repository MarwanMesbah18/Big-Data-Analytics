"""Optional GUI (opens in your web browser): pick a task, press Run, see the output.
It just runs the three task scripts and shows what they print.
You can also paste your own text (custom data) instead of the sample files.
Only the Python standard library is used. Stop it with Ctrl+C."""
import os
import subprocess
import sys
import tempfile
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

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
<p>Custom data (optional). Leave empty to use the 5 sample files.
Put a line with <code>---</code> between documents to make several files.<br>
<textarea id="text" rows="6" style="width:100%%"></textarea></p>
<pre id="out" style="border:1px solid #888; padding:8px; height:400px; overflow:auto;"></pre>
<script>
async function run() {
  const body = new URLSearchParams({
    task: document.getElementById("task").value,
    k: document.getElementById("k").value,
    text: document.getElementById("text").value,
  });
  document.getElementById("out").textContent = await (await fetch("/run", {method: "POST", body})).text();
}
// Enter = Run (inside the custom data box, Enter makes a new line; use Ctrl+Enter there)
document.addEventListener("keydown", (e) => {
  const inTextBox = e.target.id === "text";
  if (e.key === "Enter" && (!inTextBox || e.ctrlKey || e.metaKey)) run();
});
</script></body></html>""" % "".join(f"<option>{name}</option>" for name in TASKS)


def run_script(name, k, text):
    """Run one task script and return what it printed."""
    command = [sys.executable, os.path.join(ROOT, TASKS[name])]
    if name == "Top-K Words":
        command.append(k)  # K is passed as the argument
    env = dict(os.environ)
    with tempfile.TemporaryDirectory() as folder:
        if text.strip():
            # Custom data: write each document to its own book_N.txt in a temporary folder
            for i, document in enumerate(text.replace("\r", "").split("\n---\n"), start=1):
                with open(os.path.join(folder, f"book_{i}.txt"), "w") as f:
                    f.write(document)
            env["DATA_DIR"] = folder  # the scripts read their data from here
        result = subprocess.run(command, capture_output=True, text=True, env=env)
    return result.stdout + "\n--- threads (stderr) ---\n" + result.stderr


class Handler(BaseHTTPRequestHandler):
    def reply(self, body, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):  # the page
        self.reply(PAGE, "text/html")

    def do_POST(self):  # Run button
        size = int(self.headers["Content-Length"])
        form = parse_qs(self.rfile.read(size).decode())
        field = lambda name: form.get(name, [""])[0]
        self.reply(run_script(field("task"), field("k"), field("text")), "text/plain")

    def log_message(self, *args):  # keep the terminal quiet
        pass


print(f"Open http://localhost:{PORT} (Ctrl+C to stop)")
webbrowser.open(f"http://localhost:{PORT}")
HTTPServer(("localhost", PORT), Handler).serve_forever()
