import pyuppaal as pyu
from pyuppaal import UModel
import argparse
import logging
import time
import re
import os
import tkinter as tk
import platform
# Import tkmacosx for macOS
if platform.system() == 'Darwin':
    import tkmacosx as tkmac
import tempfile
import subprocess
import multiprocessing.dummy as mp
import shutil
import json

class GridPathApp:
    def __init__(self, master, grid_height, grid_width):
        """
        Initialize the GridPathApp.

        :param master: The tkinter master widget.
        :param grid_height: The height of the grid.
        :param grid_width: The width of the grid.
        """
        self.master = master
        self.master.title("Draw Drone Paths")
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
        self.paths = []
        self.current_path = []
        self.start_cell = None
        self.last_cell = None
        self.buttons = []

        self.create_grid()

        self.submit_button = self.create_button(master, text="Submit", command=self.submit)
        self.submit_button.grid(row=grid_height, column=0, columnspan=grid_width)

        self.result = None

    def create_grid(self):
        """Create the grid of buttons."""
        for i in range(self.grid_height):
            row = []
            for j in range(self.grid_width):
                btn = self.create_button(self.master, text='', width=30, height=30, command=lambda i=i, j=j: self.on_click(i, j))
                btn.grid(row=i, column=j)
                row.append(btn)
            self.buttons.append(row)

    def create_button(self, *args, **kwargs):
        """Create a button, using tkmacosx.Button on macOS and tk.Button otherwise."""
        if platform.system() == 'Darwin':
            kwargs['width'] = 30  # Width in pixels for tkmacosx.Button
            kwargs['height'] = 30  # Height in pixels for tkmacosx.Button
            return tkmac.Button(*args, **kwargs)
        else:
            kwargs['width'] = 3  # Width in text units for tk.Button
            kwargs['height'] = 1  # Height in text units for tk.Button
            return tk.Button(*args, **kwargs)

    def on_click(self, row, col):
        """
        Handle button click events.

        :param row: The row of the clicked cell.
        :param col: The column of the clicked cell.
        """
        if not self.is_contiguous((row, col)):
            return

        if not self.start_cell:
            self.start_cell = (row, col)
            self.buttons[row][col].configure(bg='red')
        else:
            self.buttons[row][col].configure(bg='blue')

        self.grid[row][col] = 1
        self.current_path.append((row, col))
        self.last_cell = (row, col)

        # Check if the current cell is the start cell to close the path
        if (row, col) == self.start_cell and len(self.current_path) > 1:
            self.new_path()

    def is_contiguous(self, cell):
        """
        Check if the cell is contiguous to the last cell in the current path.

        :param cell: The cell to check.
        :return: True if the cell is contiguous, False otherwise.
        """
        if not self.last_cell:
            return True
        row, col = cell
        last_row, last_col = self.last_cell
        if abs(row - last_row) + abs(col - last_col) == 1:
            return True
        return False

    def new_path(self):
        """Start a new path."""
        self.paths.append(self.current_path)
        self.current_path = []
        self.start_cell = None
        self.last_cell = None

    def submit(self):
        """Submit the current paths."""
        if self.current_path:
            self.new_path()  # Ensure the current path is checked and added if valid

        all_paths_directions = []
        for path in self.paths:
            directions = []
            for i in range(len(path) - 1):
                row1, col1 = path[i]
                row2, col2 = path[i + 1]
                if row2 == row1 and col2 == col1 + 1:
                    directions.append(('R', (row1, col1)))
                elif row2 == row1 and col2 == col1 - 1:
                    directions.append(('L', (row1, col1)))
                elif row2 == row1 + 1 and col2 == col1:
                    directions.append(('D', (row1, col1)))
                elif row2 == row1 - 1 and col2 == col1:
                    directions.append(('U', (row1, col1)))
            all_paths_directions.append(directions)

        self.result = all_paths_directions
        self.master.destroy()
        global drone_number 
        drone_number = len(self.paths)

def create_grid_and_get_paths(grid_height, grid_width):
    """
    Create the grid and get the paths drawn by the user.

    :param grid_height: The height of the grid.
    :param grid_width: The width of the grid.
    :return: The paths drawn by the user.
    """
    root = tk.Tk()
    app = GridPathApp(root, grid_height, grid_width)
    root.mainloop()
    return app.result

