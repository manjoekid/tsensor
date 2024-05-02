import serial
import time
import csv
import os
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

    upper_limit = float(os.getenv('upper_limit',default='7.0')) # limite superior de temperatura. O valor deve ser superior para iniciar contagem. Por exemplo, se limite é 7.0, o alarme vai acionar quando alcançar 7º acima da média
    lower_limit = float(os.getenv('lower_limit',default='7.0'))  # limite inferior de temperatura. O valor deve ser inferior para iniciar contagem. Por exemplo, se limite é 7.0, o alarme vai acionar quando alcançar 7º abaixo da média
    consecutive_limit = int(os.getenv('consecutive_limit',default='7'))     # limite de medidas acima da temperatura para acionar alarme. Por exemplo se limite é 5, o alarme vai acionar quando for realizada a 6 leitura consecutiva acima ou abaixo do limite

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
tsensor_pipe["limite_consecutivo"] = consecutive_limit
tsensor_pipe["modo"] = modo
tsensor_pipe["media"] = average_temp
tsensor_pipe["temperature"] = temp_max_array.tolist()
tsensor_pipe["temperature_max"] = temp_max_array.tolist()
tsensor_pipe["temperature_min"] = temp_max_array.tolist()




def save_alarm_to_csv(sensor,temp_limite,limite,temperatura,acionamento,contagem):
    global csv_file_path_alarm
    global current_hour_alarm
    global csv_file_alarm
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

    with open(csv_file_path_temp, mode='a', newline='') as csv_file_temp:
            csv_writer_temp = csv.writer(csv_file_temp)
            csv_writer_temp.writerow([timestamp, "Alarme", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
                                               , "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""
                                               ,sensor,temp_limite, limite,temperatura,acionamento,contagem])


def turn_off_alarm():
    global alarm_on

    if tsensor_pipe["modo"] == 'desligado' :
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 


        # Writing data to the TCP port

        data_received_mod = tcp_modbus.write_single_register(500, 0)    #Desliga alarme
        alarm_on = False
        tsensor_pipe["estado"] = False
        
        set_key(find_dotenv(), 'alarm_on', 'False')   #salva estado do alarme no '.env'

        print(f"[{timestamp}] Turning off Alarm - Data written: (500, 0)")
        # Reading data from the RS485 port
        #print_erro("Desligando Alarme")
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

            data_received_mod = tcp_modbus.write_single_register(500, 1)    #Liga alarme


            print(f"[{timestamp}] Turning alarm on - Data written: (500, 1)")
            #print_erro("Ligando Alarme")

            print(f"Data received from Modbus: {data_received_mod}")
            alarm_on = True
            tsensor_pipe["estado"] = True

            set_key(find_dotenv(), 'alarm_on', 'True')   #salva estado do alarme no '.env'

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
        set_key(find_dotenv(), 'alarm_on', 'True')   #salva estado do alarme no '.env'
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

def return_alarm_to_state(alarm_saved_state):
    if (alarm_saved_state != check_Alarm()):
        alarm_state = 1 if alarm_saved_state else 0
        data_received_mod = tcp_modbus.write_single_register(500, alarm_state)    #Liga/desliga alarme
        alarm_on = alarm_state
        tsensor_pipe["estado"] = alarm_on
        print(f"Inicializando o alarme conforme dados salvos '.env'. Modbus retornou: {data_received_mod}")


def check_Alarm():
    global alarm_on
    # Reading data to the TCP port
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 
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
    global modo,upper_limit,lower_limit,consecutive_limit
    if tsensor_pipe["modo"] != modo :
        modo = tsensor_pipe["modo"]
        set_key(find_dotenv(), 'modo', modo)   #salva estado do alarme no '.env'
        if modo == 'ligado':
            turn_on_alarm()
        else :
            turn_off_alarm()
    if tsensor_pipe["limite_superior"] != upper_limit :
        upper_limit = tsensor_pipe["limite_superior"]
        set_key(find_dotenv(), 'upper_limit', str(upper_limit))   #salva estado do alarme no '.env'
    
    if tsensor_pipe["limite_inferior"] != lower_limit :
        lower_limit = tsensor_pipe["limite_inferior"]
        set_key(find_dotenv(), 'lower_limit', str(lower_limit))   #salva estado do alarme no '.env'

    if tsensor_pipe["limite_consecutivo"] != consecutive_limit :
        consecutive_limit = tsensor_pipe["limite_consecutivo"]
        set_key(find_dotenv(), 'consecutive_limit', str(consecutive_limit))   #salva estado do alarme no '.env'


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


