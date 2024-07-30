import serial
import time
import csv
import os
import ast
import numpy as np
from shared_memory_dict import SharedMemoryDict
from pyModbusTCP.client import ModbusClient
from dotenv import load_dotenv, set_key, find_dotenv

try:
    # Load variables from the .env file
    load_dotenv(override=True)

    # Serial port settings for communicating with sensors
    port_serial = os.getenv('port_serial',default='/dev/ttyS1')   #'/dev/ttyS1'  #'COM5'       # Replace with the actual port on your system
    baudrate_serial = int(os.getenv('baudrate_serial',default='19200'))    # Use 19200 
    timeout_serial = float(os.getenv('timeout1',default='0.04'))

    # Serial port settings for communicating with Modbus
    host_tcp = os.getenv('host_tcp',default='192.168.15.130')
    port_tcp = int(os.getenv('port_tcp',default='502'))
    unit_id_tcp = int(os.getenv('unit_id_tcp',default='1'))
    auto_open_tcp = (os.getenv('auto_open_tcp',default='True')=='True')

    CONST_READ_DELAY = 60
    read_time = int(os.getenv('read_time',default='1000'))

    env_line = os.getenv("upper_limit")
    # Convert the string representation of list to a Python list
    float_list = ast.literal_eval(env_line)
    # Convert the integers to floats
    upper_limit = [float(x) for x in float_list]     # limite superior de temperatura. O valor deve ser superior para iniciar contagem. Por exemplo, se limite é 7.0, o alarme vai acionar quando alcançar 7º acima da média

    env_line = os.getenv("lower_limit")
    # Convert the string representation of list to a Python list
    float_list = ast.literal_eval(env_line)
    # Convert the integers to floats
    lower_limit = [float(x) for x in float_list]     # limite inferior de temperatura. O valor deve ser inferior para iniciar contagem. Por exemplo, se limite é 7.0, o alarme vai acionar quando alcançar 7º abaixo da média



    env_line = os.getenv("upper_limit_start")
    # Convert the string representation of list to a Python list
    upper_limit_start = [10.0 for x in range(33)]
    if env_line == None :
        set_key(find_dotenv(), 'upper_limit_start', str(upper_limit_start))   #salva estado do alarme no '.env'
    else :        
        float_list = ast.literal_eval(env_line)
        # Convert the integers to floats
        upper_limit_start = [float(x) for x in float_list]     # limite superior de temperatura no modo partida. O valor deve ser superior para iniciar contagem. Por exemplo, se limite é 7.0, o alarme vai acionar quando alcançar 7º abaixo da média

    env_line = os.getenv("lower_limit_start")
    # Convert the string representation of list to a Python list
    lower_limit_start = [10.0 for x in range(33)]
    if env_line == None :
        set_key(find_dotenv(), 'lower_limit_start', str(lower_limit_start))   #salva estado do alarme no '.env'
    else :        
        float_list = ast.literal_eval(env_line)
        # Convert the integers to floats
        lower_limit_start = [float(x) for x in float_list]     # limite inferior de temperatura  no modo partida. O valor deve ser inferior para iniciar contagem. Por exemplo, se limite é 7.0, o alarme vai acionar quando alcançar 7º abaixo da média


    consecutive_limit = int(os.getenv('consecutive_limit',default='7'))     # limite de medidas acima da temperatura para acionar alarme. Por exemplo se limite é 5, o alarme vai acionar quando for realizada a 6 leitura consecutiva acima ou abaixo do limite
    general_limit = (os.getenv('general_limit',default='True')=='True')

    env_line = os.getenv("enabled_sensor")
    enabled_sensor = [True for x in range(32)]
    if env_line == None :
        set_key(find_dotenv(), 'enabled_sensor', str(enabled_sensor))   #salva estado do alarme no '.env'
    else :
        # Convert the string representation of list to a Python list
        enabled_sensor = ast.literal_eval(env_line)

    env_line = os.getenv("calibracao")
    float_list = [0.0 for x in range(32)]
    if env_line == None :
        set_key(find_dotenv(), 'calibracao', str(float_list))   #salva calibração dos sensores no '.env'
    else :
        # Convert the string representation of list to a Python list
        float_list = ast.literal_eval(env_line)
    calibracao = [float(x) for x in float_list] 


    debug_mode = (os.getenv('debug_mode',default='False')=='True')
    verbose = int(os.getenv('verbose',default='0'))

    modo = os.getenv('modo',default="auto")

    alarm_on = (os.getenv('alarm_on',default='True')=='True')

    outlier_temp = float(os.getenv('outlier_temp',default='150.0'))

    pre_alarme_timeout = int(os.getenv('pre_alarme_timeout',default='600')) # tempo que dura o alarme de partida
    pre_alarme_init = (os.getenv('pre_alarme_init',default='False')=='True') # se igual a False, desabilita o alarme de partida

    repeat_lost = (os.getenv('repeat_lost',default='True')=='True') # tempo que dura a inicialização do pré-alarme, se igual a 0, desabilita o pré-alarme
    repeat_lost_over = False # variável que controla se filtro repete anterior já ficou ligado por mais de 5 min (count_error_limit)

    count_error_limit = int(os.getenv('count_error_limit',default='300')) # tempo em segundos entre tentativas de reinicialização da haste em caso de falha de leitura