def on_click(i, j):
    """
    Handle click events on the grid buttons.

    :param i: The row of the clicked cell.
    :param j: The column of the clicked cell.
    """
    position = (i, j)
    if position in positions:
        positions.remove(position)
    else:
        positions.append(position)
    
    update_grid()
    print(f'Current selected positions: {positions}')

def update_grid():
    """Update the grid buttons based on the current selections."""
    for i in range(grid_height):
        for j in range(grid_width):
            btn = buttons[i][j]
            if (i, j) in positions:
                if current_phase == 'Fire Positions':
                    btn.config(bg='red')
                elif current_phase == 'Civilians Positions':
                    btn.config(bg='black')
                elif current_phase == 'First Responders Positions':
                    btn.config(bg='blue')
                elif current_phase == 'Exits Positions':
                    btn.config(bg='green')
            else:
                if (i, j) not in all_selected_positions:
                    btn.config(bg='lightgray')
                else:
                    btn.config(state='disabled', bg=color_map[(i, j)])

def create_grid(master):
    """
    Create the grid of buttons.

    :param master: The tkinter master widget.
    """
    for i in range(grid_height):
        row = []
        for j in range(grid_width):
            if (i, j) in all_selected_positions:
                btn = GridPathApp.create_button(master, text='', width=30, height=30, state='disabled', bg=color_map[(i, j)])
            elif current_phase == 'Exits Positions' and not (i == 0 or i == grid_height-1 or j == 0 or j == grid_width-1):
                btn = GridPathApp.create_button(master, text='', width=30, height=30, state='disabled', bg='lightgray')
            else:
                btn = GridPathApp.create_button(master, text='', width=30, height=30, command=lambda i=i, j=j: on_click(i, j))
            btn.grid(row=i, column=j)
            row.append(btn)
        buttons.append(row)

def save_coordinates():
    """Save the current coordinates to the global variable."""
    global saved_coordinates, all_selected_positions
    saved_coordinates.append(positions.copy())
    for pos in positions:
        all_selected_positions.add(pos)
        if current_phase == 'Fire Positions':
            color_map[pos] = 'red'
        elif current_phase == 'Civilians Positions':
            color_map[pos] = 'black'
        elif current_phase == 'First Responders Positions':
            color_map[pos] = 'blue'
        elif current_phase == 'Exits Positions':
            color_map[pos] = 'green'
    print(f"Coordinates saved to variable: {positions}")
    root.destroy()  # Close the window

def config_layout():
    """
    Configure the layout by selecting positions in different phases.

    :return: The positions of fire, civilians, first responders, and exits.
    """
    global positions, buttons, root, saved_coordinates, all_selected_positions, current_phase, color_map
    saved_coordinates = []  # Initialize the variable to save coordinates
    all_selected_positions = set()  # Set to keep track of all selected positions
    color_map = {}  # Map to track the color of each position

    phases = ['Fire Positions', 'Civilians Positions', 'First Responders Positions', 'Exits Positions']

    for phase in phases:
        current_phase = phase
        root = tk.Tk()
        root.title(f"Matrix Selector - {phase}")
        positions = []
        buttons = []

        create_grid(root)

        save_button = GridPathApp.create_button(root, text="Save Coordinates", command=save_coordinates)
        save_button.grid(row=grid_height, column=grid_width)

        root.mainloop()
    
    fire_positions, civilians_positions, first_responders_positions, exits_positions = saved_coordinates
    return fire_positions, civilians_positions, first_responders_positions, exits_positions

