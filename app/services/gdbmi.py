def get_trace_step(gdb_controller, gdb_command):
    step = {'function': '', 'line': -1, 'stack_frames': [], 'heap': {}, 'stdout': ''}

    results = gdb_controller.write(gdb_command)
    if results[-1]['payload']['frame']['func'] == '__libc_start_call_main':
        return 'main_returned'
    
    stdout = next((res['payload'] for res in results if res['type'] == 'output'), '')
    
    step.update({'function': results[-1]['payload']['frame']['func'],
                 'line': results[-1]['payload']['frame']['line'],
                 'stdout': stdout})
    return step
