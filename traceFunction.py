import gdb
import os

def write_in_file(indent, content, output_file):
    output_file.write(indent*'\t' + content + '\n')

def process_result(result_list):
    for i in range(len(result_list)-1, -1, -1): # use reverse order！！
        # delete unvalid rows
        if (len(result_list[i]) <= 0 or result_list[i][0] != '#'):
            del result_list[i]

        if ('(' in result_list[i]):
            result_list[i] = result_list[i][: result_list[i].index('(')] 
        if (' in ' in result_list[i] and 'in seconds' not in result_list[i]):
            result_list[i] = result_list[i][result_list[i].index(' in ')+4:]
        else:
            result_list[i] = result_list[i][4:]

# set the global variable
output_file_name = 'output.txt'
function_to_trace = 'glXSwapBuffers'

gdb.execute('set breakpoint pending on')
gdb.execute('b '+function_to_trace)
gdb.execute('r')
# gdb.execute('set scheduler-locking step')

result = gdb.execute('bt', to_string = True)
result_list = result.split('\n')[0:-1]
process_result(result_list)
last_result_list = result_list

start_length = len(result_list)
start_frame = result_list[0]

# init output file 
if os.path.exists(output_file_name):
        os.remove(output_file_name)
output_file = open(output_file_name, 'w')
indent = 0
for frame in reversed(result_list):
    write_in_file(indent, frame, output_file)
    indent = indent + 1

# begin the loop of step
while (len(result_list)>= start_length and result_list[-start_length] == start_frame):
    gdb.execute('step')
    result = gdb.execute('bt', to_string = True)
    result_list = result.split('\n')[0:-1]
    process_result(result_list)

    if (len(result_list) > len(last_result_list)):
        write_in_file(indent, result_list[0], output_file)
    elif (len(result_list) == len(last_result_list)):
        indent = indent - 1
        if (result_list[0] != last_result_list[0]):
            write_in_file(indent, result_list[0], output_file)
    elif (len(result_list) < len(last_result_list)): 
        index_to_compare = len(last_result_list) - len(result_list)
        indent = indent - len(last_result_list) + len(result_list) - 1
        # indent = max(0, indent) #？
        if (result_list[0] != last_result_list[index_to_compare]):
            write_in_file(indent, result_list[0], output_file)
    
    indent = indent + 1
    last_result_list = result_list

output_file.close()
