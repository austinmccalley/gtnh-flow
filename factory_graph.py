# Standard libraries
import logging
import os
from pathlib import Path

# Pypi libraries
import yaml
from termcolor import colored, cprint

# Internal libraries
from src.data.loadMachines import recipesFromConfig
from src.graph._solver import systemOfEquationsSolverGraphGen

# Conditional imports based on OS
try: # Linux
    import readline
except Exception: # Windows
    import pyreadline3 as readline



class ProgramContext:


    def __init__(self):
        logging.basicConfig(level=logging.INFO)


    @staticmethod
    def cLog(msg, color='white', level=logging.DEBUG):
        # Not sure how to level based on a variable, so just if statements for now
        if level == logging.DEBUG:
            logging.debug(colored(msg, color))
        elif level == logging.INFO:
            logging.info(colored(msg, color))
        elif level == logging.WARNING:
            logging.warning(colored(msg, color))


    def run(self, graph_gen=None):
        if graph_gen == None:
            graph_gen = systemOfEquationsSolverGraphGen

        with open('config_factory_graph.yaml', 'r') as f:
            graph_config = yaml.safe_load(f)
        
        # Set up autcompletion config
        projects_path = Path('projects')
        readline.parse_and_bind('tab: complete')
        readline.set_completer_delims('')

        while True:
            def completer(text, state):
                prefix = ''
                suffix = text
                if '/' in text:
                    parts = text.split('/')
                    prefix = '/'.join(parts[:-1])
                    suffix = parts[-1]

                target_path = projects_path / prefix
                valid_tabcompletes = os.listdir(target_path)
                valid_completions = [x for x in valid_tabcompletes if x.startswith(suffix)]
                if state < len(valid_completions): # Only 1 match
                    completion = valid_completions[state]
                    if prefix != '':
                        completion = ''.join([prefix, '/', completion])
                    if not completion.endswith('.yaml'):
                        completion += '/'
                    return completion
                else:
                    return None

            readline.set_completer(completer)

            cprint('Please enter project path (example: "power/oil/light_fuel.yaml", tab autocomplete allowed)', 'blue')
            project_name = input(colored('> ', 'green'))
            if not project_name.endswith('.yaml'):
                # Assume when the user wrote "power/fish/methane", they meant "power/fish/methane.yaml"
                # This happens because autocomplete will not add .yaml if there are alternatives (like "power/fish/methane_no_biogas")
                project_name += '.yaml'

            recipes = recipesFromConfig(project_name)

            if project_name.endswith('.yaml'):
                project_name = project_name[:-5]

            graph_gen(self, project_name, recipes, graph_config)



if __name__ == '__main__':
    pc = ProgramContext()
    pc.run()