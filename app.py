from flask import Flask, render_template, request, abort
import json

app = Flask(__name__)

# Carga datos
with open('datos.json', encoding='utf-8') as f:
    CONSOLAS = json.load(f)

# Extraer lista única de desarrolladoras
developers_set = set()
for consola in CONSOLAS:
    for juego in consola.get('exclusivos', []):
        dev = juego.get('desarrollo', {}).get('desarrolladora')
        if dev:
            developers_set.add(dev)
    for juego in consola.get('subempresa', {}).get('exclusivos', []):
        dev = juego.get('desarrollo', {}).get('desarrolladora')
        if dev:
            developers_set.add(dev)
developers = sorted(developers_set)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consolas', methods=['GET'])
def consoles():
    return render_template('consoles.html', developers=developers)

@app.route('/listaconcolas', methods=['POST'])
def list_consoles():
    q = request.form.get('q', '').strip().lower()
    selected_dev = request.form.get('q', '')
    # Filtrar consolas que tengan al menos un juego de esa desarolladora
    results = []
    for i, consola in enumerate(CONSOLAS):
        encontrados = False
        for juego in consola.get('exclusivos', []) + consola.get('subempresa', {}).get('exclusivos', []):
            if juego.get('desarrollo', {}).get('desarrolladora', '').lower().startswith(q):
                encontrados = True
                break
        if encontrados:
            results.append((i, consola))
    # Calcular ventas totales de esa desarolladora
    total_sales = 0
    for consola in results:
        for juego in consola[1].get('exclusivos', []) + consola[1].get('subempresa', {}).get('exclusivos', []):
            if juego.get('desarrollo', {}).get('desarrolladora') == selected_dev:
                # Extrae número de millones (asume formato “XX millones”)
                num = juego.get('finanzas', {}).get('ventas', '0').split()[0]
                try:
                    total_sales += float(num)
                except:
                    pass
    # Formatea en “X millones”
    total_sales_str = f"{total_sales:.1f} millones" if total_sales else "0 millones"

    return render_template(
        'list_consoles.html',
        results=results,
        selected_dev=selected_dev,
        total_sales=total_sales_str
    )

# Nueva ruta: detalle por desarrolladora
@app.route('/desarrolladora')
def developer_detail():
    selected_dev = request.args.get('dev', '')
    if not selected_dev:
        abort(404)

    # Recolectar todos los juegos de esa desarrolladora
    games_by_dev = []
    for consola in CONSOLAS:
        nombre_console = consola['nombre']
        for juego in consola.get('exclusivos', []):
            if juego.get('desarrollo', {}).get('desarrolladora') == selected_dev:
                juego_copy = juego.copy()
                juego_copy['console_name'] = nombre_console
                games_by_dev.append(juego_copy)
        # Subempresa también
        sub = consola.get('subempresa', {})
        for juego in sub.get('exclusivos', []):
            if juego.get('desarrollo', {}).get('desarrolladora') == selected_dev:
                juego_copy = juego.copy()
                juego_copy['console_name'] = sub.get('nombre', nombre_console)
                games_by_dev.append(juego_copy)

    return render_template(
        'console_detail.html',
        selected_dev=selected_dev,
        games_by_dev=games_by_dev
    )

if __name__ == '__main__':
    app.run(debug=True)

