def get_trace_step(gdb_controller, gdb_command):
    step = {'function': '', 'line': -1, 'stack_frames': [], 'heap': {}, 'stdout': ''}

    results = gdb_controller.write(gdb_command)
    if results[-1]['payload'].get('frame') and results[-1]['payload']['frame']['func'] == '__libc_start_call_main':
        return 'main_returned'
    
    stdout = next((res['payload'] for res in results if res['type'] == 'output'), '')
    
    step.update({'function': results[-1]['payload']['frame']['func'],
                 'line': results[-1]['payload']['frame']['line'],
                 'stack_frames': get_stack_frames(gdb_controller=gdb_controller),
                 'stdout': stdout})
    return step

def get_stack_frames(gdb_controller):
    results = gdb_controller.write('-stack-list-frames')
    stack = results[0]['payload']['stack']
    
    stack_frames = []
    for frame in stack:
        stack_frame = {'function': frame['func'], 'local_variables': []}
        frame_level = frame['level']

        gdb_controller.write(f'-stack-select-frame {frame_level}')
        results = gdb_controller.write('-stack-list-variables --simple-values')

        local_variables = []
        local_vars = results[0]['payload']['variables']
        for var in local_vars:
            primitive_var = get_primitive_variable(gdb_controller=gdb_controller, primitive_variable=var)
            local_variables.append(primitive_var)

        stack_frame.update({'local_variables': local_variables})
        stack_frames.append(stack_frame)

    return stack_frames

def get_primitive_variable(gdb_controller, primitive_variable):
    var_name = primitive_variable['name']
    var_dtype = primitive_variable['type']
    var_value = primitive_variable['value']
    results = gdb_controller.write(f'-data-evaluate-expression &{var_name}')
    var_address = results[0]['payload']['value']

    return {'address': var_address, 'name': var_name, 'data_type': var_dtype, 'value': var_value}
