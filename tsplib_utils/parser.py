import math

import networkx as nx
from matplotlib import pyplot as plt

from tsplib_utils.helper import *

import scienceplots

plt.style.use(["science"])


class TSPParser:
    # single source of data
    # for outsiders, G -> read only if not necessary
    G: nx.Graph = None

    @classmethod
    def __init__(cls, benchmark: str, visualize: bool = True) -> None:
        cls.G = nx.Graph(benchmark=benchmark,
                         opt_tour=[], opt_tour_length=0,
                         x_tour=[], x_tour_length=math.inf)
        cls.load_tsp_file()
        cls.load_opt_file()
        if visualize:
            cls.plot_graph()

    @classmethod
    def load_tsp_file(cls):
        # __benchmark__.tsp
        lines = read_lines(filepath=f"tsplib_benchmark/{cls.G.graph['benchmark']}.tsp")

        # DIMENSION -> nums of cities/nodes/vertices
        dimension = parse_dimension(lines)

        # NODE_COORD_SECTION -> nodes/vertices with location
        starter = lines.index("NODE_COORD_SECTION") + 1
        for index in range(starter, starter + dimension):
            i, x, y = lines[index].strip().split()
            cls.G.add_node(int(i), loc=(float(x), float(y)))

        # GRAPH -> edges/links with distance
        for i in range(1, cls.G.number_of_nodes() + 1):
            for j in range(i + 1, cls.G.number_of_nodes() + 1):
                x1, y1 = cls.G.nodes[i]["loc"]
                x2, y2 = cls.G.nodes[j]["loc"]
                # N.B. EUC_2D: 用勾股定理算出两点（城市）间距离后，四舍五入取整
                cls.G.add_edge(i, j, weight=round_distance(x1, y1, x2, y2))

    @classmethod
    def load_opt_file(cls):
        # .opt may not exist at all
        filepath = f"tsplib_benchmark/{cls.G.graph['benchmark']}.opt.tour"
        if os.path.exists(filepath):
            lines = read_lines(filepath)
            starter = lines.index("TOUR_SECTION") + 1
            counter, opt_tour, opt_tour_length = 0, [], 0
            for index in range(starter, len(lines)):
                # rd100.opt.tour
                if counter >= cls.G.number_of_nodes():
                    break

                for node_index in lines[index].strip().split():
                    # a permutation corresponds to a circular tour
                    # e.g. if the permutation goes like [1,2,3,4,5]
                    #      then the tour would be 1->2->3->4->5...1
                    opt_tour.append(int(node_index))
                    counter += 1

            opt_tour_length = length_of_a_tour(cls.G, opt_tour)
            cls.G.graph["opt_tour"], cls.G.graph["opt_tour_length"] = opt_tour, opt_tour_length
            # FIXME all optimal solutions in euc_2d but tsp225, are consistent with the reported value
            # http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/STSP.html
            print(f"{cls.G.graph['benchmark']} -> {opt_tour_length}")

    @classmethod
    def set_a_tour(cls, a_tour: List[int], a_tour_length: int = -1):
        if a_tour_length == -1:
            a_tour_length = length_of_a_tour(cls.G, a_tour)

        if a_tour_length < cls.G.graph["x_tour_length"]:
            cls.G.graph["x_tour"] = a_tour
            cls.G.graph["x_tour_length"] = a_tour_length

        cls.plot_graph()

    @classmethod
    def plot_graph(cls):
        plt.clf()

        _axes = True if cls.G.graph["x_tour"] else False
        if _axes:
            fig, axes = plt.subplots(2, 1, figsize=(5, 8), layout='constrained', dpi=500)
        else:
            fig, axes = plt.subplots(layout='constrained', dpi=500)

        ax = axes[0] if _axes else axes
        color = random_color()
        # problem instance with optimal tour -> vertices/nodes
        xs, ys = [], []
        for index, data in cls.G.nodes(data=True):
            xs.append(data["loc"][0])
            ys.append(data["loc"][1])
        ax.scatter(xs, ys, color=color, s=2, zorder=1)
        ax.set_title(f"{cls.G.graph['benchmark']}")

        if cls.G.graph["opt_tour"]:
            plot_tsp_tour(ax, color, cls.G, cls.G.graph["opt_tour"])
            ax.set_title(f"{cls.G.graph['benchmark']}'s optimal tour - {cls.G.graph['opt_tour_length']}")

        if cls.G.graph["x_tour"]:
            ax = axes[1]
            plot_tsp_tour(ax, random_color(), cls.G, cls.G.graph["x_tour"])
            ax.set_title(f"{cls.G.graph['benchmark']}'s experiment result - {cls.G.graph['x_tour_length']}")

        plt.savefig("2.png", dpi=800)
        plt.show()
