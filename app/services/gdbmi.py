import re

POINTER_REGEX = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*\*+$')

def get_trace_step(gdb_controller, gdb_command):
    step = {'function': '', 'line': -1, 'stack_frames': [], 'heap': {}, 'stdout': ''}

    results = gdb_controller.write(gdb_command)
    if results[-1]['payload'].get('frame') and results[-1]['payload']['frame']['func'] == '__libc_start_call_main':
        return 'main_returned'
    
    stdout = next((res['payload'] for res in results if res['type'] == 'output'), '')
    
    heap = {}
    stack_frames = []
    update_program_state(gdb_controller=gdb_controller, stack_frames=stack_frames, heap=heap)

    step.update({'function': results[-1]['payload']['frame']['func'],
                 'line': results[-1]['payload']['frame']['line'],
                 'stack_frames': stack_frames,
                 'heap': heap,
                 'stdout': stdout})
    return step

def update_program_state(gdb_controller, stack_frames, heap):
    results = gdb_controller.write('-stack-list-frames')
    stack = results[0]['payload']['stack']

    for frame in stack:
        stack_frame = {'function': frame['func'], 'local_variables': []}
        frame_level = frame['level']

        gdb_controller.write(f'-stack-select-frame {frame_level}')
        results = gdb_controller.write('-stack-list-variables --simple-values')

        local_variables = []
        local_vars = results[0]['payload']['variables']
        for var in local_vars:
            primitive_var = get_primitive_variable(gdb_controller=gdb_controller, primitive_variable=var)

            if POINTER_REGEX.match(var['type']):
                update_heap(gdb_controller=gdb_controller, heap=heap, var=var)

            local_variables.append(primitive_var)
        
        stack_frame.update({'local_variables': local_variables})
        stack_frames.append(stack_frame)

def get_primitive_variable(gdb_controller, primitive_variable):
    var_name = primitive_variable['name']
    var_dtype = primitive_variable['type']
    var_value = primitive_variable['value'].split(' ')[0]
    results = gdb_controller.write(f'-data-evaluate-expression &{var_name}')
    var_address = results[0]['payload']['value']

    return {'address': var_address.split(' ')[0], 
            'name': var_name, 
            'data_type': var_dtype, 
            'value': chr(int(var_value)) if var_dtype == 'char' else var_value}

def update_heap(gdb_controller, heap, var):
    var_name = var['name']
    var_dtype = var['type'].split(' ')[0]
    var_value = var['value'].split(' ')[0]
    results = gdb_controller.write(f'-data-evaluate-expression *({var_name})')
    value = results[0]['payload']['value']
    heap.update({var_value: [var_dtype, 
                             chr(int(value.split(' ')[0])) if var_dtype == 'char' else var_value]})
