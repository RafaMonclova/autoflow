def flatten_json(nested_json, parent_key='', sep='.'):
    """
    Aplana un diccionario o lista separando las claves con un separador (por defecto '.').
    Extrae un solo schema genérico usando [*] para las listas.
    """
    items = []
    
    if isinstance(nested_json, dict):
        for k, v in nested_json.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            items.extend(flatten_json(v, new_key, sep=sep).items())
    elif isinstance(nested_json, list):
        if len(nested_json) > 0:
            # Generamos la ruta genérica con el comodín de iteración [*]
            # Solo iteramos el schema del primer elemento
            new_key = f"{parent_key}.[*]" if parent_key else "[*]"
            
            # En caso de que la API devuelva una lista de strings [ "a", "b" ]
            if not isinstance(nested_json[0], (dict, list)):
                items.append((new_key, nested_json[0]))
            else:
                items.extend(flatten_json(nested_json[0], new_key, sep=sep).items())
    else:
        if parent_key:
            items.append((parent_key, nested_json))
            
    return dict(items)
