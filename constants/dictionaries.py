def activities_color(activity):
    colors = {
    'running': '#FF5733',         # Naranja rojizo
    'sitting': '#3498DB',         # Azul
    'jogging': '#F1C40F',         # Amarillo
    'walking': '#2ECC71',         # Verde
    'standing': '#9B59B6',        # Morado
    'lying down': '#E67E22',      # Naranja
    'going upstairs': '#1ABC9C',  # Turquesa
    'going downstairs': '#E74C3C', # Rojo
    'unknown': "#327AE7" # Rojo
    }
    return colors[activity]