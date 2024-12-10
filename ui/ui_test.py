# main.py

from funs.utils import load_yaml
from funs.ShoeCabinetGUI import ShoeCabinetGUI
from ui.funs.SerialComm import SerialComm 
from funs.Updater import UpdateData

def main(config):

    data_updater = UpdateData(None, './pictures/sneakers.png')
    app = ShoeCabinetGUI(config, data_updater, None)
    app.run()

if __name__ == "__main__":
    # config.yaml에서 설정 파일 로드
    config = load_yaml('./config.yaml')
    main(config)
