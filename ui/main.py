# main.py

from funs.utils import load_yaml
from funs.ShoeCabinetGUI import ShoeCabinetGUI
from funs.SerialComm import SerialComm 
from funs.UpdateHandler import UpdateHandler
from funs.CameraHandler import CameraHandler
from funs.ModelHandler import ModelHandler

def main(config):
    serial_comm = SerialComm(port='/dev/ttyACM0', baudrate=9600, timeout=1)
    camera_handler = CameraHandler(save_dir="./data")
    model_handler = ModelHandler(model_path="./model/model_1214_1830.tflite")
    data_updater = UpdateHandler(serial_comm, './figs/sneakers.png', model_handler, 'foo.csv')

    app = ShoeCabinetGUI(config, data_updater, serial_comm.ser, camera_handler, model_handler)
    app.run()

if __name__ == "__main__":
    # config.yaml에서 설정 파일 로드
    config = load_yaml('./config.yaml')
    main(config)
