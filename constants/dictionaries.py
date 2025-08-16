activities = {
    'running': {'color': '#FF5733', 'label': 'Running'},         # Naranja rojizo
    'sitting': {'color': '#3498DB', 'label': 'Sitting'},         # Azul
    'jogging': {'color': '#F1C40F', 'label': 'Jogging'},         # Amarillo
    'walking': {'color': '#2ECC71', 'label': 'Walking'},         # Verde
    'standing': {'color': '#9B59B6', 'label': 'Standing'},       # Morado
    'lying down': {'color': '#E67E22', 'label': 'Lying down'},   # Naranja
    'going upstairs': {'color': '#1ABC9C', 'label': 'Going upstairs'},    # Turquesa
    'going downstairs': {'color': '#E74C3C', 'label': 'Going downstairs'}, # Rojo
    'unknown': {'color': '#327AE7', 'label': 'Unknown'}          # Azul
}

def activities_color(activity):    
    return activities[activity].get('color', '#000000')  # Default to black if activity not found