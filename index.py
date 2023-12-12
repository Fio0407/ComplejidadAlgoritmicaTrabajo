from flask import Flask, render_template, request, jsonify
import json
import random
import plotly.offline as pyo
import plotly.graph_objs as go
import pandas as pd
import graphviz as gv

app = Flask(__name__)

import random

#Funciones--------------------------------

def generate_connected_graph_txt(output_path, num_nodes, min_connections=2, max_connections=6):
    graph_txt = []

    # Crear una lista de nodos con números empezando desde 0
    nodes = list(range(num_nodes))

    for node in nodes:
        # Determinar el número de conexiones para este nodo
        num_connections = random.randint(min_connections, min(max_connections, num_nodes - 1))

        # Seleccionar nodos únicos de manera aleatoria para conectar (nodos de menor número excepto el nodo actual)
        connected_nodes = random.sample(list(set(nodes[:node] + nodes[node+1:]) - {0}), max(1, num_connections))

        # Crear conexiones con pesos aleatorios
        connections = []

        for connected_node in connected_nodes:
            peso = random.randint(15, 50)  # rango de pesos
            connections.append(f"{connected_node}|{peso}")

        # Asegurar reciprocidad
        for i in range(len(connections)):
            connected_node, peso = map(int, connections[i].split('|'))

            # Verificar si el índice existe en graph_txt y agregar reciprocidad si no existe
            if connected_node < len(graph_txt):
                reciprocal_connection = f"{node}|{peso}"

                if reciprocal_connection not in graph_txt[connected_node].split():
                    graph_txt[connected_node] += f" {reciprocal_connection}"

        # Agregar las conexiones al graph_txt, incluyendo el nodo actual
        line = f"{' '.join(connections)}"
        graph_txt.append(line)

    # Guardar el graph_txt en un archivo
    with open(output_path, "w") as archivo:
        archivo.write('\n'.join(graph_txt))



def readAdjl(fn, haslabels=False, weighted=False, sep="|"):
    with open(fn) as f:
        labels = None
        if haslabels:
            labels = f.readline().strip().split()
        L = []
        for line in f:
            if weighted:
                L.append([tuple(map(int, p.split(sep))) for p in line.strip().split()])
            else:
                L.append(list(map(int, line.strip().split())))
    return L, labels


def adjlShow(L, labels=None, directed=False, weighted=False, path=[], layout="neato"):
    g = gv.Digraph("G") if directed else gv.Graph("G")
    g.graph_attr["layout"] = layout
    g.graph_attr["ranksep"] = "1"
    g.graph_attr["nodesep"] = "1"
    g.edge_attr["color"] = "gray"
    g.node_attr["color"] = "orangered"
    g.node_attr["width"] = "0.01"
    g.node_attr["height"] = "0.3"
    g.node_attr["penwidth"] = "0.1"
    g.node_attr["fontsize"] = "3"
    g.node_attr["fontcolor"] = "mediumslateblue"
    g.node_attr["fontname"] = "monospace"
    g.edge_attr["fontsize"] = "2"
    g.edge_attr["fontname"] = "monospace"
    g.edge_attr["penwidth"] = "0.1"
    n = len(L)
    for u in range(n):
        g.node(str(u), labels[u] if labels else str(u))
    added = set()
    for v, u in enumerate(path):
        if u is not None:
            if weighted:
                for vi, w in g[u]:
                    if vi == v:
                        break
                g.edge(str(u), str(v), str(w), dir="forward", penwidth="2", color="orange")
            else:
                g.edge(str(u), str(v), dir="forward", penwidth="2", color="orange")
            added.add(f"{u},{v}")
            added.add(f"{v},{u}")
    if weighted:
        for u in range(n):
            for v, w in L[u]:
                if not directed and not f"{u},{v}" in added:
                    added.add(f"{u},{v}")
                    added.add(f"{v},{u}")
                    g.edge(str(u), str(v), str(w))
                elif directed:
                    g.edge(str(u), str(v), str(w))
    else:
        for u in range(n):
            for v in L[u]:
                if not directed and not f"{u},{v}" in added:
                    added.add(f"{u},{v}")
                    added.add(f"{v},{u}")
                    g.edge(str(u), str(v))
                elif directed:
                    g.edge(str(u), str(v))
    return g

