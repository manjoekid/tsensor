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
    CONST_READ_TIME = 1000

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

    consecutive_limit = int(os.getenv('consecutive_limit',default='7'))     # limite de medidas acima da temperatura para acionar alarme. Por exemplo se limite é 5, o alarme vai acionar quando for realizada a 6 leitura consecutiva acima ou abaixo do limite
    general_limit = (os.getenv('general_limit',default='True')=='True')

    env_line = os.getenv("enabled_sensor")
    enabled_sensor = [True for x in range(32)]
    if env_line == None :
        set_key(find_dotenv(), 'enabled_sensor', str(enabled_sensor))   #salva estado do alarme no '.env'
    else :
        # Convert the string representation of list to a Python list
        enabled_sensor = ast.literal_eval(env_line)
    debug_mode = (os.getenv('debug_mode',default='False')=='True')

    modo = os.getenv('modo',default='auto')
    alarm_on = (os.getenv('alarm_on',default='True')=='True')

    #set_key(find_dotenv(), 'upper_limit', "7.7")
    #load_dotenv(override=True)

except:
    print("Erro ao carregar variáveis de ambiente")
    
current_hour = 0
current_hour_alarm = 0


# Create a serial object
ser_sensor = serial.Serial(port_serial, baudrate_serial, timeout=timeout_serial)
#ser_sensor = serial.Serial(port=port1, baudrate=baudrate1, bytesize=8, parity='N', stopbits=2, timeout=timeout1, xonxoff=0, rtscts=0)
tcp_modbus = ModbusClient(host=host_tcp, port=port_tcp, unit_id=unit_id_tcp, auto_open=auto_open_tcp)


# Open a CSV file for writing temp
current_datetime = time.strftime("%Y%m%d_%H%M%S")
csv_file_path_temp = f'./output/output_temp_{current_datetime}.csv'
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
tsensor_pipe["general_limit"] = general_limit
tsensor_pipe["limite_consecutivo"] = consecutive_limit
tsensor_pipe["modo"] = modo
tsensor_pipe["media"] = average_temp
tsensor_pipe["temperature"] = temp_max_array.tolist()
tsensor_pipe["temperature_max"] = temp_max_array.tolist()
tsensor_pipe["temperature_min"] = temp_max_array.tolist()
tsensor_pipe["enabled_sensor"] = enabled_sensor



def save_alarm_to_log(sensor,temp_limite,limite,temperatura,acionamento,contagem):
    global csv_file_path_log
    #global current_hour_alarm
    global csv_file_log
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

    with open(csv_file_path_log, mode='a', newline='') as csv_file_log:
            csv_writer_temp = csv.writer(csv_file_log)
            csv_writer_temp.writerow([timestamp, "Alarme", "Sensor "+str(sensor+1)+" com limite "+limite+" de "+str(temp_limite)+"ºC e temperatura de "+str(temperatura)+"ºC . Acionou alarme? "+acionamento+" com contagem de "+str(contagem)])

def save_change_to_log(tipo,mensagem):
    global csv_file_path_log
    #global current_hour_alarm
    global csv_file_log
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

    with open(csv_file_path_log, mode='a', newline='') as csv_file_log:
            csv_writer_temp = csv.writer(csv_file_log)
            csv_writer_temp.writerow([timestamp, tipo, mensagem])


def turn_off_alarm():
    global alarm_on

    if tsensor_pipe["modo"] == 'desligado' :
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 


        # Writing data to the TCP port
        if debug_mode :
            data_received_mod = [1]
        else:
            data_received_mod = tcp_modbus.write_single_register(500, 0)    #Desliga alarme
        alarm_on = False
        tsensor_pipe["estado"] = False
        
        set_key(find_dotenv(), 'alarm_on', 'False')   #salva estado do alarme no '.env'

        print(f"[{timestamp}] Turning off Alarm - Data written: (500, 0)")
        # Reading data from the RS485 port
        save_change_to_log("Modbus","Desligando Alarme, Modbus retornou "+str(data_received_mod))
        print(f"Data received from Modbus: {data_received_mod}")
        return

