import json

def generate_bindings(json_path, output_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write('#include <pybind11/pybind11.h>\n')
        out.write('#include <pybind11/embed.h>\n')
        out.write('#include <pybind11/stl.h>\n')
        out.write('#include "../inc/natives.h"\n\n')
        out.write('namespace py = pybind11;\n\n')
        
        out.write('PYBIND11_EMBEDDED_MODULE(natives, m) {\n')
        
        for namespace, functions in data.items():
            out.write(f'    py::module_ {namespace.lower()} = m.def_submodule("{namespace}");\n')
            
            for hash_key, func_data in functions.items():
                name = func_data['name']
                params = func_data.get('params', [])
                
                param_types = []
                param_names = []
                for param in params:
                    param_types.append(param['type'])
                    param_names.append(param['name'])
                
                lambda_params = ', '.join([f'{ptype} {pname}' for ptype, pname in zip(param_types, param_names)])
                call_params = ', '.join(param_names)
                
                if params:
                    out.write(f'    {namespace.lower()}.def("{name}", []({lambda_params}) {{ ')
                else:
                    out.write(f'    {namespace.lower()}.def("{name}", []() {{ ')
                
                if func_data.get('return_type', 'void') == 'void':
                    out.write(f'{namespace}::{name}({call_params}); ')
                else:
                    out.write(f'return {namespace}::{name}({call_params}); ')
                
                out.write('});\n')
            
            out.write('\n')
        
        out.write('}\n')

if __name__ == "__main__":
    generate_bindings('../natives.json', '../src/bindings.cpp')
    print("bindings.cpp generated")