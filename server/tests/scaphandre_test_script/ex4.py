#!/usr/bin/env python3
import sys
sys.setrecursionlimit(10**6)

def main():
    data = sys.stdin.read().split()
    s, b, v = map(int, data[:3])

    # Total nodes: 0 = source, 1..s = students, s+1..s+b = theses, s+b+1 = sink
    N = s + b + 2
    source, sink = 0, s + b + 1

    # Build graph: each edge is [v, capacity, rev]
    graph = [[] for _ in range(N)]
    def add_edge(u, v, cap):
        graph[u].append([v, cap, len(graph[v])])
        graph[v].append([u, 0, len(graph[u]) - 1])

    # Connect source to each student (capacity 1)
    for u in range(1, s + 1):
        add_edge(source, u, 1)

    # Connect each thesis to sink (capacity 1)
    for j in range(1, b + 1):
        add_edge(s + j, sink, 1)

    # For each preference, add an edge from student to thesis
    it = iter(data[3:])
    for stu, th in zip(it, it):
        add_edge(int(stu), s + int(th), 1)

    # DFS to find an augmenting path from u to sink with available flow.
    def dfs(u, flow, visited):
        if u == sink:
            return flow
        visited[u] = True
        for edge in graph[u]:
            v, cap, rev = edge
            if not visited[v] and cap > 0:
                pushed = dfs(v, min(flow, cap), visited)
                if pushed:
                    edge[1] -= pushed
                    graph[v][edge[2]][1] += pushed
                    return pushed
        return 0

    max_flow = 0
    # Repeatedly find augmenting paths until none exist.
    while True:
        visited = [False] * N
        pushed = dfs(source, float('inf'), visited)
        if not pushed:
            break
        max_flow += pushed

    # Write the output via the binary interface with no trailing newline.
    sys.stdout.buffer.write(str(max_flow).encode())

if __name__ == '__main__':
    main()
