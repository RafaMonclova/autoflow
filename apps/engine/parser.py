import re

def get_nested_value(d, path, default=""):
    """
    Navega de forma segura por un diccionario anidado utilizando una ruta de strings.
    Soporta índices numéricos en listas. Ej: path="users.0.name"
    """
    keys = path.split('.')
    val = d
    for key in keys:
        if isinstance(val, dict) and key in val:
            val = val[key]
        elif isinstance(val, list) and key.isdigit():
            idx = int(key)
            if 0 <= idx < len(val):
                val = val[idx]
            else:
                return default
        else:
            return default
    return val

def parse_template_with_payload(template_data, payload_dict):
    """
    Recibe un template_string, diccionario o lista y un payload_dict.
    Busca de forma recursiva todas las ocurrencias de {{ruta.al.dato}} 
    y las reemplaza navegando por el diccionario payload_dict.
    Si la variable no existe en el JSON, se reemplaza por cadena vacía por defecto.
    """
    
    # Si es un string, buscamos las etiquetas {{ }}
    if isinstance(template_data, str):
        # Patrón que busca {{variable.anidada}} soportando corchetes y asteriscos
        pattern = re.compile(r'\{\{([\w\.\[\]\*]+)\}\}')
        
        def replace_match(match):
            path = match.group(1)
            # Reemplazar con el valor extraído o cadena vacía si no existe
            return str(get_nested_value(payload_dict, path))
            
        return pattern.sub(replace_match, template_data)
        
    # Si es un diccionario (ej. config_template), iterar recursivamente
    elif isinstance(template_data, dict):
        result = {}
        for key, value in template_data.items():
            result[key] = parse_template_with_payload(value, payload_dict)
        return result
        
    # Si es una lista, iterar recursivamente
    elif isinstance(template_data, list):
        return [parse_template_with_payload(item, payload_dict) for item in template_data]
        
    # Otros tipos de datos se devuelven intactos
    return template_data

def extract_wildcard_path(template_data):
    """
    Busca recursivamente dentro de plantillas si hay un iterador [*].
    Devuelve la ruta base de la lista a iterar.
    Ej: 'step1.usuarios' de la variable '{{step1.usuarios.[*].email}}'
    """
    if isinstance(template_data, str):
        pattern = re.compile(r'\{\{([\w\.]+\.\[\*\][\w\.]*)\}\}')
        match = pattern.search(template_data)
        if match:
            full_path = match.group(1)
            base_path = full_path.split('.[*]')[0]
            return base_path
            
    elif isinstance(template_data, dict):
        for value in template_data.values():
            found = extract_wildcard_path(value)
            if found:
                return found
                
    elif isinstance(template_data, list):
        for item in template_data:
            found = extract_wildcard_path(item)
            if found:
                return found
                
    return None

def replace_wildcard_with_index(template_data, index):
    """
    Reemplaza todas las apariciones de '[*]' por el índice proporcionado.
    Ej: '{{step1.[*].name}}' -> '{{step1.0.name}}'
    """
    if isinstance(template_data, str):
        pattern = re.compile(r'\{\{([\w\.]+)\.\[\*\]([\w\.]*)\}\}')
        def replace_match(m):
            base = m.group(1)
            resto = m.group(2)
            if resto:
                return f"{{{{{base}.{index}{resto}}}}}"
            return f"{{{{{base}.{index}}}}}"
        return pattern.sub(replace_match, template_data)
        
    elif isinstance(template_data, dict):
        result = {}
        for key, value in template_data.items():
            result[key] = replace_wildcard_with_index(value, index)
        return result
        
    elif isinstance(template_data, list):
        return [replace_wildcard_with_index(item, index) for item in template_data]
        
    return template_data