def turn_on_alarm():
    global alarm_on
    #if check_Alarm() :
    #    return

    if tsensor_pipe["modo"] == 'auto' :
        if check_GA():
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

            # Writing data to the TCP port
            if debug_mode:
                data_received_mod = True
            else :
                data_received_mod = tcp_modbus.write_single_register(500, 1)    #Liga alarme

            print(f"[{timestamp}] Turning alarm on - Data written: (500, 1)")
            save_change_to_log("Modbus","Ligando Alarme, Modbus "+("resposta OK!" if data_received_mod else "aparentemente desligado, sem resposta"))

            print(f"Data received from Modbus: {data_received_mod}")
            check_Alarm()
    
            set_key(find_dotenv(), 'alarm_on', 'True')   #salva estado do alarme no '.env'

            return
        else:
            print("Erro - Alarme não foi acionado - GA Desligado")
            save_change_to_log("Erro","Alarme não foi acionado - GA Desligado")
            #alarm_on = False
            #tsensor_pipe["estado"] = False
            return
    elif tsensor_pipe["modo"] == 'ligado' :
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

        # Writing data to the TCP port

        if debug_mode:
                data_received_mod = True
        else :
            data_received_mod = tcp_modbus.write_single_register(500, 1)    #Liga alarme

        print(f"[{timestamp}] Turning alarm on - Data written: (500, 1)")
        save_change_to_log("Modbus","Ligando Alarme, Modbus "+("resposta OK!" if data_received_mod else "aparentemente desligado, sem resposta"))

        print(f"Data received from Modbus: {data_received_mod}")
        check_Alarm()
        set_key(find_dotenv(), 'alarm_on', 'True')   #salva estado do alarme no '.env'
        return

def check_GA():
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 
    # Reading data to the TCP port
    if debug_mode:
                data_received_mod = [1]
    else :
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

def return_alarm_to_state(alarm_saved_state):
    if (alarm_saved_state != check_Alarm()):
        alarm_state = 1 if alarm_saved_state else 0
        if debug_mode:
                data_received_mod = alarm_state
        else :
            data_received_mod = tcp_modbus.write_single_register(500, alarm_state)    #Liga/desliga alarme
        
        alarm_on = alarm_state
        tsensor_pipe["estado"] = alarm_on
        print(f"Inicializando o alarme conforme dados salvos '.env'. Modbus retornou: {data_received_mod}")


def check_Alarm():
    global alarm_on
    # Reading data to the TCP port
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

    if debug_mode:
        data_received_mod = [1]
    else :
        data_received_mod = tcp_modbus.read_holding_registers(500, 1)
        

    print(f"[{timestamp}] Checking if Alarme is ON - Data written: (500, 1)")
    # Reading data from the RS485 port
        
    print(f"Data received from Modbus: {data_received_mod}")

    alarm_state = (data_received_mod == [1]) 
    if (alarm_on!=alarm_state):
        print(f"[{timestamp}] Alarm changed state to {alarm_state}")
        alarm_on = alarm_state
        tsensor_pipe["estado"] = alarm_on
        set_key(find_dotenv(), 'alarm_on', 'True' if alarm_on else 'False')   #salva estado do alarme no '.env'

    return alarm_state

def check_update_from_interface():
    global modo,upper_limit,lower_limit,consecutive_limit,general_limit,enabled_sensor
    if tsensor_pipe["modo"] != modo :
        modo = tsensor_pipe["modo"]
        set_key(find_dotenv(), 'modo', modo)   #salva estado do alarme no '.env'
        save_change_to_log("Info","Modo alterado para "+modo)
        if modo == 'ligado':
            turn_on_alarm()
        else :
            turn_off_alarm()
    if tsensor_pipe["limite_superior"] != upper_limit :
        upper_limit = tsensor_pipe["limite_superior"]
        set_key(find_dotenv(), 'upper_limit', str(upper_limit))   #salva estado do alarme no '.env'
        save_change_to_log("Info","Limite superior alterado para "+str(upper_limit))
    if tsensor_pipe["limite_inferior"] != lower_limit :
        lower_limit = tsensor_pipe["limite_inferior"]
        set_key(find_dotenv(), 'lower_limit', str(lower_limit))   #salva estado do alarme no '.env'
        save_change_to_log("Info","Limite inferior alterado para "+str(lower_limit))
    if tsensor_pipe["limite_consecutivo"] != consecutive_limit :
        consecutive_limit = tsensor_pipe["limite_consecutivo"]
        set_key(find_dotenv(), 'consecutive_limit', str(consecutive_limit))   #salva estado do alarme no '.env'
        save_change_to_log("Info","Quantidade de amostras antes de alarmar alterado para  "+str(consecutive_limit))
    if tsensor_pipe["general_limit"] != general_limit :
        general_limit = tsensor_pipe["general_limit"]
        set_key(find_dotenv(), 'general_limit', str(general_limit))   #salva estado do alarme no '.env'
        save_change_to_log("Info","Modo de avaliação de limites alterado para "+ ("Geral" if general_limit else "Individual"))
    if tsensor_pipe["enabled_sensor"] != enabled_sensor :
        enabled_sensor = tsensor_pipe["enabled_sensor"]
        set_key(find_dotenv(), 'enabled_sensor', str(enabled_sensor))   #salva estado do alarme no '.env'
        save_change_to_log("Info","Lista de sensores habilitados alterada para "+str(enabled_sensor))


