"""
File to create a map from scratch for the agents.
"""
import sys
import json

def main():
    """
    'g' is a goal location
    '#' is an obstacle
    '{team}{digit}' refers to agent{team}{digit}, where team must be uppercase.
    'b{digit}' refers to a block of type {digit}. 
        If an exclamation mark is in front of  the digit (e.g. '!b{digit}'), the block is attatched to an adjascent agent/block.
    'd{digit}' refers to a dispenser of type {digit}.

    A task can be created in the dictionary as follows:
    {'task_name': (duration, [(x1, y1, block), (x2, y2, block)])}
    Where the coordinates are relative to the agent.

    Taskboards refers to the number of taskboards in the game, these can only be generated at a random location.
    Steps refers to the amount of steps for the simulation.
    If fast_mode is set to false, extra agents are moved outside the map, this ensures that the game will not skip through the steps.
    """

    ######## CONFIG #########
    mapping = [
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', 'd0', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '#', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '#', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', 'A1', '.', '.', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '#', '.', '.', '.', '.', '.', '.', '.', '#', '#', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '#', '#', '#', '.', '#', '.', '.', '#', '#', '#', '#', '.', '.', '.', 'd1'],
        ['.', '.', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', 'g', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '#', '#', '#', '#', '.', '.', '.', '.', 'g', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '#', '#', '#', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '#', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.']
    ]

    tasks = {'task1': (100, [(1, 0, 'b0')]), 'task2': (200, [(0, 1, 'b1')])}
    taskboards = 1
    steps = 300
    fast_mode = False
    #########################

    # get the prefix of the tools directory
    tools_prefix = '/'.join(sys.argv[0].split('/')[:-1]) + '/'

    # get path to config, request it if it does not yet exist
    path_to_config = get_path_to_config(tools_prefix)

    config_name = "Custom.json"
    sim_name = "sim/simCustom.json"
    setup_name = "setup/custom.txt"
    
    # create the setup file
    setup_file = open(path_to_config + setup_name, "w")
    config = create_setup_file(mapping, tasks, setup_file)

    # get sample files
    sample_config = json.load(open(tools_prefix + 'sample/Custom.json'))
    sample_sim = json.load(open(tools_prefix + 'sample/simCustom.json'))

    # edit sample config
    sample_config["server"]["teamsPerMatch"] = len(config['teams'])
    sample_config["manual-mode"][0] = config['teams']
    sample_config["match"][0] = "$(" + sim_name + ")"
    for team in config['teams']:
        sample_config[team] = {"prefix" : "agent", "password" : "1"}

    # edit sample simulation
    if fast_mode:
        sample_sim["entities"]["standard"] = len(config["agent_ids"])
    else:
        n_agents = len(config["agent_ids"]) + 1
        sample_sim["entities"]["standard"] = n_agents
        for i, team in enumerate(config['teams']):
            setup_file.write(f"move {i} {len(mapping)} agent{team}{n_agents}")

    sample_sim["grid"]["height"] = len(mapping)
    sample_sim["grid"]["width"] = len(mapping[0])
    sample_sim["blockTypes"] = 2 * [len(config['blocks'])]
    sample_sim["setup"] = 'conf/' + setup_name
    sample_sim["steps"] = steps
    sample_sim["tasks"]["taskboards"] = taskboards

    # write results
    with open(path_to_config + config_name, "w") as f:
        json.dump(sample_config, f, indent=4)
    
    with open(path_to_config + sim_name, "w") as f:
        json.dump(sample_sim, f, indent=4)

    print(f"Environment created. Select {config_name} to play it.")


def get_adjacent(i, j):
    return [(i+1, j), (i, j+1), (i-1, j), (i, j-1)]

def create_setup_file(mapping, tasks, output_file):
    config = {'teams':[], 'agent_ids': [], 'blocks':[]}
    attach_queue = []
    for i in range(len(mapping[0])):
        for j in range(len(mapping)):
            element = mapping[j][i]
            if element[0].isupper():
                # add to config
                if element[0] not in config['teams']:
                    config['teams'].append(element[0])

                if element[1:] not in config['agent_ids']:
                    config['agent_ids'].append(element[1:])

                # move agent
                output_file.write(f"move {i} {j} agent{element}\n")
            elif element == '#':
                # create obstacle
                output_file.write(f"terrain {i} {j} obstacle\n")
            elif element == 'g':
                # create goal location
                output_file.write(f"terrain {i} {j} goal\n")
            elif element[0] == 'd':
                # add to config
                if element[1:] not in config['blocks']:
                    config['blocks'].append(element[1:])
                # create dispenser
                output_file.write(f"add {i} {j} dispenser b{element[1:]}\n")
            elif 'b' in element:
                # add to config
                if element[-1] not in config['blocks']:
                    config['blocks'].append(element[-1])
                # create block
                output_file.write(f"add {i} {j} block {element[-2:]}\n")
                if '!' in element:
                    for adj_i, adj_j in get_adjacent(i, j):
                        if mapping[adj_j][adj_i][0].isupper() or 'b' in mapping[adj_j][adj_i]:
                            attach_queue.append(f'attach {adj_i} {adj_j} {i} {j}\n')
    
    # create tasks
    for name, (duration, options) in tasks.items():
        # add blocks to shape
        task = f"create task {name} {duration} "
        for i, (rel_x, rel_y, block) in enumerate(options):
            # add to config
            if block[1:] not in config['blocks']:
                config['blocks'].append(block[1:])
            if i != 0:
                task += ';'
            task += f"{rel_x},{rel_y},{block}"

        # create task
        output_file.write(task + '\n')

    # add attachments
    output_file.writelines(attach_queue)

    return config

def get_path_to_config(tools_prefix):
    path_file = tools_prefix + 'path_to_config.txt'
    try:
        with open(path_file) as f:
            path_to_config = f.readline()
    except:
        path_to_config = input("Enter full path to the conf folder of the server\ni.e. path/to/massim_2020/server/conf\n").strip().replace('\\', '')
        with open(path_file, "w") as f:
            f.write(path_to_config)
        print("Path saved for future use")
    path_to_config = path_to_config
    if path_to_config[-1] != '/':
        return path_to_config + '/'
    return path_to_config


if __name__ == "__main__":
    main()