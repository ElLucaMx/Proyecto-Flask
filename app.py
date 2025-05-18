from flask import Flask, render_template, request, abort
import json

app = Flask(__name__)

# Carga datos
with open('datos.json', encoding='utf-8') as f:
    CONSOLAS = json.load(f)

# Extraer lista única de desarrolladoras
developers_set = set()
for consola in CONSOLAS:
    for juego in consola.get('exclusivos', []) + consola.get('subempresa', {}).get('exclusivos', []):
        dev = juego.get('desarrollo', {}).get('desarrolladora')
        if dev:
            developers_set.add(dev)
developers = sorted(developers_set)

# Extraer lista única de modos de juego
modos_juego_set = set()
for consola in CONSOLAS:
    for juego in consola.get('exclusivos', []) + consola.get('subempresa', {}).get('exclusivos', []):
        modos = juego.get('jugabilidad', {}).get('modoJuego', [])
        for modo in modos:
            if modo:
                modos_juego_set.add(modo)
modos_juego = sorted(modos_juego_set)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consolas', methods=['GET', 'POST'])
def consoles():
    results = []
    total_sales_str = "0 millones"
    q = ''
    selected_dev = ''
    modo_juego_seleccionado = '' # Inicializa la nueva variable

    if request.method == 'POST':
        q = request.form.get('q', '').strip().lower()
        selected_dev = request.form.get('q', '')
        modo_juego_seleccionado = request.form.get('modoJuego_seleccionado', '') # Obtén el valor del nuevo select

        # Filtrar consolas que tengan al menos un juego que cumpla ambos criterios
        for i, consola in enumerate(CONSOLAS):
            encontrados = False
            for juego in consola.get('exclusivos', []) + consola.get('subempresa', {}).get('exclusivos', []):
                # Criterio de desarrolladora
                dev_match = juego.get('desarrollo', {}).get('desarrolladora', '').lower().startswith(q)

                # Criterio de modo de juego (si se ha seleccionado uno)
                modo_match = True # Por defecto es True si no se selecciona modo de juego
                if modo_juego_seleccionado:
                    modo_match = modo_juego_seleccionado in juego.get('jugabilidad', {}).get('modoJuego', [])

                if dev_match and modo_match:
                    encontrados = True
                    break
            if encontrados:
                results.append((i, consola))

        # Calcular ventas totales de esa desarrolladora (solo si se filtró por desarrolladora)
        # La lógica de ventas no se ve afectada por el modo de juego
        if selected_dev:
            total_sales = 0
            for consola in results: # Iterar sobre los resultados ya filtrados por desarrolladora y modo de juego
                for juego in consola[1].get('exclusivos', []) + consola[1].get('subempresa', {}).get('exclusivos', []):
                     # Solo suma ventas si coincide la desarrolladora original (ignorando el filtro de modo de juego aquí)
                    if juego.get('desarrollo', {}).get('desarrolladora') == selected_dev:
                        num = juego.get('finanzas', {}).get('ventas', '0').split()[0]
                        try:
                            total_sales += float(num)
                        except:
                            pass
            total_sales_str = f"{total_sales:.1f} millones" if total_sales else "0 millones"
        else:
             # Si no se seleccionó desarrolladora, las ventas totales no tienen sentido en este contexto
             total_sales_str = "N/A (Selecciona una desarrolladora para ver ventas)"


    return render_template(
        'consoles.html',
        developers=developers,
        modos_juego=modos_juego,  # Pasa la lista de modos de juego
        results=results,
        selected_dev=selected_dev,
        modo_juego_seleccionado=modo_juego_seleccionado, # Pasa el modo de juego seleccionado
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
