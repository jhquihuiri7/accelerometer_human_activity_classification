def plot_legend_boxes():
    from dash import html
    from constants.dictionaries import activities
    legend_boxes = []
    for _, props in activities.items():
        box = html.Div(
            children=[html.Span(props.get('label', 'Unknown'), className="text-[12px]")],
            className=f"flex items-center bg-[{props.get('color', '#000000')}] px-2 py-1 rounded",
        )
        legend_boxes.append(box)
    return html.Div(
        children=legend_boxes,
        className="flex flex-wrap gap-1 justify-center"
    )

