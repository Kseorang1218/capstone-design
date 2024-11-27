# main.py

from funs.utils import load_yaml
from funs.ShoeCabinetGUI import ShoeCabinetGUI

def main(config):
    app = ShoeCabinetGUI(config)
    app.run()


if __name__ == "__main__":
    config = load_yaml('./config.yaml')
    main(config)