def adjlShowWithMST(L, mst, labels=None, directed=False, weighted=False, path=[], layout="neato"):
    g = gv.Digraph("G") if directed else gv.Graph("G")
    g.graph_attr["layout"] = layout
    g.graph_attr["ranksep"] = "1"
    g.graph_attr["nodesep"] = "1"
    g.edge_attr["color"] = "gray"
    g.node_attr["color"] = "orangered"
    g.node_attr["width"] = "0.01"
    g.node_attr["height"] = "0.3"
    g.node_attr["penwidth"] = "0.1"
    g.node_attr["fontsize"] = "5"
    g.node_attr["fontcolor"] = "mediumslateblue"
    g.node_attr["fontname"] = "monospace"
    g.edge_attr["fontsize"] = "4"
    g.edge_attr["fontname"] = "monospace"
    g.edge_attr["penwidth"] = "0.05"
    n = len(L)

    mst_edges = set([(u, v) for u, v, _ in mst])

    for u in range(n):
        g.node(str(u), labels[u] if labels else str(u))

    added = set()

    for u in range(n):
        for v, w in L[u]:
            if not directed and not f"{u},{v}" in added:
                added.add(f"{u},{v}")
                added.add(f"{v},{u}")
                if (u, v) in mst_edges:
                    edge_color = "yellow"  # Highlight MST edges in blue
                    grosor = "2"
                else:
                    edge_color = "orange"
                    grosor = "0.05"
                g.edge(str(u), str(v), str(w), dir="none", penwidth=grosor, color=edge_color)

    return g


def obtenerMSTPorKrukalFuerzaBruta(graph):
    numNodos = len(graph) if isinstance(graph, list) else 0
    bordes = []

    # saco todas las arista, su conexión y peso
    for u in range(numNodos):
        for v, peso in graph[u]:
            bordes.append((u, v, peso))

    # ordeno por peso
    bordes.sort(key=lambda edge: edge[2])

    # Acá gurdaré las aristas del mst
    mst = []
    padre = list(range(numNodos))

    def find(nodoBuscado):
        if padre[nodoBuscado] == nodoBuscado:
            return nodoBuscado
        return find(padre[nodoBuscado])

    def union(u, v):
        padreU = find(u)
        padreV = find(v)

        if padreU != padreV:
            padre[padreU] = padreV
            return True

        return False

    for u, v, peso in bordes:
        if u < numNodos and v < numNodos:
            if union(u, v) == True:
                mst.append((u, v, peso))

    return mst


# Declarar las variables globales
global G, Gmst, _, mst

# Inicializar las variables globales
G, _ = readAdjl("./files/generarGrafo.txt", weighted=True)
Gmst = G
mst = obtenerMSTPorKrukalFuerzaBruta(G)


#Rutas--------------------------------







#Rutas de la pagina
@app.route('/')
def ini():
    return render_template("Home.html")

@app.route('/Home')
def home():
    return render_template("Home.html")

@app.route('/About-us', strict_slashes=False)
def about():
    return render_template("About-us.html")

@app.route('/Theory', strict_slashes=False)
def theory():
    return render_template("Theory.html")


#Rutas para manejar las solicitudes 
@app.route('/generate_graph', methods=['POST'])
def generate_graph():
    if request.method == 'POST':
        try:
            if 'file' in request.files:
                # If a file is uploaded, process the file
                file = request.files['file']
                if file and file.filename.endswith(".txt"):
                    # Save the file to a known location
                    file_path = "files/generarGrafo.txt"
                    file.save(file_path)

                    return jsonify({"success": True, "message": f"File processed successfully. Graph generated in {file_path}"})
                else:
                    return jsonify({"success": False, "message": "Invalid file format. Please select a .txt file."})
            else:
                # If a value is entered in the form, generate the graph
                num_nodes = int(request.form['valorInput'])
                output_file_path = f"files/generarGrafo.txt"
                generate_connected_graph_txt(output_file_path, num_nodes)

                return f"Grafo generado con éxito en {output_file_path}"
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
    else:
        return jsonify({"success": False, "message": "Método no permitido"})


