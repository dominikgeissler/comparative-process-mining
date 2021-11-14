def convert_dfg_to_dict(dfg):
    dfg_graph_dict = {}
    min_frequency = float('inf')
    max_frequency = 0
    for (startnode, endnote), frequency in dfg.items():
        if startnode not in dfg_graph_dict:
            dfg_graph_dict[startnode] = {}
        dfg_graph_dict[startnode][endnote] = frequency
        min_frequency = min(min_frequency, frequency)
        max_frequency = max(max_frequency, frequency)

    dfg_properties = {
        'min_frequency': min_frequency,
        'max_frequency': max_frequency,
    }
    return {
        'properties': dfg_properties,
        'dfg_graph': dfg_graph_dict
    }
