# UPPAAL Model Configuration and Verification Tool

This tool allows you to configure the layout and paths for a UPPAAL model and verify queries against the modified model. It provides a graphical user interface (GUI) to select positions and paths for various entities such as fire positions, civilians positions, first responders positions, exits positions, and drones.

## Features

- **Graphical Configuration**: Select positions for different entities and draw paths for drones using a graphical interface.
- **Model Modification**: Update the UPPAAL model with the selected positions and paths.
- **Verification**: Verify queries against the modified UPPAAL model.

## Prerequisites

- Python 3.x
- Tkinter library for Python (usually included with Python installations)
- pyuppaal library

## Installation

1. Install the required Python libraries:
    ```sh
    pip install pyuppaal
    ```

## Usage

1. **Configure Layout Positions**:
    ```sh
    cd scripts/
    python simulate.py --configure_layout
    ```
    You will be prompted to input the grid width and height. Then, you can select positions for different entities (fire, civilians, first responders, and exits) through the GUI.

2. **Configure Drones**:
    ```sh
    python simulate.py --configure_drones
    ```
    You can draw paths for drones on the grid through the GUI.

3. **Modify and Verify Model**:

    To verify the model with oonly one query, run:

    ```sh
    python simulate.py --verifyta_path /path/to/verifyta --model_file path_to_model.xml --modified_model_file modified_model.xml --parameters_file params1.cfg --query 'E<>(global <= Tscs and (rescued_civilians * 100 / CIVILIAN_NUMBER >= N))'
    ```
    However, it is possible to indicate a file containing multiple queries. Such queries will be ran concurrently on at most 10 threads if not specified otherwise. For instance:
    ```sh
    touch ../../queries.q
    echo 'E<>(global <= Tscs and (rescued_civilians * 100 / CIVILIAN_NUMBER >= N))' >> queries.q
    python simulate.py --verifyta_path /path/to/verifyta --model_file path_to_model.xml --modified_model_file modified_model.xml --parameters_file params1.cfg --multiple_queries --queries_file_path ../../queries.q --clean_traces=True
    ```
    In such cases, the argument `--clean_traces` is recommended as the verifier will produce a lot of traces in the temporary files directory of your system. Anyway, it defaults to `True`. 
    To specify the desired __maximum__ number of threads, use `-t` or `--threads`. The default value is 10.

    In addition, it's possible to automatically generate some queries using the script `build_queries.py` which will save them in the file `../../queries.q`. An example workflow would be:

    ```sh
    python build_queries.py
    python simulate.py --verifyta_path /path/to/verifyta --model_file path_to_model.xml --modified_model_file modified_model.xml --parameters_file params1.cfg --multiple_queries --queries_file_path ../../queries.q --clean_traces=True -t 4
    ```

### Command Line Arguments

- `--verifyta_path`: Path to the UPPAAL verifyta executable.
- `--model_file`: Path to the original UPPAAL model file.
- `--modified_model_file`: Path to save the modified UPPAAL model.
- `--parameters_file`: Path to the file with parameters to modify.
- `--query`: The query to verify on the modified model.
- `--configure_layout`: Open the GUI to configure layout positions.
- `--configure_drones`: Open the GUI to configure drones' paths and positions.

## Example

Configure layout positions:
```sh
python simulate.py --configure_layout
```
You will be prompted to enter the grid dimensions and then presented with a GUI to select the positions for fires, civilians, first responders, and exits.

Configure drones:
```sh
python simulate.py --configure_drones
```
You will be presented with a GUI to draw paths for the drones on the grid.

Modify the UPPAAL model with specified parameters and verify a query:
```sh
python simulate.py --verifyta_path /opt/uppaal/bin/verifyta --model_file ../../FM_HW.xml --modified_model_file modified_model.xml --parameters_file params1.cfg --query 'E<>(global <= Tscs and (rescued_civilians * 100 / CIVILIAN_NUMBER >= N))'

```
This command modifies the UPPAAL model based on the parameters in params1.cfg and verifies the specified query.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
