from flask import Flask, render_template, request, abort
import json

app = Flask(__name__)

# Carga inicial de datos desde datos.json
with open('datos.json', encoding='utf-8') as f:
    CONSOLAS = json.load(f)

@app.route('/')
def index():
    # Página inicial con logo central
    return render_template('index.html')

@app.route('/consolas', methods=['GET'])
def consoles():
    # Mostrar formulario de búsqueda
    return render_template('consoles.html')

@app.route('/listaconcolas', methods=['POST'])
def list_consoles():
    # Leer parámetros del formulario
    q = request.form.get('q', '').strip().lower()
    show_sub = bool(request.form.get('show_sub'))

    # Filtrar por subempresa.nombre
    results = []
    for i, consola in enumerate(CONSOLAS):
        empresa = consola.get('subempresa', {}).get('nombre', '').lower()
        if not q or empresa.startswith(q):
            results.append((i, consola))

    return render_template(
        'list_consoles.html',
        results=results,
        q=request.form.get('q', ''),
        show_sub=show_sub
    )

@app.route('/consola/<int:cid>')
def console_detail(cid):
    # Mostrar detalle de una consola concreta
    if cid < 0 or cid >= len(CONSOLAS):
        abort(404)

    consola = CONSOLAS[cid]
    # Leer flag desde query string
    show_sub = request.args.get('show_sub', '0') == '1'

    return render_template(
        'console_detail.html',
        consola=consola,
        show_sub=show_sub
    )

if __name__ == '__main__':
    app.run(debug=True)