try:
    
    alarm_up_array = np.zeros(32, dtype='int')
    alarm_down_array = np.zeros(32, dtype='int')
    #print_erro("Sistema inicializado")

    return_alarm_to_state(alarm_on)   #retorna alarme para o estado inicial gravado no '.env'

    inicializa_haste()

    while True:
        ### inicia marcação de tempo para que cada leitura seja feita em intervalos de 1s
        frame_start = time.time() * 1000

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

        if current_hour == 0 :
            current_hour = time.localtime().tm_hour 
            with open(csv_file_path_temp, mode='w', newline='') as csv_file_temp:
                csv_writer_temp = csv.writer(csv_file_temp)
                csv_writer_temp.writerow(csv_header_temp)  # Write the header to the CSV file
        
        # Check if the hour has changed

        if time.localtime().tm_hour != current_hour:
            current_hour = time.localtime().tm_hour 
            if csv_file_path_temp:
                csv_file_temp.close()

            # Create a new CSV file
            current_datetime = time.strftime("%Y%m%d_%H%M%S")
            csv_file_path_temp = f'./output/output_temp_{current_datetime}.csv'
            with open(csv_file_path_temp, mode='w', newline='') as csv_file_temp:
                csv_writer_temp = csv.writer(csv_file_temp)
                csv_writer_temp.writerow(csv_header_temp)  # Write the header to the CSV file
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


            upper_limit_total = average_temp + upper_limit
            lower_limit_total = average_temp - lower_limit

            if ((data_received[:4] == "2165") and (len(data_received) == 12)):

                ####################################################################
                ### recorta os dados do primeiro sensor ############################
                ####################################################################
                temp_array[i*2] = int(data_received[4:8],16)/100
                temp_shm[i*2] = int(data_received[4:8],16)/100
                ### verifica se ultrapassou limite superior
                if temp_array[i*2] > upper_limit_total :
                    alarm_up_array[i*2] += 1
                    if alarm_up_array[i*2] > consecutive_limit :
                        turn_on_alarm()
                        

                        print(f"[{timestamp}] ALARME TEMPERATURA ALTA --- Sensor {i*2} com temperatura de %.2f" % temp_array[i*2])
                        #save_alarm_to_csv(i*2,upper_limit,"Superior",temp_array[i*2],"Sim",alarm_up_array[i*2])
                    else: 
                        #save_alarm_to_csv(i*2,upper_limit,"Superior",temp_array[i*2],"Não",alarm_up_array[i*2])
                        pass
                else :
                    alarm_up_array[i*2] = 0

                ### verifica se ultrapassou limite inferior
                if temp_array[i*2] < lower_limit_total :
                    alarm_down_array[i*2] += 1
                    if alarm_down_array[i*2] > consecutive_limit :
                        turn_on_alarm()
                        

                        print(f"[{timestamp}] ALARME TEMPERATURA BAIXA --- Sensor {i*2} com temperatura de %.2f" % temp_array[i*2])
                        #save_alarm_to_csv(i*2,lower_limit,"Inferior",temp_array[i*2],"Sim",alarm_up_array[i*2])
                    else: 
                        #save_alarm_to_csv(i*2,lower_limit,"Inferior",temp_array[i*2],"Não",alarm_up_array[i*2])
                        pass
                else :
                    alarm_down_array[i*2] = 0

                ####################################################################
                ### recorta os dados do segundo sensor #############################
                ####################################################################
                temp_array[(i*2)+1] = int(data_received[8:12],16)/100
                temp_shm[(i*2)+1] = int(data_received[8:12],16)/100
                ### verifica se ultrapassou limite superior
                if temp_array[(i*2)+1] > upper_limit_total :
                    alarm_up_array[(i*2)+1] += 1
                    if alarm_up_array[(i*2)+1] > consecutive_limit :
                        turn_on_alarm()

                        print(f"[{timestamp}] ALARME TEMPERATURA ALTA --- Sensor {(i*2)+1} com temperatura de %.2f" % temp_array[(i*2)+1])
                        #save_alarm_to_csv((i*2)+1,upper_limit,"Superior",temp_array[(i*2)+1],"Sim",alarm_up_array[(i*2)+1])
                    else: 
                        #save_alarm_to_csv((i*2)+1,upper_limit,"Superior",temp_array[(i*2)+1],"Não",alarm_up_array[(i*2)+1])
                        pass
                else :
                    alarm_up_array[(i*2)+1] = 0

                ### verifica se ultrapassou limite inferior
                if temp_array[(i*2)+1] < lower_limit_total :
                    alarm_down_array[(i*2)+1] += 1
                    if alarm_down_array[(i*2)+1] > consecutive_limit :
                        turn_on_alarm()

                        print(f"[{timestamp}] ALARME TEMPERATURA BAIXA --- Sensor {(i*2)+1} com temperatura de %.2f" % temp_array[(i*2)+1])
                        #save_alarm_to_csv((i*2)+1,lower_limit,"Inferior",temp_array[(i*2)+1],"Sim",alarm_up_array[(i*2)+1])
                    else: 
                        #save_alarm_to_csv((i*2)+1,lower_limit,"Inferior",temp_array[(i*2)+1],"Não",alarm_up_array[(i*2)+1])
                        pass

                else :
                    alarm_down_array[(i*2)+1] = 0 
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


        read_count = np.count_nonzero(temp_array)
        if read_count != 0 :
            average_temp = np.sum(temp_array)/read_count
        else :
            average_temp = 0.0
        tsensor_pipe["media"] = average_temp

        if read_count != 32:
            reiniciar_haste()

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
    #print_erro("Programa finalizado pelo usuário")
except serial.SerialTimeoutException:
    print("Program terminated by SerialTimeoutException. Modbus not connected or error")
    #print_erro("Programa finalizado por exceção ou com erro")
finally:
    # Close the serial port
    ser_sensor.close()
    csv_file_temp.close()
    tsensor_pipe.shm.close()