except:
    print("Erro ao carregar variáveis de ambiente")
    
current_hour = 0
current_hour_alarm = 0
count_reboot = 0
connection = ""
GA_state = False

# Create a serial object
if not debug_mode:
    ser_sensor = serial.Serial(port_serial, baudrate_serial, timeout=timeout_serial)
    tcp_modbus = ModbusClient(host=host_tcp, port=port_tcp, unit_id=unit_id_tcp, auto_open=auto_open_tcp)


# Open a CSV file for writing temp
current_datetime = time.strftime("%Y%m%d_%H%M%S")
csv_file_path_temp = f'./output/output_temp_{current_datetime}.csv'
csv_file_path_interface = f'./output/output_interface_{current_datetime}.csv'
csv_header_temp = ['Timestamp', 'Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4'
                           , 'Sensor 5', 'Sensor 6', 'Sensor 7', 'Sensor 8'
                           , 'Sensor 9', 'Sensor 10', 'Sensor 11', 'Sensor 12'
                           , 'Sensor 13', 'Sensor 14', 'Sensor 15', 'Sensor 16'
                           , 'Sensor 17', 'Sensor 18', 'Sensor 19', 'Sensor 20'
                           , 'Sensor 21', 'Sensor 22', 'Sensor 23', 'Sensor 24'
                           , 'Sensor 25', 'Sensor 26', 'Sensor 27', 'Sensor 28'
                           , 'Sensor 29', 'Sensor 30', 'Sensor 31', 'Sensor 32'
                           ,'Estado Alarme','Estado GA','Modo de Operação']
csv_file_path_log = f'./output/output_log_{current_datetime}.csv'
csv_header_log = ['Timestamp', 'Tipo', 'Mensagem']



average_temp = 0.0   #temperatura média 

### inicializa array com os valores máximos encontrados
temp_max_array = np.zeros(32, dtype='float32')
### inicializa array com os valores máximos encontrados
temp_min_array = np.zeros(32, dtype='float32')

tsensor_pipe = SharedMemoryDict(name='temperatures', size=4096)



tsensor_pipe["estado"] = alarm_on
tsensor_pipe["estado_ga"] = False
tsensor_pipe["limite_superior"] = upper_limit
tsensor_pipe["limite_inferior"] = lower_limit
tsensor_pipe["limite_superior_partida"] = upper_limit_start
tsensor_pipe["limite_inferior_partida"] = lower_limit_start
tsensor_pipe["calibracao"] = calibracao
tsensor_pipe["general_limit"] = general_limit
tsensor_pipe["limite_consecutivo"] = consecutive_limit
tsensor_pipe["modo"] = modo
tsensor_pipe["media"] = average_temp
tsensor_pipe["temperature"] = temp_max_array.tolist()
tsensor_pipe["temperature_max"] = temp_max_array.tolist()
tsensor_pipe["temperature_min"] = temp_max_array.tolist()
tsensor_pipe["enabled_sensor"] = enabled_sensor
tsensor_pipe["pre_alarme_timeout"] = pre_alarme_timeout
tsensor_pipe["repeat_lost"] = repeat_lost
tsensor_pipe["user"] = "system"
tsensor_pipe["connection"] = connection


def save_alarm_to_log(sensor,temp_limite,limite,temperatura,acionamento,contagem):
    global csv_file_path_log
    #global current_hour_alarm
    global csv_file_log
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

    with open(csv_file_path_log, mode='a', newline='', encoding="utf-8") as csv_file_log:
            csv_writer_temp = csv.writer(csv_file_log)
            csv_writer_temp.writerow([timestamp, "Alarme", "Sensor "+str(sensor+1)+" com limite "+limite+" de "+str(temp_limite)+"ºC e temperatura de "+str(temperatura)+"ºC . Acionou alarme? "+acionamento+" com contagem de "+str(contagem)])

def save_change_to_log(tipo,mensagem):
    global csv_file_path_log
    #global current_hour_alarm
    global csv_file_log
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

    with open(csv_file_path_log, mode='a', newline='', encoding="utf-8") as csv_file_log:
            csv_writer_temp = csv.writer(csv_file_log)
            csv_writer_temp.writerow([timestamp, tipo, mensagem])

def print_msg(message,level):
    if level <= verbose:
        print(message)

def blink_led_error(led_state):
    global debug_mode
    if debug_mode :
        data_received_mod = [0]
    else:
        data_received_mod = tcp_modbus.write_single_register(501, led_state)    #Liga/desliga led
    print_msg(f"Data received from Modbus after turning LED on/off: {data_received_mod}",2)

