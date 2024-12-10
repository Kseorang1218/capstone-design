# main.py

from funs.utils import load_yaml
from funs.ShoeCabinetGUI import ShoeCabinetGUI
from funs.serial_conn import SerialComm 
from funs.data import UpdateData

def main(config):
    # SerialComm 객체 생성 (시리얼 포트 설정)
    serial_comm = SerialComm(port='/dev/ttyACM0', baudrate=9600, timeout=1)

    data_updater = UpdateData(serial_comm, './pictures/running_shoe.png')
    app = ShoeCabinetGUI(config, data_updater, serial_comm.ser)
    app.run()

if __name__ == "__main__":
    # config.yaml에서 설정 파일 로드
    config = load_yaml('./config.yaml')
    main(config)