def update_layout_cfg_file(file_path, fire_positions, civilians_positions, first_responders_positions, exits_positions):
    """
    Update the layout configuration file with new positions.

    :param file_path: The path to the configuration file.
    :param fire_positions: List of fire positions.
    :param civilians_positions: List of civilians positions.
    :param first_responders_positions: List of first responders positions.
    :param exits_positions: List of exits positions.
    """
    with open(file_path, 'r') as f:
        content = f.read()

    # Define the new values
    fire_positions_str = ", ".join([f"{{{x[0]},{x[1]}}}" for x in fire_positions])
    exits_positions_str = ", ".join([f"{{{x[0]},{x[1]}}}" for x in exits_positions])
    first_responders_positions_str = ", ".join([f"{{{x[0]},{x[1]}}}" for x in first_responders_positions])
    civilians_positions_str = ", ".join([f"{{{x[0]},{x[1]}}}" for x in civilians_positions])

    content = re.sub(r'const int GRID_WIDTH = \d+;', f'const int GRID_WIDTH = {grid_width};', content)
    content = re.sub(r'const int GRID_HEIGHT = \d+;', f'const int GRID_HEIGHT = {grid_height};', content)
    content = re.sub(r'const int FIRE_NUM = \d+;', f'const int FIRE_NUM = {len(fire_positions)};', content)
    content = re.sub(r'const int EXIT_NUM = \d+;', f'const int EXIT_NUM = {len(exits_positions)};', content)
    content = re.sub(r'const int CIVILIAN_NUMBER = \d+;', f'const int CIVILIAN_NUMBER = {len(civilians_positions)};', content)
    content = re.sub(r'const int FIRST_RESPONDER_NUMBER = \d+;', f'const int FIRST_RESPONDER_NUMBER = {len(first_responders_positions)};', content)

    content = re.sub(r'position_t fires_positions\[.*?\] = \{.*?\};',
                     f'position_t fires_positions[FIRE_NUM] = {{ {fire_positions_str} }};', content, flags=re.DOTALL)
    content = re.sub(r'position_t exits_positions\[.*?\] = \{.*?\};',
                     f'position_t exits_positions[EXIT_NUM] = {{ {exits_positions_str} }};', content, flags=re.DOTALL)
    content = re.sub(r'position_t firstResponder_positions\[.*?\] = \{.*?\};',
                     f'position_t firstResponder_positions[FIRST_RESPONDER_NUMBER] = {{ {first_responders_positions_str} }};', content, flags=re.DOTALL)
    content = re.sub(r'position_t civilians_positions\[.*?\] = \{.*?\};',
                     f'position_t civilians_positions[CIVILIAN_NUMBER] = {{ {civilians_positions_str} }};', content, flags=re.DOTALL)
    Tfrs_s = '1,'*(len(first_responders_positions) - 1)+'1'
    content = re.sub(r'const int Tfrs\[.*?\] = \{.*?\};',
                     f'const int Tfrs[FIRST_RESPONDER_NUMBER] = {{{Tfrs_s}}};', content, flags=re.DOTALL)
    Tzr_s = '2,'*(len(civilians_positions) - 1)+'2'
    content = re.sub(r'const int Tzr\[.*?\] = \{.*?\};',
                     f'const int Tzr[CIVILIAN_NUMBER] = {{{Tzr_s}}};', content, flags=re.DOTALL)
    Tv_s = '5,'*(len(civilians_positions) - 1)+'5'
    content = re.sub(r'const int Tv\[.*?\] = \{.*?\};',
                     f'const int Tv[CIVILIAN_NUMBER] = {{{Tzr_s}}};', content, flags=re.DOTALL)

    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Configuration file {file_path} updated.")

def update_drones_cfg_file(file_path, drone_paths):
    """
    Update the drone configuration file with new paths and positions.

    :param file_path: The path to the configuration file.
    :param drone_paths: List of drone paths.
    """
    with open(file_path, 'r') as f:
        content = f.read()

    # Flatten the list of drone paths
    all_paths = [direction for path in drone_paths for direction in path]

    # Calculate the path length
    path_len = len(all_paths)

    # Convert paths to the required format
    drone_paths_str = ", ".join([f"{{{d[0]},{{{d[1][0]},{d[1][1]}}}}}" for d in all_paths])
    
    # Get initial positions of drones
    initial_positions = [path[0][1] for path in drone_paths]
    drone_positions_str = ", ".join([f"{{{pos[0]},{pos[1]}}}" for pos in initial_positions])

    # Update the content
    content = re.sub(r'const int DRONE_NUM = \d+;', f'const int DRONE_NUM = {len(drone_paths)};', content)
    content = re.sub(r'const int PATH_LEN = \d+;', f'const int PATH_LEN = {path_len};', content)
    content = re.sub(r'const direction_t drones_path\[.*?\] = \{.*?\};',
                     f'const direction_t drones_path[PATH_LEN] = {{{drone_paths_str}}};', content, flags=re.DOTALL)
    content = re.sub(r'const position_t drones_positions\[.*?\] = \{.*?\};',
                     f'const position_t drones_positions[DRONE_NUM] = {{{drone_positions_str}}};', content, flags=re.DOTALL)
    Nv = '2,'*(drone_number - 1)+'2'
    content = re.sub(r'const int Nv\[.*?\] = \{.*?\};',
                     f'const int Nv[DRONE_NUM] = {{{Nv}}};', content, flags=re.DOTALL)

    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Configuration file {file_path} updated.")

