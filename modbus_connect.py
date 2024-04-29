import os
import serial
import time
from pyModbusTCP.client import ModbusClient
from dotenv import load_dotenv
from shared_memory_dict import SharedMemoryDict

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
port1 = os.getenv("port1")
baudrate1 = os.getenv("baudrate1")
timeout1 = os.getenv("timeout1")

host2 = os.getenv("host2")
port2 = os.getenv("port2")
unit_id2 = os.getenv("unit_id2")
auto_open2 = os.getenv("auto_open2")



# Create a serial object
ser_sensor = serial.Serial(port1, baudrate1, timeout=timeout1)
#ser_sensor = serial.Serial(port=port1, baudrate=baudrate1, bytesize=8, parity='N', stopbits=2, timeout=timeout1, xonxoff=0, rtscts=0)
tcp_modbus = ModbusClient(host=host2, port=port2, unit_id=unit_id2, auto_open=auto_open2)

tsensor_pipe = SharedMemoryDict(name='temperatures', size=4096)


def turn_off_alarm():
    global alarm_on

    if tsensor_pipe["modo"] == 'desligado' :
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 


        # Writing data to the TCP port

        data_received_mod = tcp_modbus.write_single_register(500, 0)    #Desliga alarme
        alarm_on = False
        tsensor_pipe["estado"] = False
        print(f"[{timestamp}] Turning off Alarm - Data written: (500, 0)")
        # Reading data from the RS485 port
        #print_erro("Desligando Alarme")
        print(f"Data received from Modbus: {data_received_mod}")
        return

def turn_on_alarm():
    global alarm_on
    #if check_Alarme() :
    #    return

    if tsensor_pipe["modo"] == 'auto' :
        if check_GA():
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

            # Writing data to the TCP port

            data_received_mod = tcp_modbus.write_single_register(500, 1)    #Liga alarme


            print(f"[{timestamp}] Turning alarm on - Data written: (500, 1)")
            #print_erro("Ligando Alarme")

            print(f"Data received from Modbus: {data_received_mod}")
            alarm_on = True
            tsensor_pipe["estado"] = True
            return
        else:
            print("Erro - Alarme não foi acionado - GA Desligado")
            #print_erro("Erro - Alarme não foi acionado - GA Desligado")
            #alarm_on = False
            #tsensor_pipe["estado"] = False
            return
    elif tsensor_pipe["modo"] == 'ligado' :
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

        # Writing data to the TCP port

        data_received_mod = tcp_modbus.write_single_register(500, 1)    #Liga alarme


        print(f"[{timestamp}] Turning alarm on - Data written: (500, 1)")
        #print_erro("Ligando Alarme")

        print(f"Data received from Modbus: {data_received_mod}")
        alarm_on = True
        tsensor_pipe["estado"] = True
        return

def check_GA():
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 
    # Reading data to the TCP port
    data_received_mod = tcp_modbus.read_holding_registers(70, 1)

    print(f"[{timestamp}] Checking if GA is ON - Data written: (70, 1)")
    # Reading data from the RS485 port
        
    print(f"Data received from Modbus: {data_received_mod}")
    if data_received_mod == [1] :
        print(f"[{timestamp}] GA is ON")
        tsensor_pipe["estado_ga"] = True
        return True
    else:
        print(f"[{timestamp}] GA is OFF")
        tsensor_pipe["estado_ga"] = False
        return False        


def check_Alarme():
    global alarm_on
    # Reading data to the TCP port
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 
    data_received_mod = tcp_modbus.read_holding_registers(500, 1)

    print(f"[{timestamp}] Checking if Alarme is ON - Data written: (500, 1)")
    # Reading data from the RS485 port
        
    print(f"Data received from Modbus: {data_received_mod}")

    if data_received_mod == [1] :
        alarm_on = True
        tsensor_pipe["estado"] = True
    else:
        alarm_on = False
        tsensor_pipe["estado"] = False

    print(f"[{timestamp}] Alarme is {alarm_on}")

    return alarm_on


def reiniciar_haste():
    
    data_received_mod = tcp_modbus.write_single_register(502, 1)    #Desliga haste
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    print(f"[{timestamp}] Desligando a haste - Data written: (502, 1)")
    
    print(f"Data received from Modbus: {data_received_mod}")
    time.sleep(0.1)

    data_received_mod = tcp_modbus.write_single_register(502, 0)    #Liga haste
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    print(f"[{timestamp}] Religando a haste - Data written: (502, 0)")
    
    print(f"Data received from Modbus: {data_received_mod}")
    time.sleep(0.1)
    return

def inicializa_haste():
    for x in range(2):
        read_count = 0
        for i in range(16):

            controller_ID = "%0.2X" % (i+1)
            #if controller_ID == "10" :
            #    controller_ID = "15"
            hex_data_to_write = "64" + controller_ID
            data_to_write = bytes.fromhex(hex_data_to_write)

            ser_sensor.write(data_to_write)
            data_received = ser_sensor.read(12).hex()
            #data_received = '21650892080a' ### remover linha - uso apenas em testes
            if ((data_received[:4] == "2165") and (len(data_received) == 12)):
                read_count += 1
            time.sleep(0.1)

        if read_count != 16 :
            print(f"Haste inicializada com {read_count}/16 controladores, reiniciando haste.")
            #print_erro("Erro ao inicializar haste")
            reiniciar_haste()
        else:
            print("Haste inicializada")
            #print_erro("Haste inicializada")
            return
    print("Haste inicializada porém com sensores faltando")



def read_controller(i):
    controller_ID = "%0.2X" % (i+1)
    #if controller_ID == "10" :
    #    controller_ID = "15"
    # Writing data to the RS485 port
    # Hex data to write
    hex_data_to_write = "64" + controller_ID
    # Convert hex string to bytes
    data_to_write = bytes.fromhex(hex_data_to_write)

    # Writing data to the RS485 port
    ser_sensor.write(data_to_write)
    #print(f"[{timestamp}] Data written: {hex_data_to_write}")

    # Reading data from the RS485 port
    data_received = ser_sensor.read(12).hex()
    # data_received = ser_sensor.read_until(expected=b"\xFF", size=12) #.strip().hex()
    #data_received = data_received.hex()
    #data_received = '21650892080a' ### remover linha - uso apenas em testes

    print(f"[{timestamp}] Data written: {hex_data_to_write} Data received: {data_received}")
    #time.sleep(5)
    return data_received