def turn_off_alarm():
    global alarm_on
    if not check_Alarm() :
        return
    
    if modo == 'desligado' :
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 


        # Writing data to the TCP port
        if debug_mode :
            data_received_mod = [0]
        else:
            data_received_mod = tcp_modbus.write_single_register(500, 0)    #Desliga alarme
        alarm_on = False
        tsensor_pipe["estado"] = False
        
        set_key(find_dotenv(), 'alarm_on', 'False')   #salva estado do alarme no '.env'
        print_msg(f"[{timestamp}] Turning off Alarm - Data written: (500, 0)",1)
        # Reading data from the RS485 port
        save_change_to_log("Modbus","Desligando Alarme, Modbus retornou "+str(data_received_mod))
        print_msg(f"Data received from Modbus: {data_received_mod}",1)
        return

def turn_on_alarm():
    global alarm_on
    if check_Alarm() :
        return

    if ((tsensor_pipe["modo"] == "auto") or (tsensor_pipe["modo"] == "partida")) :
        if check_GA():
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

            # Writing data to the TCP port
            if debug_mode:
                data_received_mod = True
                alarm_on = True
            else :
                data_received_mod = tcp_modbus.write_single_register(500, 1)    #Liga alarme
            print_msg(f"[{timestamp}] Turning alarm on - Data written: (500, 1)",2)
            save_change_to_log("Modbus","Ligando Alarme, Modbus "+("resposta OK!" if data_received_mod else "aparentemente desligado, sem resposta"))
            
            print_msg(f"Data received from Modbus: {data_received_mod}",2)
            check_Alarm()
    
            set_key(find_dotenv(), 'alarm_on', 'True')   #salva estado do alarme no '.env'

            return
        else:
            print_msg("Erro - Alarme não foi acionado - GA Desligado",1)
            save_change_to_log("Erro","Alarme não foi acionado - GA Desligado")
            #alarm_on = False
            #tsensor_pipe["estado"] = False
            return
    elif (tsensor_pipe["modo"] == 'ligado' ) :
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

        # Writing data to the TCP port

        if debug_mode:
            data_received_mod = True
        else :
            data_received_mod = tcp_modbus.write_single_register(500, 1)    #Liga alarme
        print_msg(f"[{timestamp}] Turning alarm on - Data written: (500, 1)",2)
        save_change_to_log("Modbus","Ligando Alarme, Modbus "+("resposta OK!" if data_received_mod else "aparentemente desligado, sem resposta"))

        print_msg(f"Data received from Modbus: {data_received_mod}",2)
        check_Alarm()
        set_key(find_dotenv(), 'alarm_on', 'True')   #salva estado do alarme no '.env'
        return

def check_GA():
    global modo, pre_alarme_init, GA_state
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 
    # Reading data to the TCP port
    if debug_mode:
        data_received_mod = [1]
    else :
        data_received_mod = tcp_modbus.read_holding_registers(70, 1)
    
    print_msg(f"[{timestamp}] Checking if GA is ON - Data written: (70, 1)",2)
        # Reading data from the RS485 port
        
    print_msg(f"Data received from Modbus: {data_received_mod}",2)
    if data_received_mod == [1] :
        print_msg(f"[{timestamp}] GA is ON",2)
        if not GA_state :
            print_msg(f"[{timestamp}] GA foi ligado - Identificada partida do motor",0)
            GA_state = True
            if ((modo == "auto") and (pre_alarme_init)) :
                print_msg(f"[{timestamp}] Entrando em modo partida",0)
                modo = "partida"
                tsensor_pipe["modo"] = "partida"
        tsensor_pipe["estado_ga"] = True
        return True
    else:
        print_msg(f"[{timestamp}] GA is OFF",2)
        tsensor_pipe["estado_ga"] = False
        GA_state = False
        return False        

def return_alarm_to_state(alarm_saved_state):
    if (alarm_saved_state != check_Alarm()):
        alarm_state = 1 if alarm_saved_state else 0
        if debug_mode:
                data_received_mod = alarm_state
        else :
            data_received_mod = tcp_modbus.write_single_register(500, alarm_state)    #Liga/desliga alarme
        
        alarm_on = True if alarm_state == 1 else False
        tsensor_pipe["estado"] = alarm_on
        print_msg(f"Inicializando o alarme conforme dados salvos '.env'. Modbus retornou: {data_received_mod}",0)


def check_Alarm():
    global alarm_on
    # Reading data to the TCP port
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

    if debug_mode:
        data_received_mod = [1 if alarm_on else 0]
    else :
        data_received_mod = tcp_modbus.read_holding_registers(500, 1)
        
    print_msg(f"[{timestamp}] Checking if Alarme is ON - Data written: (500, 1)",2)
    # Reading data from the RS485 port
    print_msg(f"Data received from Modbus: {data_received_mod}",2)

    alarm_state = (data_received_mod == [1]) 
    if (alarm_on!=alarm_state):
        print_msg(f"[{timestamp}] Alarm changed state to {alarm_state}",1)
        alarm_on = alarm_state
        tsensor_pipe["estado"] = alarm_on
        set_key(find_dotenv(), 'alarm_on', 'True' if alarm_on else 'False')   #salva estado do alarme no '.env'

    return alarm_state

