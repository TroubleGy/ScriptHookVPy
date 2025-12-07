import json

TYPE_MAP = {
    'void': 'Void',
    'int': 'int',
    'float': 'float',
    'bool': 'BOOL',
    'BOOL': 'BOOL',
    'char*': 'const char*',
    'const char*': 'const char*',
    'Hash': 'Hash',
    'Entity': 'Entity',
    'Player': 'Player',
    'Ped': 'Ped',
    'Vehicle': 'Vehicle',
    'Cam': 'Cam',
    'Object': 'Object',
    'Pickup': 'Pickup',
    'Blip': 'Blip',
    'Camera': 'Camera',
    'FireId': 'FireId',
    'Interior': 'Interior',
    'ScrHandle': 'ScrHandle',
    'Vector3': 'Vector3',
    'Any': 'Any',
    'Any*': 'Any*',
}

def map_type(json_type):
    json_type = json_type.strip()
    if json_type.endswith('*'):
        base = json_type[:-1].strip()
        return TYPE_MAP.get(base, base) + '*'
    return TYPE_MAP.get(json_type, json_type)

def get_invoke_type(return_type):
    if return_type == 'void':
        return 'Void'
    elif return_type == 'int':
        return 'int'
    elif return_type == 'float':
        return 'float'
    elif return_type == 'BOOL' or return_type == 'bool':
        return 'BOOL'
    elif return_type == 'Vector3':
        return 'Vector3'
    else:
        return return_type

def generate_natives_h(json_path, output_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write("#pragma once\n")
        out.write('#include "types.h"\n')
        out.write('#include "nativeCaller.h"\n\n')
        
        for namespace, functions in data.items():
            out.write(f"namespace {namespace}\n{{\n")
            
            for hash_key, func_data in functions.items():
                name = func_data['name']
                params = func_data.get('params', [])
                return_type = func_data.get('return_type', 'void')
                
                param_list = []
                param_names = []
                for param in params:
                    ptype = map_type(param['type'])
                    pname = param['name']
                    param_list.append(f"{ptype} {pname}")
                    param_names.append(pname)
                
                params_str = ', '.join(param_list)
                call_params = ', '.join(param_names)
                if call_params:
                    call_params = ', ' + call_params
                
                cpp_return_type = map_type(return_type)
                invoke_type = get_invoke_type(cpp_return_type)
                
                out.write(f"\tstatic {cpp_return_type} {name}({params_str}) {{ ")
                
                if return_type == 'void':
                    out.write(f"invoke<{invoke_type}>({hash_key}{call_params}); ")
                else:
                    out.write(f"return invoke<{invoke_type}>({hash_key}{call_params}); ")
                
                out.write("}\n")
            
            out.write("}\n\n")

if __name__ == "__main__":
    generate_natives_h('../natives.json', '../inc/natives.h')
    print("natives.h generated")