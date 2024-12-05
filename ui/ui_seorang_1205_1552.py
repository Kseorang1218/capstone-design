# main.py

from funs.utils import load_yaml
from funs.ShoeCabinetGUI import ShoeCabinetGUI
from funs.SerialComm import SerialComm  # SerialComm 클래스를 임포트

def main(config):
    # SerialComm 객체 생성 (시리얼 포트 설정)
    serial_comm = SerialComm(port='/dev/ttyACM0', baudrate=9600, timeout=1)
    
    # ShoeCabinetGUI 객체 생성 시 SerialComm 객체 전달
    app = ShoeCabinetGUI(config, serial_comm)
    app.run()

if __name__ == "__main__":
    # config.yaml에서 설정 파일 로드
    config = load_yaml('./config.yaml')
    main(config)
