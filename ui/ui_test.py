# main.py

from funs.utils import load_yaml
from funs.ShoeCabinetGUI import ShoeCabinetGUI
from funs.UpdateHandler import UpdateHandler

def main(config):

    data_updater = UpdateHandler(None, './figs/sneakers.png')
    app = ShoeCabinetGUI(config, data_updater, None)
    app.run()

if __name__ == "__main__":
    # config.yaml에서 설정 파일 로드
    config = load_yaml('./config.yaml')
    main(config)
