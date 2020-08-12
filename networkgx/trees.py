import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


class Tree:
    """
    TODO:   Accept different inputs
            Add clustering methods
            Draw Tree then highlight path

    """

    def __init__(self):
        """
        Initializes Tree global variables
        """

        # Dictionary to save node positions
        self.layout = None
        # links represents the edges as non-tuple list.
        self.positive_links = None
        # The negative correlation links.
        self.negative_links = None
        # The weighted edges of the tree
        self.edges = None
        # The tree nodes.
        self.nodes = None
        # The desired edges, in case of MST that should be the minimum spanning edges of the tree.
        self.path = None

    def set_layout(self):
        """
        Creates the positions dictionary for nodes
        """

        G = nx.Graph()
        G.add_edges_from(self.edges)
        self.layout = nx.spring_layout(G)

    def minimum_spanning_tree(self, algorithm='kruskal', draw=False):
        """
        Finds the minimum spanning tree

        :param algorithm: (str) The algorithm used to find the minimum spanning tree. (``kruskal`` by default, ``prim``,
        ``boruvka``)
        :param draw: (bool) If True, The function will plot the minimum spanning tree. (``False`` by default)
        Returns the networx graph object
        """

        tree = nx.Graph()
        tree.add_edges_from(self.edges)
        # the iterator foe the path
        self.path = nx.algorithms.minimum_spanning_edges(tree, weight='corr_value', algorithm=algorithm, data=True)

        min_spanning_tree = nx.Graph()
        min_spanning_tree.add_edges_from(self.path)

        if draw:
            draw_style = {'with_labels': True, 'node_color': 'orange', 'node_size': 400, 'edge_color': 'grey',
                           'linewidths': 1, 'font_size': 10, 'width': 1.5}

            plt.figure(figsize=(10, 6))
            ax = plt.subplot(111)
            plt.title('Minimum Spanning Tree', fontdict ={'fontsize':20})
            nx.draw(min_spanning_tree, ax=ax, label='Minimum Spanning Tree', **draw_style)
            plt.show()

        return min_spanning_tree

    def get_links(self):
        """
        returns the links array
        """
        return self.positive_links, self.negative_links

    def build(self, data: pd.DataFrame) -> nx.classes.graph.Graph:
        """
        The class backbone
        """
        # If data is a correlation matrix (pd.DataFrame)
        self._make_links_from_corr(data)
        self.edges = self._get_edges(self.positive_links)
        self.set_layout()
        mst = self.minimum_spanning_tree(draw=False)

        return mst

    def _make_links_from_corr(self, corr, threshold=0):
        """
        TODO:   make method accept multi dimensional corr
                make method split negative and positive corr

        Creates the links array which will reshape the correlation matrix to a DataFrame of the networks links, where
        first two columns are the source, and target nodes. and the last column is the dictionary of attributes.

        :param corr: (pd.DataFrame) The correlation matrix
        :param threshold: (None, float) The threshold value to return only weights above the threshold limit
        """

        links = corr.stack().reset_index()
        # Creates the edge link attributes.
        links.columns = ['src', 'trgt', 'att']
        # Removes the correlation between same variables. added copy to silence pandas warning
        links = links.loc[(links['src'] != links['trgt'])].copy()

        # Store positive correlations
        positive_links = links.loc[(links['att'] >= threshold)]
        # Store negative correlations
        negative_links = links.loc[(links['att'] < threshold)]

        positive_links.loc[:, 'att'] = [{'corr_value': x} for x in positive_links.loc[:, 'att']]
        negative_links.loc[:, 'att'] = [{'corr_value': x} for x in negative_links.loc[:, 'att']]

        self.positive_links = positive_links
        self.negative_links = negative_links

    @staticmethod
    def _get_edges(links, filtered=True, sort=True):
        """
        TODO: add support for links with multivariate random variables.
        Returns the edges for the graphs from the links array.
        """
        # Create a list of tuples containing edge data.
        edges = list(zip(links.iloc[:, 0], links.iloc[:, 1], links.iloc[:, 2]))

        if filtered:
            # Removing duplicated edges using list comprehension
            seen = set()  # Empty set used for list comprehension
            edges = [(a, b, c) for a, b, c in edges if not ((a, b) in seen or seen.add((a, b)) or seen.add((b, a)))]

        if sort:
            edges = sorted(edges, key=lambda x: x[2]['corr_value'])
        return edges
