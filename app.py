from flask import Flask, render_template, request, jsonify
import heapq

app = Flask(__name__)

# Graph data
graph = {
    'A': {'B': 2, 'D': 6},
    'B': {'A': 2, 'C': 3, 'E': 1},
    'C': {'B': 3, 'F': 5},
    'D': {'A': 6, 'E': 2},
    'E': {'B': 1, 'D': 2, 'F': 4},
    'F': {'C': 5, 'E': 4}
}

# Node positions for canvas
positions = {
    'A': (100, 100),
    'B': (300, 100),
    'C': (500, 100),
    'D': (100, 300),
    'E': (300, 300),
    'F': (500, 300)
}

start = "A"
treasure = "F"

# Game state
game_state = {"current": start, "visited": [start], "total_cost": 0}

# Dijkstra's algorithm
def dijkstra(graph, start):
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    parent = {node: None for node in graph}

    while pq:
        current_dist, current_node = heapq.heappop(pq)
        if current_dist > distances[current_node]:
            continue
        for neighbor, weight in graph[current_node].items():
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                parent[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))
    return distances, parent

def shortest_path(parent, target):
    path = []
    while target is not None:
        path.insert(0, target)
        target = parent[target]
    return path

@app.route("/")
def home():
    return render_template("index.html", positions=positions, graph=graph, start=start, treasure=treasure)

@app.route("/move", methods=["POST"])
def move():
    data = request.json
    choice = data["choice"]
    if choice not in graph[game_state["current"]]:
        return jsonify({"error": "Invalid move"}), 400

    cost = graph[game_state["current"]][choice]
    game_state["current"] = choice
    game_state["visited"].append(choice)
    game_state["total_cost"] += cost

    if choice == treasure:
        distances, parent = dijkstra(graph, start)
        optimal_path = shortest_path(parent, treasure)
        return jsonify({
            "game_over": True,
            "visited": game_state["visited"],
            "total_cost": game_state["total_cost"],
            "optimal_path": optimal_path,
            "optimal_cost": distances[treasure]
        })

    return jsonify({
        "current": game_state["current"],
        "visited": game_state["visited"],
        "total_cost": game_state["total_cost"]
    })

@app.route("/reset")
def reset():
    game_state["current"] = start
    game_state["visited"] = [start]
    game_state["total_cost"] = 0
    return jsonify({"message": "Game reset"})

if __name__ == "__main__":
    app.run(debug=True)
