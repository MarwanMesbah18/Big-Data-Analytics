"""Optional GUI (opens in your web browser): pick a task, press Run, see the output.
It just runs the three task scripts and shows what they print.
You can also paste your own text or upload .txt, .csv and .db (SQLite) files instead of the sample files.
Only the Python standard library is used. Stop it with Ctrl+C."""
import base64
import csv
import io
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

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
<textarea id="text" rows="6" style="width:100%%"></textarea><br>
Or upload files (.txt, .csv, .db): <input type="file" id="files" multiple accept=".txt,.csv,.db,.sqlite"></p>
<pre id="out" style="border:1px solid #888; padding:8px; height:400px; overflow:auto;"></pre>
<script>
// Read the chosen files as base64 text so they can be sent as JSON
async function readFiles() {
  const files = [];
  for (const f of document.getElementById("files").files) {
    let binary = "";
    new Uint8Array(await f.arrayBuffer()).forEach((b) => { binary += String.fromCharCode(b); });
    files.push({name: f.name, data: btoa(binary)});
  }
  return files;
}
async function run() {
  const body = JSON.stringify({
    task: document.getElementById("task").value,
    k: document.getElementById("k").value,
    text: document.getElementById("text").value,
    files: await readFiles(),
  });
  document.getElementById("out").textContent = await (await fetch("/run", {method: "POST", body})).text();
}
// Enter = Run (inside the custom data box, Enter makes a new line; use Ctrl+Enter there)
document.addEventListener("keydown", (e) => {
  const inTextBox = e.target.id === "text";
  if (e.key === "Enter" && (!inTextBox || e.ctrlKey || e.metaKey)) run();
});
</script></body></html>""" % "".join(f"<option>{name}</option>" for name in TASKS)


def file_to_text(name, data):
    """Turn an uploaded file (bytes) into plain text: one line per row."""
    if name.lower().endswith(".csv"):
        rows = csv.reader(io.StringIO(data.decode("utf-8", errors="replace")))
        return "\n".join(" ".join(row) for row in rows)
    if name.lower().endswith((".db", ".sqlite")):
        with tempfile.NamedTemporaryFile(suffix=".db") as tmp:  # sqlite3 needs a real file
            tmp.write(data)
            tmp.flush()
            db = sqlite3.connect(tmp.name)
            lines = []
            for (table,) in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
                for row in db.execute(f'SELECT * FROM "{table}"'):
                    lines.append(" ".join(str(value) for value in row if value is not None))
            db.close()
        return "\n".join(lines)
    return data.decode("utf-8", errors="replace")  # .txt


def run_script(name, k, text, files):
    """Run one task script and return what it printed."""
    command = [sys.executable, os.path.join(ROOT, TASKS[name])]
    if name == "Top-K Words":
        command.append(k)  # K is passed as the argument
    env = dict(os.environ)
    with tempfile.TemporaryDirectory() as folder:
        documents = {}  # file name -> text
        if text.strip():
            for i, part in enumerate(text.replace("\r", "").split("\n---\n"), start=1):
                documents[f"book_pasted{i}.txt"] = part
        for upload in files:
            stem = re.sub(r"[^A-Za-z0-9_]", "_", os.path.splitext(upload["name"])[0])
            documents[f"book_{stem}.txt"] = file_to_text(upload["name"], base64.b64decode(upload["data"]))
        if documents:
            # Custom data: write every document into a temporary folder as book_*.txt
            for file_name, content in documents.items():
                with open(os.path.join(folder, file_name), "w") as f:
                    f.write(content)
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
        form = json.loads(self.rfile.read(size))
        self.reply(run_script(form["task"], form["k"], form["text"], form["files"]), "text/plain")

    def log_message(self, *args):  # keep the terminal quiet
        pass


print(f"Open http://localhost:{PORT} (Ctrl+C to stop)")
webbrowser.open(f"http://localhost:{PORT}")
HTTPServer(("localhost", PORT), Handler).serve_forever()
