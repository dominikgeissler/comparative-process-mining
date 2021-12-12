export const drawGraph =  (containerID, data)=>{
    const container = document.getElementById(containerID);
    const width = container.scrollWidth || 500;
    const height = container.scrollHeight || 500;

    function nodecolFunc(node) {
        if (node.isUnique === 'True')
            return  '#FF0000';
        return  '#C6E5FF';
    }
    
    const graph = new G6.Graph({
        container,
        width,
        height,
        layout: {
            type: 'dagre',
            ranksep: 70,
            controlPoints: true,
        },
        defaultNode: {
            type: 'sql',
        },
        defaultEdge: {
            type: 'polyline',
            style: {
                radius: 20,
                offset: 45,
                endArrow: true,
                lineWidth: 2,
                stroke: '#C2C8D5',
            },
            labelCfg: {
                style: {
                    fontSize: 25,
                    fontWeight: "bold"
                }
            },
        },
        nodeStateStyles: {
            selected: {
                stroke: '#d9d9d9',
                fill: '#5394ef',
            },
        },
        modes: {
            default: [
                'drag-canvas',
                'zoom-canvas',
                'click-select',
                'drag-node',
                {
                    type: 'tooltip',
                    formatText(model) {
                        const cfg = model.conf;
                        const text = [];
                        Array.prototype.forEach.call(cfg, (row) => {
                            text.push(row.label + ':' + row.value + '<br>')
                        })
                        return text.join('\n');
                    },
                    offset: 30,
                },
            ],
        },
        fitView: true,
    });

    G6.registerNode(
        'sql',
        {
            drawShape(cfg, group) {
                const rect = group.addShape('rect', {
                    attrs: {
                        x: -75,
                        y: -25,
                        width: 150,
                        height: 50,
                        radius: 10,
                        stroke: '#5B8FF9',
                        fill: nodecolFunc(cfg),
                        lineWidth: 3,
                    },
                    name: 'rect-shape',
                });
                if (cfg.name) {
                    group.addShape('text', {
                        attrs: {
                            text: cfg.name,
                            x: 0,
                            y: 0,
                            fill: '#00287E',
                            fontSize: 14,
                            textAlign: 'center',
                            textBaseline: 'middle',
                            fontWeight: 'bold',
                        },
                        name: 'text-shape',
                    });
                }
                return rect;
            },
        },
        'single-node',
    );
    // set image path in local storage
    graph.on('afterlayout', () => {
        graph.toFullDataURL(
            (res) => {
                localStorage.setItem('graph'+containerID,res);
            }
        )
    });
    graph.data(data);
    graph.render();
    if (typeof window !== 'undefined'){
        window.onresize = () => {
            if (!graph || graph.get('destroyed')) return;
            if (!container || !container.scrollWidth || !container.scrollHeight) return;
            graph.changeSize(container.scrollWidth, container.scrollHeight);
        };
    }
}
