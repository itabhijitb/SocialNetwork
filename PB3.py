#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:58:31 2016

@author: abhibhat
"""
import pants
import sys


class TSP:
    def __init__(self, no_of_skills, no_of_nodes, node_value, adj):
        self.no_of_skills = no_of_skills
        self.no_of_nodes = no_of_nodes
        self.node_value = node_value
        self.adj = adj
        self.dist = self.dist_mat(self.node_value, self.adj)

    @staticmethod
    def dist_mat(node_value, adj, p=1., q=1.):
        '''The distance is just not the Euclidian distance but the path code
           between two nodes is assumed to be directly proportional to the
           edge cost and inversely proportional to the uniqueness between the
           skillsets.
        '''
        dist = [[0] * len(adj) for _ in range(len(adj))]
        for a in range(len(adj)):
            for b in range(len(adj[0])):
                if adj[a][b]:
                    skill_cost = len(set(node_value[a]) ^ set(node_value[b]))
                    edge_cost = adj[a][b]
                    dist[a][b] = edge_cost**q / (skill_cost**(p))
                    dist[b][a] = dist[a][b]
                else:
                    dist[a][b] = dist[b][a] = sys.maxsize
        return dist

    def minimal_subset_path(self, tour):
        path = []
        skills = set()
        for t in tour:
            skills |= set(self.node_value[t])
            path.append(t)
            if len(skills) == self.no_of_skills:
                break
        return path

    def aco(self):
        '''ACO is a simulated approach wherein it is assumed that ants are
        exploring possible routes on the graph. Using a probabilistic approach
        which considers both the cost and the amount of pheromone deposited
        each ant chooses the next city to visit.
        Until each opf the ants complets a tour, they explore, depositing
        pheromone on each edge that they cross. The Ant which completes with
        tour with the lowest cost wins. The amount of pheromone deposited is
        inversely proportional to the tour length: the shorter the tour, the
        more it deposits.
        
        Time Comlexity: http://ls2-www.cs.tu-dortmund.de/~sudholt/chapterACO09.pdf'''
        nodes = list(range(len(self.dist)))
        world = pants.World(nodes, lambda a, b: self.dist[a][b])
        solver = pants.Solver()
        solution = solver.solve(world)
        path = self.minimal_subset_path(solution.tour)
        return path

    def brute_force(self):
        '''Find all possible paths from each node and then select the path
           with the minimum cost
           Time Complexity: O(n!)
           Space Complexity: O(n)
        '''
        def tour_cost(path):
            return sum(self.adj[p1][p2] if adj[p1][p2] else sys.maxsize
                       for p1, p2 in zip(path, path[1:]))

        from itertools import permutations
        nodes = list(range(len(self.dist)))
        min_path = sys.maxsize
        for start in nodes:
            path = min((perm for perm in permutations(nodes)
                        if perm[0] == start),
                       key=tour_cost)
            path = self.minimal_subset_path(path)
            min_path = min(min_path, tour_cost(path))
        return path

    def nearest_neighbour(self):
        """Selects the nearest nrighbour as the next move. Though the worst
        case can be quite fatal, the average case is just 25% dearer than the
        optimal solution
        https://en.wikipedia.org/wiki/Nearest_neighbour_algorithm
        Time Complexity: O(n!)
        Space Complexity: O(n^2)
        """
        start = 0
        unvisited = list(range(len(self.dist)))
        path = [start]
        unvisited.remove(start)
        while unvisited:
            nearest_neighbour = min(unvisited,
                                    key=lambda x: self.dist[path[-1]][x])
            path.append(nearest_neighbour)
            unvisited.remove(nearest_neighbour)
        path = self.minimal_subset_path(path)
        return path

if __name__ == "__main__":
    no_of_skills = int(input())
    no_of_nodes = int(input())
    node_value = [list(map(int, input().split())) for _ in range(no_of_nodes)]
    adj = [list(map(int, input().split())) for _ in range(no_of_nodes)]
    tsp = TSP(no_of_skills, no_of_nodes, node_value, adj)
    path = tsp.aco()
    cost = sum(adj[i][j] for i, j in zip(path, path[1:]))
    print("ACO: cost = {}, path = {}".format(cost, path))
    path = tsp.nearest_neighbour()
    cost = sum(adj[i][j] for i, j in zip(path, path[1:]))
    print("Nearest Neighbour: cost = {}, path = {}".format(cost, path))
    path = tsp.brute_force()
    cost = sum(adj[i][j] for i, j in zip(path, path[1:]))
    print("Brute Force: cost = {}, path = {}".format(cost, path))
