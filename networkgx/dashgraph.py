"""
The Dash Graph creates an interactive 2D graph modeling networks in an HTML output.
"""
import pandas as pd
import networkx as nx

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
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
        # The edges graph data
        self.edge_trace = go.Scatter(
            x=[],
            y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        # Keeps track of the number of nodes in graph
        self.num_of_nodes = len(self.G.nodes)

        # The nodes graph data
        self.node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='blues',
                reversescale=True,
                color=[],
                size=16,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line=dict(width=2,
                          color='black')))

        # gets the edges and nodes trace data
        self._make_edges()
        self._make_nodes()
        # Adds style to edges and nodes
        self._style()

        # The figure style
        self.fig = go.Figure(data=[self.edge_trace, self.node_trace],
                             layout=go.Layout(
                                 title='<br>Minimum Spanning Tree of ' + str(self.num_of_nodes) + ' nodes',
                                 titlefont=dict(size=16),
                                 showlegend=False,
                                 hovermode='closest',
                                 margin=dict(b=20, l=5, r=5, t=40),
                                 annotations=[dict(
                                     showarrow=False,
                                     xref="paper", yref="paper",
                                     x=0.005, y=-0.002)],
                                 xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                 yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

        self.dash_layout = html.Div([
            html.Div(dcc.Graph(id='Graph', figure=self.fig)),
            html.Div(className='row', children=[
                html.Div([html.H2('Overall Data'),
                          html.P('Num of nodes: ' + str(len(self.G.nodes))),
                          html.P('Num of edges: ' + str(len(self.G.edges)))],
                         className='three columns'),
                html.Div([
                    html.H2('Selected Data'),
                    html.Div(id='selected-data'),
                ], className='six columns')
            ])
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
        #app.run_server(debug=True)

    def _make_edges(self):
        """
        Creates the edges to use for a scatter plot
        """

        for edge in self.G.edges():
            x0, y0 = self.pos[edge[0]]
            x1, y1 = self.pos[edge[1]]
            self.edge_trace['x'] += tuple([x0, x1, None])
            self.edge_trace['y'] += tuple([y0, y1, None])

    def _make_nodes(self):
        """
        Creates the nodes to use for a scatter plot
        """
        for node in self.pos:
            x, y = self.pos[node]
            self.node_trace['x'] += tuple([x])
            self.node_trace['y'] += tuple([y])

    def _style(self):
        """
        Creates a stylized tree with weight data
        # TODO: Add Neighboring nods weight value
                Add different shapes and colors to nodes when you develop clustering
        """
        for node, adjacencies in enumerate(self.G.adjacency()):
            self.node_trace['marker']['color'] += tuple([len(adjacencies[1])])
            node_info = 'Name: ' + str(adjacencies[0]) + '<br># of neighboring nods: ' + str(len(adjacencies[1]))
            #self.node_trace['hovertext'] += tuple([node_info])
            self.node_trace['text'] += tuple([str(adjacencies[0])])


#=============================================================================


@app.callback(
    Output('selected-data', 'children'),
    [Input('Graph', 'selectedData')])
def display_selected_data(selected):

    print(selected)
    ctx = dash.callback_context
    print(ctx.inputs)

    if selected is not None:
        num_of_nodes = len(selected['points'])
        text = [html.P('Num of nodes selected: ' + str(num_of_nodes))]
        for x in selected['points']:
            print(x['text'])
            material = x['text'].split('<br>')[0][7:]
            text.append(html.P(str(material)))
        return text





if __name__ == '__main__':
    """
    The main of the tests file
    """

    # Class initiations
    tree = Tree()

    # Get sample data
    stock_prices = pd.read_csv('./dataset/stock_prices.csv', parse_dates=True, index_col='Date')
    stock_returns = stock_prices.pct_change()
    stock_returns.dropna(inplace=True)

    # get Correlation matrix
    corr_matrix = stock_returns.corr()

    # Build the Minimum Spanning Tree of the Correlation matrix as a networkx graph object
    mst = tree.build(corr_matrix)

    dash_graph = DashGraph(mst)
    dash_graph.run_dash()
    app.run_server()