def reiniciar_haste(timeOff,timeOn):
    
    data_received_mod = tcp_modbus.write_single_register(502, 1)    #Desliga haste
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    print(f"[{timestamp}] Desligando a haste - Data written: (502, 1)")
    
    print(f"Data received from Modbus: {data_received_mod}")
    time.sleep(timeOff)

    data_received_mod = tcp_modbus.write_single_register(502, 0)    #Liga haste
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    print(f"[{timestamp}] Religando a haste - Data written: (502, 0)")
    
    print(f"Data received from Modbus: {data_received_mod}")
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
            print(f"Haste inicializada com {read_count}/16 controladores, reiniciando haste.")
            save_change_to_log("Erro","Haste inicializada com "+str(read_count)+"/16 controladores, reiniciando haste.")
            reiniciar_haste(5,5)
        else:
            print("Haste inicializada")
            save_change_to_log("Info","Haste inicializada com todos os controladores OK.")
            average_temp = np.sum(avg_init)/32
            return
    print("Haste inicializada porém com sensores faltando.")
    save_change_to_log("Info","Haste inicializada com sensores faltando.")
    if read_count != 0 :
        average_temp = np.sum(avg_init)/read_count
    else :
        average_temp = 0.0
    return

try:
    
    alarm_up_array = np.zeros(32, dtype='int')
    alarm_down_array = np.zeros(32, dtype='int')
    
    if current_hour == 0 :
        current_hour = time.localtime().tm_hour 
        with open(csv_file_path_temp, mode='w', newline='') as csv_file_temp:
            csv_writer_temp = csv.writer(csv_file_temp)
            csv_writer_temp.writerow(csv_header_temp)  # Write the header to the CSV file
        with open(csv_file_path_log, mode='w', newline='') as csv_file_log:
            csv_writer_log = csv.writer(csv_file_log)
            csv_writer_log.writerow(csv_header_log)  # Write the header to the CSV file

    save_change_to_log("Info","Sistema iniciado.")

    return_alarm_to_state(alarm_on)   #retorna alarme para o estado inicial gravado no '.env'

    inicializa_haste()
    reboot_sensor_count = 0  # temporizador para limitar reinicialização da haste a cada 10min (600s)

    reboot_sensor_count = 0  # temporizador para limitar reinicialização da haste a cada 10min (600s)

    while True:
        ### inicia marcação de tempo para que cada leitura seja feita em intervalos de 1s
        frame_start = time.time() * 1000

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

        # Check if the hour has changed

        if time.localtime().tm_hour != current_hour:
            current_hour = time.localtime().tm_hour 
            if csv_file_path_temp:
                csv_file_temp.close()

            # Create a new CSV file
            current_datetime = time.strftime("%Y%m%d_%H%M%S")
            csv_file_path_temp = f'./output/output_temp_{current_datetime}.csv'
            csv_file_path_log = f'./output/output_log_{current_datetime}.csv'
            with open(csv_file_path_temp, mode='w', newline='') as csv_file_temp:
                csv_writer_temp = csv.writer(csv_file_temp)
                csv_writer_temp.writerow(csv_header_temp)  # Write the header to the CSV file
            with open(csv_file_path_log, mode='w', newline='') as csv_file_log:
                csv_writer_log = csv.writer(csv_file_log)
                csv_writer_log.writerow(csv_header_log)  # Write the header to the CSV file
            print(f"[{timestamp}] Creating a new CSV file for the new hour.")


        ### zera o array de temperaturas
        temp_array = np.zeros(32, dtype='float32')      ## ARRAY COM VALORES QUE SÃO ENVIADOS PARA CSV
        temp_shm = np.zeros(32, dtype='float32')        ## ARRAY COM VALORES QUE SÃO ENVIADOS PARA PÁGINA DO USUÁRIO - sem valores zerados


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


            print(f"[{timestamp}] Data written: {hex_data_to_write} Data received: {data_received}")
            #time.sleep(5)



            if ((data_received[:4] == "2165") and (len(data_received) == 12)):

                

                ####################################################################
                ### recorta os dados do primeiro sensor ############################
                ####################################################################

                upper_limit_total = (average_temp + (upper_limit[32] if general_limit else upper_limit[i*2]) )
                lower_limit_total = (average_temp - (lower_limit[32] if general_limit else lower_limit[i*2]) )


                temp_array[i*2] = int(data_received[4:8],16)/100
                temp_shm[i*2] = int(data_received[4:8],16)/100
                ### verifica se o sensor está habilitado
                if enabled_sensor[i*2] :
                    ### verifica se ultrapassou limite superior
                    if temp_array[i*2] > upper_limit_total :
                        alarm_up_array[i*2] += 1
                        if alarm_up_array[i*2] > consecutive_limit :
                            turn_on_alarm()
                            

                            print(f"[{timestamp}] ALARME TEMPERATURA ALTA --- Sensor {i*2} com temperatura de %.2f" % temp_array[i*2])
                            save_alarm_to_log(i*2,upper_limit_total,"Superior",temp_array[i*2],"Sim",alarm_up_array[i*2])
                        else: 
                            save_alarm_to_log(i*2,upper_limit_total,"Superior",temp_array[i*2],"Não",alarm_up_array[i*2])
                            pass
                    else :   # se temperatura não estiver maior que o limite, zera o contador
                        alarm_up_array[i*2] = 0

                    ### verifica se ultrapassou limite inferior
                    if temp_array[i*2] < lower_limit_total :
                        alarm_down_array[i*2] += 1
                        if alarm_down_array[i*2] > consecutive_limit :
                            turn_on_alarm()
                            

                            print(f"[{timestamp}] ALARME TEMPERATURA BAIXA --- Sensor {i*2} com temperatura de %.2f" % temp_array[i*2])
                            save_alarm_to_log(i*2,lower_limit_total,"Inferior",temp_array[i*2],"Sim",alarm_up_array[i*2])
                        else: 
                            save_alarm_to_log(i*2,lower_limit_total,"Inferior",temp_array[i*2],"Não",alarm_up_array[i*2])
                            pass
                    else :   # se temperatura não estiver menor que o limite, zera o contador
                        alarm_down_array[i*2] = 0

                else:    # se o sensor não estiver habilitado, salva a temperatura média na lista shm
                    temp_shm[i*2] = average_temp
                ####################################################################
                ### recorta os dados do segundo sensor #############################
                ####################################################################

                upper_limit_total = (average_temp + (upper_limit[32] if general_limit else upper_limit[(i*2)+1]) )
                lower_limit_total = (average_temp - (lower_limit[32] if general_limit else lower_limit[(i*2)+1]) )


                temp_array[(i*2)+1] = int(data_received[8:12],16)/100
                temp_shm[(i*2)+1] = int(data_received[8:12],16)/100

                ### verifica se o sensor está habilitado
                if enabled_sensor[(i*2)+1]:
                    ### verifica se ultrapassou limite superior
                    if temp_array[(i*2)+1] > upper_limit_total :
                        alarm_up_array[(i*2)+1] += 1
                        if alarm_up_array[(i*2)+1] > consecutive_limit :
                            turn_on_alarm()

                            print(f"[{timestamp}] ALARME TEMPERATURA ALTA --- Sensor {(i*2)+1} com temperatura de %.2f" % temp_array[(i*2)+1])
                            save_alarm_to_log((i*2)+1,upper_limit_total,"Superior",temp_array[(i*2)+1],"Sim",alarm_up_array[(i*2)+1])
                        else: 
                            save_alarm_to_log((i*2)+1,upper_limit_total,"Superior",temp_array[(i*2)+1],"Não",alarm_up_array[(i*2)+1])
                            pass
                    else :
                        alarm_up_array[(i*2)+1] = 0

                    ### verifica se ultrapassou limite inferior
                    if temp_array[(i*2)+1] < lower_limit_total :
                        alarm_down_array[(i*2)+1] += 1
                        if alarm_down_array[(i*2)+1] > consecutive_limit :
                            turn_on_alarm()

                            print(f"[{timestamp}] ALARME TEMPERATURA BAIXA --- Sensor {(i*2)+1} com temperatura de %.2f" % temp_array[(i*2)+1])
                            save_alarm_to_log((i*2)+1,lower_limit_total,"Inferior",temp_array[(i*2)+1],"Sim",alarm_up_array[(i*2)+1])
                        else: 
                            save_alarm_to_log((i*2)+1,lower_limit_total,"Inferior",temp_array[(i*2)+1],"Não",alarm_up_array[(i*2)+1])
                            pass

                    else :
                        alarm_down_array[(i*2)+1] = 0 
                else :   # se o sensor não estiver habilitado, salva a temperatura média na lista shm
                    temp_shm[(i*2)+1] = average_temp
            else:
                ################### ERRO DE LEITURA ######################
                temp_shm[i*2] = average_temp
                temp_shm[(i*2)+1] = average_temp

            delay_read_finish = round((time.time() * 1000 ) - delay_read_start)
            print(f"Read processing time: {delay_read_finish}ms")
            if delay_read_finish < CONST_READ_DELAY :
                time.sleep((CONST_READ_DELAY-delay_read_finish)/1000)
            else :
                pass
                #time.sleep(0.01)
                

        check_update_from_interface()
        
        if alarm_on :
            if ((max(alarm_down_array) < consecutive_limit) and (max(alarm_up_array) < consecutive_limit)) :
                turn_off_alarm()
                pass
            else :
                turn_on_alarm()
                pass


        check_Alarm()

        with open(csv_file_path_temp, mode='a', newline='') as csv_file_temp:
            csv_writer_temp = csv.writer(csv_file_temp)
            csv_writer_temp.writerow([timestamp, temp_array[0], temp_array[1], temp_array[2], temp_array[3]
                                        , temp_array[4], temp_array[5], temp_array[6], temp_array[7]
                                        , temp_array[8], temp_array[9], temp_array[10], temp_array[11]
                                        , temp_array[12], temp_array[13], temp_array[14], temp_array[15]
                                        , temp_array[16], temp_array[17], temp_array[18], temp_array[19]
                                        , temp_array[20], temp_array[21], temp_array[22], temp_array[23]
                                        , temp_array[24], temp_array[25], temp_array[26], temp_array[27]
                                        , temp_array[28], temp_array[29], temp_array[30], temp_array[31]
                                        , alarm_on, check_GA(), modo ])

        for i in range(len(temp_array)):
            temp_max_array[i] = max(temp_max_array[i],temp_array[i])
            if temp_array[i] != 0.0 :
                if temp_min_array[i] == 0.0 :
                    temp_min_array[i] = temp_array[i]
                else :
                    temp_min_array[i] = min(temp_min_array[i],temp_array[i])

        
        tsensor_pipe["temperature"] = temp_shm.tolist()
        tsensor_pipe["temperature_max"] = temp_max_array.tolist()
        tsensor_pipe["temperature_min"] = temp_min_array.tolist()
        tsensor_pipe["estado"] = alarm_on


        ####################################################################
        ##### Cálculo da média de temperaturas #############################
        ####################################################################
        average_array = np.zeros(32, dtype='float32')
        for i in range(32):
            average_array[i] = temp_array[i] if enabled_sensor[i] else 0

        read_count = np.count_nonzero(average_array)   # verifica quantas temperaturas são diferentes de 0
        if read_count != 0 :
            average_temp = np.sum(average_array)/read_count
        else :
            average_temp = 0.0
        tsensor_pipe["media"] = average_temp





        if read_count != 32:                #verifica se tem falha na leitura dos sensores
            reboot_sensor_count+=1
            if reboot_sensor_count > 600:   #se tiver por mais de 10min (600 leituras) com sensores faltando, reinicia haste     
                reiniciar_haste(2,3)
                reboot_sensor_count = 0
        else:
            reboot_sensor_count = 0        #se estiver OK, zera o contador



        frame_finish = round((time.time() * 1000 ) - frame_start)
        print(f"Total processing time: {frame_finish}ms")
        print(f"array: {temp_array}")
        if frame_finish < CONST_READ_TIME :
            time.sleep((CONST_READ_TIME-frame_finish)/1000)
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
    tsensor_pipe.shm.close()
