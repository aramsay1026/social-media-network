# Worked on by: Amy Ramsay
from graph_adt import UndirectedGraph

def main():
    g = UndirectedGraph()
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")

    print("Vertices:", g.get_vertices())
    print("Edges:", g.get_edges())
    print("BFS from A:", g.bfs("A"))
    print("DFS from A:", g.dfs("A"))

if __name__ == "__main__":
    main()
