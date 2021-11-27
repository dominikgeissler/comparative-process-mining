def dfg_dict_to_g6(dfg_dict):
    edges = []
    nodes = []
    dfg_graph_dict = dfg_dict['dfg_graph']
    unique_nodes = set()
    max_frequency = dfg_dict['properties']['max_frequency']
    min_frequency = dfg_dict['properties']['min_frequency']
    for startnode in dfg_graph_dict:
        edges_from_startnode = []
        unique_nodes.add(startnode)
        for endnode in dfg_graph_dict[startnode]:
            unique_nodes.add(endnode)
            frequency = dfg_graph_dict[startnode][endnode]
            edges_from_startnode.append(
                {
                    'source': startnode,
                    'target': endnode,
                    'label': frequency,
                    'style': {
                        'lineWidth': ((frequency - min_frequency) / (max_frequency - min_frequency)) * (18) + 2,
                        'endArrow': True
                    }
                }
            )
        edges.extend(edges_from_startnode)

    nodes = [
        {
            'id': node,
            'name': node,
            'isUnique': False,
            'conf': {
                'label': 'Name',
                'value': node,
            }


        }
        for node in unique_nodes
    ]
    return {
        'edges': edges,
        'nodes': nodes,
    }


def highlight_nonstandard_activities(g6_graph, reference):
    """
    Highlight non-standard activities in dfg/g6-graph
    """
    from logs.models import Log, LogObjectHandler
    import json
    from helpers.dfg_helper import convert_dfg_to_dict
    """
    The log that is chosen first on the manage side or first uploaded 
    will be the reference log for all comparisons
    """

    for node in g6_graph['nodes']:
        if find_node_in_g6(node['name'], reference):
            node['isUnique'] = 'False'
        else:
            node['isUnique'] = 'True'

    return g6_graph


def find_node_in_g6(node_name, reference):
    for node in reference['nodes']:
        if node['name'] == node_name:
            return True
    return False