def set_verifyta_path(path):
    """
    Set the path to the UPPAAL verifyta executable.
    
    :param path: Path to the verifyta executable.
    """
    pyu.set_verifyta_path(path)

def modify_parameters(model_file, modified_model_file, parameters_str):
    """
    Modify parameters in the model and save the new model.
    
    :param model_file: Path to the original model file.
    :param modified_model_file: Path to save the modified model.
    :param parameters_str: String with parameters to modify, separated by newlines.
    """
    # Load the original model
    umodel = UModel(model_file)
    umodel.save_as(modified_model_file)
    # template_path = '../../uppaal/Templates/Model_Template.xml'
    # Load the modified model
    modified_umodel = UModel(modified_model_file)

    # Modify the parameters
    parameters = parameters_str.split('\n')

    '''values = {}
    json_path = '../../uppaal/Templates/PH_mapping.json'
    ph_mapping = json.load(open(json_path, 'r'))'''
    for param in parameters:
        if param.strip().startswith('//'):
            continue
        name, value = param.split('=')
        name = name.strip()
        value = value.strip().rstrip(';')
        modified_umodel.declaration = modified_umodel.declaration.replace(f'{name} =', f'{name} = {value};//', 1)        

    # Save the changes to the modified model
    modified_umodel.save()

def verify_query(modified_model_file, query):
    """
    Verify a query on the modified model.
    
    :param modified_model_file: Path to the modified model file.
    :param query: The query to verify.
    :return: The result of the verification.
    """
    # Load the modified model
    modified_umodel = UModel(modified_model_file)

    # Define the query
    modified_umodel.queries = [query]

    # Verify the query
    start_time = time.time()
    logging.info("Verification started.")
    result = modified_umodel.verify()
    end_time = time.time()

    logging.info("Verification completed.")
    logging.info(f"Time taken: {end_time - start_time} seconds")
    
    # For each line in the output result, take only those beginning with 'Formula'
    # result = '\n'.join([line for line in result.split('\n') if line.startswith('Formula')])
    return result

def read_parameters_from_file(file_path):
    """
    Read parameters from a configuration file.
    
    :param file_path: Path to the configuration file.
    :return: A string with parameters to modify, separated by newlines.
    """
    with open(file_path, 'r') as file:
        parameters_str = file.read()
    return parameters_str

