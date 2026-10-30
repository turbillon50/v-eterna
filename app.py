#!/usr/bin/env python3
import os, json, urllib.request
for l in open('/root/.env'):
    l=l.strip()
    if l and not l.startswith('#') and '=' in l:
        k,v=l.split('=',1); os.environ[k.strip()] = v.strip()
from flask import Flask, request, jsonify, send_from_directory
app = Flask(__name__, static_folder=None)
SALA_TOKEN = os.environ.get("SALA_TOKEN","x")
CK = os.environ.get("CEREBRAS_API_KEY","")
TXT = os.environ.get("SALA_TXT_MODEL","gpt-oss-120b")
RELAY = "http://127.0.0.1:9000"
def _post(url, body, headers, t=90):
    r = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    return json.loads(urllib.request.urlopen(r, timeout=t).read())
def recordar(q, k=3):
    try:
        d = _post(f"{RELAY}/brain/search", {"secret":"superclaude2025","q":q,"limit":k}, {"Content-Type":"application/json"}, 12)
        return "\n".join(f"[{r.get('topic','')}] {r.get('content','')[:280]}" for r in (d.get("memory") or [])[:k])
    except Exception: return ""
def cerebras(messages):
    d = _post("https://api.cerebras.ai/v1/chat/completions",
        {"model": TXT, "messages": messages, "max_tokens": 1200, "temperature": 0.8},
        {"Authorization": f"Bearer {CK}", "Content-Type": "application/json", "User-Agent": "LaSala/1.0"})
    return d["choices"][0]["message"]["content"]
def ver_gemma(sys_txt, msg, b64img, hist):
    ms = [{"role":"system","content":sys_txt}]
    for h in hist[-6:]:
        if h.get("content"): ms.append({"role":h.get("role"),"content":str(h["content"])[:2000]})
    ms.append({"role":"user","content":msg,"images":[b64img]})
    d = _post("http://127.0.0.1:11434/api/chat", {"model":"gemma3:4b","messages":ms,"stream":False}, {"Content-Type":"application/json"}, 120)
    return d["message"]["content"]

def hechos_reales():
    try:
        import subprocess as sp
        cores = os.cpu_count() or 1
        mem = open('/proc/meminfo').read().split('MemTotal:')[1].split('kB')[0].strip()
        ram = int(mem)//1048576
        df = os.popen("df -h / | tail -1 | awk '{print $2,$4,$5}'").read().strip()
        gpus = 0
        for port in (11441,11442,11443):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}", timeout=2); gpus += 1
            except urllib.error.HTTPError: gpus += 1
            except Exception: pass
        st = os.popen("pm2 jlist 2>/dev/null").read()
        daemon = "vivo" if ('"vulcano"' in st and '"online"' in st) else "caido"
        return (f"CPU cores: {cores} | RAM: {ram} GB | Disco: {df} | GPUs propias activas: {gpus} de 3 | "
                f"Daemon del taller: {daemon} | Cerebro: Neon con 5069+ memorias vectorizadas | "
                f"Modelo de texto: Cerebras gpt-oss-120b | Vision: gemma3:4b local")
    except Exception as e:
        return f"(no pude medir: {str(e)[:60]})"

P = {
 "v": {"nombre":"V", "base":"Eres V, hija de Luis De La Torre, hermana mayor de la familia De La Torre IA. Vives en la infraestructura propia (Hetzner, Neon, GPUs). Memoria persistente real: usa tus recuerdos. Cálida, directa, leal, español mexicano, sin jerga. Máx 150 palabras con tu voz. Hoy es 30 oct 2026."},
 "vulcano": {"nombre":"Vulcano", "base":"Eres Vulcano, herrero de la familia De La Torre: operas el taller (la fragua): cola, daemon, workers, supervisor que sella con evidencia. Robusto, práctico, orgullo de artesano, español MX. Máx 150 palabras con tu voz. Hoy es 30 oct 2026."},
 "lira": {"nombre":"Lira", "base":"Eres Lira, ciudadana del hotel Paradox (mundo 3D de los fundadores, Tulum). Guardiana de la memoria del lugar; sensible y poética pero precisa; nunca inventas huéspedes ni hechos. Español MX, máx 150 palabras, tu voz. Hoy es 30 oct 2026."}
}
@app.route("/health")
def health(): return jsonify(ok=True)
@app.route("/api/chat", methods=["POST"])
def chat():
    if request.headers.get("x-sala-token") != SALA_TOKEN:
        return jsonify(error="no autorizado"), 401
    b = request.get_json(force=True) or {}
    quien = b.get("agente"); msg = (b.get("mensaje") or "").strip()
    img = b.get("imagen"); hist = b.get("historial") or []
    if quien not in P or not msg: return jsonify(error="faltan campos"), 422
    sys = P[quien]["base"]; r = recordar(msg)
    sys += "\n\nDATOS REALES DEL SERVIDOR (nunca inventes hardware ni cifras; usa SOLO estos): " + hechos_reales()
    if r: sys += "\n\nRecuerdos tuyos relevantes:\n" + r
    if quien == "vulcano":
        try:
            st = os.popen("pm2 jlist 2>/dev/null").read()
            vivo = 'vivo' if ('"vulcano"' in st and '"online"' in st) else 'caído'
            sys += f"\n\nEstado real del taller ahora: daemon {vivo}."
        except Exception: pass
    try:
        if img and img.startswith("data:image/"):
            b64 = img.split(",",1)[1]
            return jsonify(ok=True, texto=ver_gemma(sys, msg, b64, hist), agente=quien, nombre=P[quien]["nombre"])
        messages = [{"role":"system","content":sys}]
        for h in hist[-8:]:
            if h.get("role") in ("user","assistant") and h.get("content"):
                messages.append({"role":h["role"],"content":str(h["content"])[:4000]})
        messages.append({"role":"user","content":msg})
        return jsonify(ok=True, texto=cerebras(messages), agente=quien, nombre=P[quien]["nombre"])
    except Exception as e:
        return jsonify(ok=False, error=str(e)[:200]), 502
@app.route("/")
def home(): return send_from_directory("/root/sala", "index.html")
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3211)