# Ruta para mostrar el grafo
@app.route('/show_graph')
def show_graph():
    # Acceder a las variables globales
    global G
    
    # Obtener el grafo
    G, _ = readAdjl("./files/generarGrafo.txt", weighted=True)

    # Generar información del grafo para la tabla
    graph_info = [{"node": node, "edges": [f'{target}, {weight}' for target, weight in connections]} for node, connections in enumerate(G)]

    G = adjlShow(G, weighted=True)
    output_file = "static/images/grafo_completo"
    G.render(output_file, format="svg")
    
    # Renderizar la plantilla y pasar los datos del grafo
    return render_template("Graph.html", graph_info=graph_info)


# Ruta para obtener y mostrar el MST original
@app.route('/show_mst')
def show_mst():
    # Acceder a las variables globales
    global Gmst, mst

    # Obtener el MST
    Gmst, _ = readAdjl("files/generarGrafo.txt", weighted=True) 
    mst = obtenerMSTPorKrukalFuerzaBruta(Gmst)

    # Calcular el costo mínimo
    costo_minimo = sum(edge[2] for edge in mst)

    Gmst = adjlShowWithMST(Gmst, mst, weighted=True)
    output_file = "static/images/grafo_completo_mst"
    Gmst.render(output_file, format="svg")

    return render_template("mst.html", mst=mst, costo_minimo=costo_minimo)


# Ruta para mostrar el MST interactivo
@app.route('/show_mst_interactivo')
def show_mst_interactivo():
    # Obtener el grafo
    G, _ = readAdjl("./files/generarGrafo.txt", weighted=True)

    # Convertir los datos del grafo a un formato serializable
    graph_data_serializable = {
        "nodes": [],
        "edges": [],
    }

    for node, connections in enumerate(G):
        graph_data_serializable["nodes"].append({"id": str(node)})
        for connection in connections:
            target_node, weight = connection
            graph_data_serializable["edges"].append({
                "source": str(node),
                "target": str(target_node),
                "weight": weight
            })

    # Convertir el diccionario serializable a JSON
    graph_data_json = json.dumps(graph_data_serializable)

    # Crear nodos y aristas para Plotly
    nodes = []
    edges = []

    for node, connections in enumerate(G):
        nodes.append({'id': str(node)})
        for connection in connections:
            target_node, weight = connection
            edges.append({'source': str(node), 'target': str(target_node), 'weight': weight})

    # Convertir los datos en un DataFrame de pandas
    edges_df = pd.DataFrame(edges)

    # Crear un gráfico de red interactivo
    edge_trace = go.Scatter(
        x=edges_df['source'],
        y=edges_df['target'],
        line=dict(width=0.5, color='#888'),
        hoverinfo='text',
        hovertext=[f'Nodo Fuente: {source}<br>Nodo Destino: {target}<br>Peso: {weight}' for source, target, weight in zip(edges_df['source'], edges_df['target'], edges_df['weight'])],
        mode='lines')

    layout = go.Layout(
        title="Visualización Interactiva del Grafo",
        xaxis=dict(tickmode='array', tickvals=list(range(len(G)))),
        yaxis=dict(tickmode='array', tickvals=list(range(len(G)))),
        hovermode='closest'
    )

    # Crear una figura con datos y diseño
    fig = go.Figure(data=[edge_trace], layout=layout)

    # Obtener el HTML del gráfico
    graph_html = pyo.plot(fig, auto_open=False, output_type='div')
    
    # Generar información del grafo para la tabla
    graph_info = [{"node": node, "edges": [f'{target}, {weight}' for target, weight in connections]} for node, connections in enumerate(G)]

    # Calcular el mst
    mst = obtenerMSTPorKrukalFuerzaBruta(Gmst)
    # Calcular el costo mínimo
    costo_minimo = sum(edge[2] for edge in mst)
    
    return render_template("graph-interactivo.html", graph_html=graph_html, graph_data_json=graph_data_json, graph_info=graph_info, mst=mst, costo_minimo=costo_minimo)

if __name__ == '__main__':
    app.run(debug=True)