def main():
    global grid_width, grid_height, drone_number,fr_number,civ_number;
    NUM_THREADS = 10
    grid_width = 10
    grid_height = 10
    drone_number = 4
    fr_number = 3
    civ_number = 6
    # Depeding on the OS
    #default_verifyta_path = '/Applications/UPPAAL-5.0.0.app/Contents/Resources/uppaal/bin/verifyta' if platform.system() == "Darwin" else '/opt/uppaal/bin/verifyta'
    #default_verifyta_path =  '/opt/uppaal/bin/verifyta'
    default_verifyta_path =  '/home/due2/Desktop/FormalMethods/sources/scripts2/uppaal/bin/verifyta'
    # Add arguments
    parser = argparse.ArgumentParser(description='Modify UPPAAL model parameters and verify a query.')
    parser.add_argument('--verifyta_path', type=str, default=default_verifyta_path, help='Path to the UPPAAL verifyta executable')
    parser.add_argument('--model_file', type=str, default='../../FM_HW.xml', help='Path to the original model file')
    parser.add_argument('--modified_model_file', type=str, default='modified_model.xml', help='Path to save the modified model')
    parser.add_argument('--parameters_file', type=str, default='params1.cfg', help='Path to the file with parameters to modify')
    parser.add_argument('--query', type=str, default='E<>(global <= Tscs and (rescued_civilians * 100 / CIVILIAN_NUMBER >= N))', help='The query to verify on the modified model')
    parser.add_argument('--configure_layout', action='store_true', help='Configure layout positions')
    parser.add_argument('--configure_drones', action='store_true', help='Configure drones number, path and positions')
    parser.add_argument('--multiple_queries', action='store_true', help='Verify multiple queries')
    parser.add_argument('--queries_file_path', type=str, default='../../queries.q', help='Path to the file with queries to verify')
    parser.add_argument('--clean_traces', type=bool, default=True, help='Delete traces files')
    parser.add_argument('-t', '--threads', type=int, default=NUM_THREADS, help='Define maximum number of threads')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


    if args.configure_layout:
        args.parameters_file = 'params_tmp.cfg'
        grid_width = int(input("Insert the grid width: "))
        grid_height = int(input("Insert the grid height: "))
        fire_positions, civilians_positions, first_responders_positions, exits_positions = config_layout()
        logging.info(f"Fire positions: {fire_positions}")
        logging.info(f"Civilians positions: {civilians_positions}")
        logging.info(f"First responders positions: {first_responders_positions}")
        logging.info(f"Exits positions: {exits_positions}")
        update_layout_cfg_file('params_tmp.cfg', fire_positions, civilians_positions, first_responders_positions, exits_positions)
        fr_number = len(first_responders_positions)
        civ_number = len(civilians_positions)
    if args.configure_drones:
        args.parameters_file = 'params_tmp.cfg'
        # look for the grid size in the file
        with open('params_tmp.cfg', 'r') as f:
            content = f.read()
        grid_width = int(re.search(r'const int GRID_WIDTH = (\d+);', content).group(1))
        grid_height = int(re.search(r'const int GRID_HEIGHT = (\d+);', content).group(1))
        print(f'Grid size: {grid_width}x{grid_height}')
        drones_paths = create_grid_and_get_paths(grid_height, grid_width)
        print(drones_paths)
        update_drones_cfg_file('params_tmp.cfg', drones_paths)
        

    set_verifyta_path(args.verifyta_path)
    parameters_str = read_parameters_from_file(args.parameters_file)
    modify_parameters(args.model_file, args.modified_model_file, parameters_str)

    if args.multiple_queries:
        queries = []
        temp_files = []
        with open(args.queries_file_path, 'r') as file:
            queries = file.readlines()
            results_output_directory_path = './Results/'
        os.makedirs(results_output_directory_path, exist_ok=True)
        with open(os.path.join(results_output_directory_path, 'results.csv'), 'w') as f:
            f.write('Query, Result\n')
        for query in queries:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name
            temp_file_path_with_extension = temp_file_path + '.xml'
            os.rename(temp_file_path, temp_file_path_with_extension)
            shutil.copyfile(args.modified_model_file, temp_file_path_with_extension)
            temp_files.append(temp_file_path_with_extension)
        with mp.Pool(min(NUM_THREADS, len(queries))) as pool:
            results = pool.starmap(verify_query, zip(temp_files, queries))
        for i, query in enumerate(queries):
            results[i] = results[i].split('\n')
            results[i] = [line for line in results[i] if 'satisfied' in line.lower()]
            results[i] = ['Not Satisfied' if 'not' in line.lower() else 'Satisfied' for line in results[i]]
            results[i] = '\n'.join(results[i])
            formatted_query = query.replace('\n', '')
            print(f'Query: {formatted_query}, Result: {results[i]}')
            with open(os.path.join(results_output_directory_path, 'results.csv'), 'a') as f:
                f.write(f'{formatted_query}, {results[i]}\n')
        for temp_file in temp_files:
            xml_path = temp_file
            if temp_file.endswith('.xml'):
                xtr_path = temp_file.replace('.xml', '_xtr-1')
            else:
                xtr_path = temp_file + '_xtr-1'
            if os.path.exists(xml_path):
                os.remove(xml_path)
            if args.clean_traces and os.path.exists(xtr_path):
                os.remove(xtr_path)
    else:
        result = verify_query(args.modified_model_file, args.query)
        print(f'Query: {args.query}, Result: {result}')


if __name__ == '__main__':
    main()
