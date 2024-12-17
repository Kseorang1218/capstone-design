# main.py

from funs.utils import load_yaml
from funs.ShoeCabinetGUI import ShoeCabinetGUI
from funs.UpdateHandler import UpdateHandler
from funs.ModelHandler import ModelHandler

def main(config):
    model_handler = ModelHandler()
    data_updater = UpdateHandler(None, './figs/sneakers.png', model_handler)
    app = ShoeCabinetGUI(config, data_updater, None, None, None)
    app.run()

if __name__ == "__main__":
    # config.yaml에서 설정 파일 로드
    config = load_yaml('./config.yaml')
    main(config)