def check_update_from_interface():
    global modo,upper_limit,lower_limit,consecutive_limit,general_limit,enabled_sensor,calibracao,pre_alarme_timeout, repeat_lost,connection, upper_limit_start, lower_limit_start

    user = tsensor_pipe["user"]
    if user is None:
        user = 'error getting user'
    if tsensor_pipe["modo"] != modo :
        modo = tsensor_pipe["modo"]
        set_key(find_dotenv(), 'modo', modo)   #salva estado do alarme no '.env'
        save_change_to_log("Info","Modo alterado para "+modo_string(modo)+" por usuário " + user)
        if modo == 'ligado':
            turn_on_alarm()
        else :
            turn_off_alarm()
    if tsensor_pipe["limite_superior"] != upper_limit :
        upper_limit = tsensor_pipe["limite_superior"]
        set_key(find_dotenv(), 'upper_limit', str(upper_limit))   #salva estado do alarme no '.env'
        save_change_to_log("Info","Limite superior alterado para "+str(upper_limit)+" por usuário " + user)
    if tsensor_pipe["limite_inferior"] != lower_limit :
        lower_limit = tsensor_pipe["limite_inferior"]
        set_key(find_dotenv(), 'lower_limit', str(lower_limit))   #salva estado do alarme no '.env'
        save_change_to_log("Info","Limite inferior alterado para "+str(lower_limit)+" por usuário "+ user)
    if tsensor_pipe["limite_consecutivo"] != consecutive_limit :
        consecutive_limit = tsensor_pipe["limite_consecutivo"]
        set_key(find_dotenv(), 'consecutive_limit', str(consecutive_limit))   
        save_change_to_log("Info","Quantidade de amostras antes de alarmar alterado para  "+str(consecutive_limit)+" por usuário "+ user)
    if tsensor_pipe["general_limit"] != general_limit :
        general_limit = tsensor_pipe["general_limit"]
        set_key(find_dotenv(), 'general_limit', str(general_limit))  
        save_change_to_log("Info","Modo de avaliação de limites alterado para "+ ("Geral" if general_limit else "Individual")+" por usuário "+ user)
    if tsensor_pipe["enabled_sensor"] != enabled_sensor :
        enabled_sensor = tsensor_pipe["enabled_sensor"]
        set_key(find_dotenv(), 'enabled_sensor', str(enabled_sensor))  
        save_change_to_log("Info","Lista de sensores habilitados alterada para "+str(enabled_sensor)+" por usuário "+ user)
    if tsensor_pipe["calibracao"] != calibracao :
        calibracao = tsensor_pipe["calibracao"]
        set_key(find_dotenv(), 'calibracao', str(calibracao))  
        save_change_to_log("Info","Calibração dos sensores alterada para "+str(calibracao)+" por usuário "+ user)
    if tsensor_pipe["pre_alarme_timeout"] != pre_alarme_timeout :
        pre_alarme_timeout = tsensor_pipe["pre_alarme_timeout"]
        set_key(find_dotenv(), 'pre_alarme_timeout', str(pre_alarme_timeout))  
        save_change_to_log("Info","Timeout de pré-alarme alterado para "+str(pre_alarme_timeout)+" por usuário "+ user)
    if tsensor_pipe["repeat_lost"] != repeat_lost :
        repeat_lost = tsensor_pipe["repeat_lost"]
        set_key(find_dotenv(), 'repeat_lost', str(repeat_lost))  
        save_change_to_log("Info","Filtro repete anterior alterado para "+("Ligado" if repeat_lost else "Desligado")+" por usuário "+ user)
    if tsensor_pipe["connection"] != connection :
        connection = tsensor_pipe["connection"]
        save_change_to_log("Info","Nova conexão na interface por usuário " + user + " - connection: " + str(connection))
        connection = ""
        tsensor_pipe["connection"] = connection
        print_msg(f"[{timestamp}] Nova conexão do usuário {user}",1)
    if tsensor_pipe["limite_superior_partida"] != upper_limit_start :
        upper_limit_start = tsensor_pipe["limite_superior_partida"]
        set_key(find_dotenv(), 'upper_limit_start', str(upper_limit_start))   #salva estado do alarme no '.env'
        save_change_to_log("Info","Limite superior de partida alterado para "+str(upper_limit_start)+" por usuário "+ user)         
    if tsensor_pipe["limite_inferior_partida"] != lower_limit_start :
        lower_limit_start = tsensor_pipe["limite_inferior_partida"]
        set_key(find_dotenv(), 'lower_limit_start', str(lower_limit_start))   #salva estado do alarme no '.env'
        save_change_to_log("Info","Limite inferior de partida alterado para "+str(lower_limit_start)+" por usuário "+ user) 
    



