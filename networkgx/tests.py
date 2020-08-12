"""
The Dash Graph creates an interactive 2D graph modeling networks in an HTML output.
"""
import pandas as pd
import networkx as nx

import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_cytoscape as cyto

from networkgx.trees import Tree

import plotly.graph_objects as go

# The dash app
app = dash.Dash(__name__)
app.css.config.serve_locally = False


class DashGraph(nx.classes.graph.Graph):
    """
    This class creates a dash app using Flask.io

    class parameter input should the the networkx graph
    """

    def __init__(self, graph, weight='weight', **attr):
        """
        :param graph: is the networkx graph object
        """
        super().__init__(**attr)
        # The networkx graph object

        self.G = graph
        # the weight attribute in the edge tuples data dictionary
        self.weight = weight
        # The dictionary of the nodes coordinates
        self.pos = nx.layout.spring_layout(self.G)
        # The edges and nodes graph data
        self.elements = []
        # Keeps track of the number of nodes in graph
        self.num_of_nodes = len(self.G.nodes)

        # Make elements
        self._make_elements()

        # The nodes graph data
        self.dash_layout = html.Div([
            cyto.Cytoscape(
                id='MST',
                layout={'name': 'preset'},
                style={'width': '100%', 'height': '400px'},
                elements=self.elements,
                stylesheet=[{
                    'selector': 'node',
                    'style': {
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'background-color': '#F1B40E',
                        'color': '',
                        'font-family': 'sans-serif',
                        'font-size': '12',
                        'font-weight': 'bold',
                        'border-width': 1.5,
                        'border-color': '#161615'
                    }}, {
                    'selector': 'edge',
                    'style': {
                        'line-color': '#6F5306',
                    }
                }]
            ), html.Pre(id='cytoscape-tapNodeData-json', style={
                'border': 'thin lightgrey solid',
                'overflowX': 'scroll'})
        ])

    def run_dash(self):
        """
        Draws the tree from a networkx Graph object using plotly
        """

        # to add ability to use columns
        app.css.append_css({
            'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
        })

        app.layout = self.dash_layout
        # app.run_server(debug=True)

    def _make_elements(self):
        """
        doc
        """
        for node in self.pos:
            self.elements.append({
                'data': {'id': node, 'label': node},
                'position': {
                    'x': self.pos[node][0] * 256,
                    'y': self.pos[node][1] * 256
                }
            })

        for node1, node2, weight in self.G.edges(data=True):
            self.elements.append({'data': {'source': node1, 'target': node2, 'weight': weight['corr_value']}})


# =============================================================================

# Class initiations
tree = Tree()

# Get sample data
stock_prices = pd.read_csv('../datasets/data/stock_prices.csv', parse_dates=True, index_col='Date')
stock_returns = stock_prices.pct_change()
stock_returns.dropna(inplace=True)

# get Correlation matrix
corr_matrix = stock_returns.corr()

# Build the Minimum Spanning Tree of the Correlation matrix as a networkx graph object
mst = tree.build(corr_matrix)


# ========================== CALLBACKS =======================================
@app.callback(Output('cytoscape-tapNodeData-json', 'children'),
              [Input('MST', 'tapNode')])
def even_tap_node(data):

    if data:
        return json.dumps(data['edgesData'], indent=2)



if __name__ == '__main__':
    """
    The main of the tests file
    """

    dash_graph = DashGraph(mst)
    dash_graph.run_dash()
    app.run_server(debug=True)