def modo_string(modo):
    if modo == 'ligado':
        return "Ligado Manual"
    elif modo == 'desligado':
        return "Desligado Manual"
    elif modo == 'auto':
        return "Alarme Operacional"
    elif modo == 'partida':
        return "Partida"
    else:
        return "Erro - Modo não reconhecido"

def reiniciar_haste(timeOff,timeOn):
    
    data_received_mod = tcp_modbus.write_single_register(502, 1)    #Desliga haste
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    print_msg(f"[{timestamp}] Desligando a haste - Data written: (502, 1)",1)
    
    print_msg(f"Data received from Modbus: {data_received_mod}",1)
    time.sleep(timeOff)

    data_received_mod = tcp_modbus.write_single_register(502, 0)    #Liga haste
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    print_msg(f"[{timestamp}] Religando a haste - Data written: (502, 0)",1)
    
    print_msg(f"Data received from Modbus: {data_received_mod}",1)
    time.sleep(timeOn)
    return

def inicializa_haste():
    global average_temp
    avg_init = np.zeros(32, dtype='float32')
    for x in range(10):
        read_count = 0
        for i in range(16):

            controller_ID = "%0.2X" % (i+1)
            #if controller_ID == "10" :
            #    controller_ID = "15"
            hex_data_to_write = "64" + controller_ID
            data_to_write = bytes.fromhex(hex_data_to_write)


            if debug_mode:
                random_number = np.random.randint(3000, 4001)
                hex_number = format(random_number, '04x')
                random_number = np.random.randint(3000, 4001)
                data_received = '2165' + hex_number + format(random_number, '04x') ### uso apenas em testes - modo debug

            else:
                ser_sensor.write(data_to_write)
                data_received = ser_sensor.read(12).hex()

            if ((data_received[:4] == "2165") and (len(data_received) == 12)):
                read_count += 1
                avg_init[i*2] = int(data_received[4:8],16)/100
                avg_init[(i*2)+1] = int(data_received[8:12],16)/100

            time.sleep(0.1)

        if read_count != 16 :
            print_msg(f"Haste inicializada com {read_count}/16 controladores, reiniciando haste.",0)
            save_change_to_log("Erro","Haste inicializada com "+str(read_count)+"/16 controladores, reiniciando haste.")
            reiniciar_haste(5,5)
        else:
            print_msg("Haste inicializada",0)
            save_change_to_log("Info","Haste inicializada com todos os controladores OK.")
            average_temp = np.sum(avg_init)/32
            return
    print_msg("Haste inicializada porém com sensores faltando.",0)
    save_change_to_log("Info","Haste inicializada com sensores faltando.")
    if read_count != 0 :
        average_temp = np.sum(avg_init)/read_count
    else :
        average_temp = 0.0
    return


def analisa_alarme(sensor):
    global enabled_sensor, temp_array, outlier_temp, upper_limit_total, alarm_up_array, consecutive_limit, timestamp, lower_limit_total, alarm_down_array, temp_shm, average_temp, repeat_lost, repeat_lost_over

    acionou_alarme = False
    ### verifica se o sensor está habilitado
    if enabled_sensor[sensor] :
        ### verifica se o sensor estivá com a temperatura acima do limite outlier
        if temp_array[sensor] < outlier_temp :
            ### verifica se ultrapassou limite superior
            if temp_array[sensor] > upper_limit_total :
                alarm_up_array[sensor] += 1
                if alarm_up_array[sensor] > consecutive_limit :
                    turn_on_alarm()
                    acionou_alarme = True

                    print_msg(f"[{timestamp}] ALARME TEMPERATURA ALTA --- Sensor {sensor} com temperatura de %.2f" % temp_array[sensor],0)
                    save_alarm_to_log(i*2,upper_limit_total,"Superior",temp_array[sensor],"Sim",alarm_up_array[sensor])
                else: 
                    save_alarm_to_log(i*2,upper_limit_total,"Superior",temp_array[sensor],"Não",alarm_up_array[sensor])
                    pass
            else :   # se temperatura não estiver maior que o limite, zera o contador
                alarm_up_array[sensor] = 0

            ### verifica se ultrapassou limite inferior
            if temp_array[sensor] < lower_limit_total :
                alarm_down_array[sensor] += 1
                if alarm_down_array[sensor] > consecutive_limit :
                    turn_on_alarm()
                    acionou_alarme = True

                    print_msg(f"[{timestamp}] ALARME TEMPERATURA BAIXA --- Sensor {sensor} com temperatura de %.2f" % temp_array[sensor],0)
                    save_alarm_to_log(i*2,lower_limit_total,"Inferior",temp_array[sensor],"Sim",alarm_down_array[sensor])
                else: 
                    save_alarm_to_log(i*2,lower_limit_total,"Inferior",temp_array[sensor],"Não",alarm_down_array[sensor])
                    pass
            else :   # se temperatura não estiver menor que o limite, zera o contador
                alarm_down_array[sensor] = 0
        else:    # se o sensor estiver com a temperatura acima do limite outlier, desconsidera o valor e usa a média
            temp_shm[sensor] = average_temp
            if (repeat_lost and not repeat_lost_over):
                temp_shm[sensor] = last_temp_array[sensor]
    else:    # se o sensor não estiver habilitado, salva a temperatura média na lista shm
        temp_shm[sensor] = average_temp

    return acionou_alarme



#############################################################################
##########################  INICIO DO LOOP  #################################
#############################################################################

try:
    
    alarm_up_array = np.zeros(32, dtype='int')
    alarm_down_array = np.zeros(32, dtype='int')
    
    if current_hour == 0 :
        current_hour = time.localtime().tm_hour 
        with open(csv_file_path_temp, mode='w', newline='', encoding="utf-8") as csv_file_temp:
            csv_writer_temp = csv.writer(csv_file_temp)
            csv_writer_temp.writerow(csv_header_temp)  # Write the header to the CSV file
        with open(csv_file_path_interface, mode='w', newline='', encoding="utf-8") as csv_file_interface:
            csv_writer_interface= csv.writer(csv_file_interface)
            csv_writer_interface.writerow(csv_header_temp)  # Write the header to the CSV file
        with open(csv_file_path_log, mode='w', newline='', encoding="utf-8") as csv_file_log:
            csv_writer_log = csv.writer(csv_file_log)
            csv_writer_log.writerow(csv_header_log)  # Write the header to the CSV file
    if debug_mode :
        save_change_to_log("Info","Sistema iniciado em modo debug.")
        print_msg("Sistema iniciado em modo debug",0)
    else:
        save_change_to_log("Info","Sistema iniciado.")
        print_msg("Sistema iniciado",0)

    return_alarm_to_state(alarm_on)   #retorna alarme para o estado inicial gravado no '.env'

    inicializa_haste()
    reboot_sensor_count = 0  # temporizador para limitar reinicialização da haste a cada 10min (600s)

    if alarm_on:             # verifica se o alarme está ligado ao iniciar o sistema, se estiver, desabilita o pré-alarme
        pre_alarme_init = False

    last_temp_array = np.zeros(32, dtype='float32')

    while True:
        ### inicia marcação de tempo para que cada leitura seja feita em intervalos de 1s
        frame_start = time.time() * 1000

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

        # Check if the hour has changed

        if time.localtime().tm_hour != current_hour:
            current_hour = time.localtime().tm_hour 
            if csv_file_path_temp:
                csv_file_temp.close()
                csv_file_interface.close()

            # Create a new CSV file
            current_datetime = time.strftime("%Y%m%d_%H%M%S")
            csv_file_path_temp = f'./output/output_temp_{current_datetime}.csv'
            csv_file_path_log = f'./output/output_log_{current_datetime}.csv'
            with open(csv_file_path_temp, mode='w', newline='', encoding="utf-8") as csv_file_temp:
                csv_writer_temp = csv.writer(csv_file_temp)
                csv_writer_temp.writerow(csv_header_temp)  # Write the header to the CSV file
            with open(csv_file_path_interface, mode='w', newline='', encoding="utf-8") as csv_file_interface:
                csv_writer_interface= csv.writer(csv_file_interface)
                csv_writer_interface.writerow(csv_header_temp)  # Write the header to the CSV file
            with open(csv_file_path_log, mode='w', newline='', encoding="utf-8") as csv_file_log:
                csv_writer_log = csv.writer(csv_file_log)
                csv_writer_log.writerow(csv_header_log)  # Write the header to the CSV file
            print_msg(f"[{timestamp}] Creating a new CSV file for the new hour.",0)


        
        ### zera o array de temperaturas
        temp_array = np.zeros(32, dtype='float32')      ## ARRAY COM VALORES QUE SÃO ENVIADOS PARA CSV
        temp_shm = np.zeros(32, dtype='float32')        ## ARRAY COM VALORES QUE SÃO ENVIADOS PARA PÁGINA DO USUÁRIO - sem valores zerados

        alarmou = False

        ### inicia a contagem de 16 controladores
        for i in range(16):

            ### inicia a marcação de tempo de leitura para evitar sobrecarregar o buffer da serial
            delay_read_start = time.time() * 1000

            controller_ID = "%0.2X" % (i+1)
            #if controller_ID == "10" :
            #    controller_ID = "15"
            # Writing data to the RS485 port
            # Hex data to write
            hex_data_to_write = "64" + controller_ID
            # Convert hex string to bytes
            data_to_write = bytes.fromhex(hex_data_to_write)

            if debug_mode :
                random_number = np.random.randint(3000, 4001)
                hex_number = format(random_number, '04x')
                random_number = np.random.randint(3000, 4001)
                data_received = '2165' + hex_number + format(random_number, '04x') ### uso apenas em testes - modo debug
            else:
                # Writing data to the RS485 port
                ser_sensor.write(data_to_write)
                # Reading data from the RS485 port
                data_received = ser_sensor.read(12).hex()


            print_msg(f"[{timestamp}] Data written: {hex_data_to_write} Data received: {data_received}",3)
            #time.sleep(5)



            if ((data_received[:4] == "2165") and (len(data_received) == 12)):

                ####################################################################
                ### recorta os dados do primeiro sensor ############################
                ####################################################################
                if modo == "partida" :
                    upper_limit_total = (average_temp + (upper_limit_start[32] if general_limit else upper_limit_start[i*2]) )
                    lower_limit_total = (average_temp - (lower_limit_start[32] if general_limit else lower_limit_start[i*2]) )
                else: 
                    upper_limit_total = (average_temp + (upper_limit[32] if general_limit else upper_limit[i*2]) )
                    lower_limit_total = (average_temp - (lower_limit[32] if general_limit else lower_limit[i*2]) )


                #########  converte valor recebido da serial em temperatura
                temp_array[i*2] = int(data_received[4:8],16)/100
                temp_shm[i*2] = int(data_received[4:8],16)/100

                #########  ajusta valor da temperatura com dados de calibração
                temp_array[i*2] += calibracao[i*2]
                temp_shm[i*2] += calibracao[i*2]

                
                alarmou |= analisa_alarme(i*2)

                ####################################################################
                ### recorta os dados do segundo sensor #############################
                ####################################################################

                if modo == "partida" :
                    upper_limit_total = (average_temp + (upper_limit_start[32] if general_limit else upper_limit_start[(i*2)+1]) )
                    lower_limit_total = (average_temp - (lower_limit_start[32] if general_limit else lower_limit_start[(i*2)+1]) )
                else: 
                    upper_limit_total = (average_temp + (upper_limit[32] if general_limit else upper_limit[(i*2)+1]) )
                    lower_limit_total = (average_temp - (lower_limit[32] if general_limit else lower_limit[(i*2)+1]) )
                

                #########  converte valor recebido da serial em temperatura
                temp_array[(i*2)+1] = int(data_received[8:12],16)/100
                temp_shm[(i*2)+1] = int(data_received[8:12],16)/100

                #########  ajusta valor da temperatura com dados de calibração
                temp_array[(i*2)+1] += calibracao[(i*2)+1]
                temp_shm[(i*2)+1] += calibracao[(i*2)+1]

                alarmou |= analisa_alarme((i*2)+1)


            else:
                ################### ERRO DE LEITURA ######################
                temp_shm[i*2] = average_temp
                temp_shm[(i*2)+1] = average_temp
                if (repeat_lost and not repeat_lost_over):
                    temp_shm[i*2] = last_temp_array[i*2]
                    temp_shm[(i*2)+1] = last_temp_array[(i*2)+1]

            delay_read_finish = round((time.time() * 1000 ) - delay_read_start)
            print_msg(f"Read processing time: {delay_read_finish}ms",2)
            if delay_read_finish < CONST_READ_DELAY :
                time.sleep((CONST_READ_DELAY-delay_read_finish)/1000)
            else :
                pass
                #time.sleep(0.01)
                

        if modo == "partida":
            if pre_alarme_timeout > 0:
                pre_alarme_timeout -= 1
                tsensor_pipe["pre_alarme_timeout"] = pre_alarme_timeout
            else:
                modo = "auto"
                tsensor_pipe["modo"] = modo

        check_update_from_interface()
        
        if alarm_on :
            if ((max(alarm_down_array) < consecutive_limit) and (max(alarm_up_array) < consecutive_limit)) :
                turn_off_alarm()
                pass
            else :
                turn_on_alarm()
                pass

                

        check_Alarm()

        with open(csv_file_path_temp, mode='a', newline='', encoding="utf-8") as csv_file_temp:
            csv_writer_temp = csv.writer(csv_file_temp)
            csv_writer_temp.writerow([timestamp, temp_array[0], temp_array[1], temp_array[2], temp_array[3]
                                        , temp_array[4], temp_array[5], temp_array[6], temp_array[7]
                                        , temp_array[8], temp_array[9], temp_array[10], temp_array[11]
                                        , temp_array[12], temp_array[13], temp_array[14], temp_array[15]
                                        , temp_array[16], temp_array[17], temp_array[18], temp_array[19]
                                        , temp_array[20], temp_array[21], temp_array[22], temp_array[23]
                                        , temp_array[24], temp_array[25], temp_array[26], temp_array[27]
                                        , temp_array[28], temp_array[29], temp_array[30], temp_array[31]
                                        , alarm_on, check_GA(), modo_string(modo) ])
        with open(csv_file_path_interface, mode='a', newline='', encoding="utf-8") as csv_file_interface:
            csv_writer_interface = csv.writer(csv_file_interface)
            csv_writer_interface.writerow([timestamp, temp_shm[0], temp_shm[1], temp_shm[2], temp_shm[3]
                                        , temp_shm[4], temp_shm[5], temp_shm[6], temp_shm[7]
                                        , temp_shm[8], temp_shm[9], temp_shm[10], temp_shm[11]
                                        , temp_shm[12], temp_shm[13], temp_shm[14], temp_shm[15]
                                        , temp_shm[16], temp_shm[17], temp_shm[18], temp_shm[19]
                                        , temp_shm[20], temp_shm[21], temp_shm[22], temp_shm[23]
                                        , temp_shm[24], temp_shm[25], temp_shm[26], temp_shm[27]
                                        , temp_shm[28], temp_shm[29], temp_shm[30], temp_shm[31]
                                        , alarm_on, check_GA(), modo_string(modo) ])
        for i in range(len(temp_shm)):
            temp_max_array[i] = max(temp_max_array[i],temp_shm[i])
            if temp_shm[i] != 0.0 :
                if temp_min_array[i] == 0.0 :
                    temp_min_array[i] = temp_shm[i]
                else :
                    temp_min_array[i] = min(temp_min_array[i],temp_shm[i])

        
        tsensor_pipe["temperature"] = temp_shm.tolist()
        tsensor_pipe["temperature_max"] = temp_max_array.tolist()
        tsensor_pipe["temperature_min"] = temp_min_array.tolist()
        tsensor_pipe["estado"] = alarm_on

        last_temp_array = temp_shm.copy()

        ####################################################################
        ##### Cálculo da média de temperaturas #############################
        ####################################################################
        average_array = np.zeros(32, dtype='float32')
        error_array = np.zeros(32, dtype='float32')
        for i in range(32):
            if temp_array[i] < outlier_temp :
                error_array[i] = temp_array[i]
            else :
                error_array[i] = 0

            if enabled_sensor[i] :
                if temp_array[i] < outlier_temp :
                    average_array[i] = temp_array[i]
                else :
                    average_array[i] = 0
            else :
                average_array[i] = 0
            

        read_count = np.count_nonzero(average_array)   # verifica quantas temperaturas são diferentes de 0
        if read_count != 0 :
            average_temp = np.sum(average_array)/read_count
        else :
            average_temp = 0.0
        tsensor_pipe["media"] = average_temp


        ####################################################################
        ##### Verificação de erros na leitura  #############################
        ####################################################################
        #
        #  Análise de erros de leitura
        #  Verifica se a contagem de leituras corretas é menor que 32, se
        #  for, indica que houve erro.
        #  Depois de 5 leituras seguidas com erro, acende o LED indicando 
        #  erro (somente se mais de 1 sensor estiver com problema) e 
        #  reinicia a haste.
        #  Se o erro persistir por 'count_error_limit' (default 5min), 
        #  reinicia novamente o contador e habilita o repeat_lost_over.
        #  Quando o repeat_lost_over estiver habilitado o sensor com 
        #  falha vai pra média. Essa verificação é global para os sensores
        #  portanto independe de contagem individual de erros.
        #
        #

        read_count_error = np.count_nonzero(error_array)
        if read_count_error != 32:                #verifica se tem falha na leitura dos sensores
            reboot_sensor_count+=1
            if ((reboot_sensor_count > 5) and (read_count_error < 31)) :
                blink_led_error(True)
            if reboot_sensor_count == 5:
                count_reboot+=1
                if count_reboot < 3:        #verifica se já teve pelo menos 2 reinicializações com menos de 5min, se tiver, reinicia count_reboot e aguarda 
                    #reiniciar_haste(2,3)
                    pass
                else:
                    if count_reboot > 100:
                        count_reboot = 0
            if reboot_sensor_count == count_error_limit:   #se tiver por mais de 5min (count_error_limit) com sensores faltando, reinicia contagem
                #reboot_sensor_count = 0
                count_reboot = 0
                if repeat_lost :
                    repeat_lost_over = True

        else:
            reboot_sensor_count = 0        #se estiver OK, zera o contador
            repeat_lost_over = False       #zera o verificador de filtro repete ligado por mais de 5min (count_error_limit)
            blink_led_error(False)


        frame_finish = round((time.time() * 1000 ) - frame_start)
        print_msg(f"Total processing time: {frame_finish}ms",2)
        print_msg(f"array: {temp_array}",3)
        if frame_finish < read_time :
            time.sleep((read_time-frame_finish)/1000)
        else :
            time.sleep(0.1)

except KeyboardInterrupt:
    # Handle KeyboardInterrupt (Ctrl+C) to gracefully exit the loop
    print("Program terminated by user.")
    save_change_to_log("Info","Sistema finalizado pelo usuário.")
except serial.SerialTimeoutException:
    print("Program terminated by SerialTimeoutException. Modbus not connected or error")
    save_change_to_log("Erro","Programa finalizado por exceção ou com erro.")
finally:
    # Close the serial port
    ser_sensor.close()
    csv_file_temp.close()
    csv_file_interface.close()
    tsensor_pipe.shm.close()
