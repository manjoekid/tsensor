import time
import csv
import numpy as np
import modbus_connect as modbus
import util_tsensor as utils
from shared_memory_dict import SharedMemoryDict
from global_vars import current_hour, current_hour_alarm, alarm_on, average_temp,modo, temp_array, temp_shm

CONST_READ_DELAY = 60
CONST_READ_TIME = 1000

CONST_UPPER_LIMIT       = 7.0  # limite superior de temperatura. O valor deve ser superior para iniciar contagem. Por exemplo, se limite é 7.0, o alarme vai acionar quando alcançar 7º acima da média
CONST_LOWER_LIMIT       = 7.0  # limite inferior de temperatura. O valor deve ser inferior para iniciar contagem. Por exemplo, se limite é 7.0, o alarme vai acionar quando alcançar 7º abaixo da média
CONST_CONSECUTIVE_LIMIT = 7     # limite de medidas acima da temperatura para acionar alarme. Por exemplo se limite é 5, o alarme vai acionar quando for realizada a 6 leitura consecutiva acima ou abaixo do limite


### inicializa array com os valores máximos encontrados
temp_max_array = np.zeros(32, dtype='float32')
### inicializa array com os valores máximos encontrados
temp_min_array = np.zeros(32, dtype='float32')

tsensor_pipe = SharedMemoryDict(name='temperatures', size=4096)
tsensor_pipe["estado"] = True
tsensor_pipe["estado_ga"] = False
tsensor_pipe["limite_superior"] = CONST_UPPER_LIMIT
tsensor_pipe["limite_inferior"] = CONST_LOWER_LIMIT
tsensor_pipe["modo"] = modo
tsensor_pipe["media"] = average_temp
tsensor_pipe["temperature"] = temp_max_array.tolist()
tsensor_pipe["temperature_max"] = temp_max_array.tolist()
tsensor_pipe["temperature_min"] = temp_max_array.tolist()


try:
    
    alarm_up_array = np.zeros(32, dtype='int')
    alarm_down_array = np.zeros(32, dtype='int')
    #print_erro("Sistema inicializado")

    #turn_off_alarm()
    modbus.check_Alarme()

    modbus.inicializa_haste()

    while True:
        ### inicia marcação de tempo para que cada leitura seja feita em intervalos de 1s
        frame_start = time.time() * 1000

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 

        if current_hour == 0 :
            current_hour = time.localtime().tm_hour 
            utils.create_csv_file()
        
        # Check if the hour has changed
        utils.update_csv_file()

        ### inicia a contagem de 16 controladores
        for i in range(16):

            ### inicia a marcação de tempo de leitura para evitar sobrecarregar o buffer da serial
            delay_read_start = time.time() * 1000

            data_received = modbus.read_controller(i)

            upper_limit = average_temp + CONST_UPPER_LIMIT
            lower_limit = average_temp - CONST_LOWER_LIMIT

            if ((data_received[:4] == "2165") and (len(data_received) == 12)):

                ####################################################################
                ### recorta os dados do primeiro sensor ############################
                ####################################################################
                temp_array[i*2] = int(data_received[4:8],16)/100
                temp_shm[i*2] = int(data_received[4:8],16)/100
                ### verifica se ultrapassou limite superior
                if temp_array[i*2] > upper_limit :
                    alarm_up_array[i*2] += 1
                    if alarm_up_array[i*2] > CONST_CONSECUTIVE_LIMIT :
                        modbus.turn_on_alarm()
                        

                        print(f"[{timestamp}] ALARME TEMPERATURA ALTA --- Sensor {i*2} com temperatura de %.2f" % temp_array[i*2])
                        #save_alarm_to_csv(i*2,upper_limit,"Superior",temp_array[i*2],"Sim",alarm_up_array[i*2])
                    else: 
                        #save_alarm_to_csv(i*2,upper_limit,"Superior",temp_array[i*2],"Não",alarm_up_array[i*2])
                        pass
                else :
                    alarm_up_array[i*2] = 0

                ### verifica se ultrapassou limite inferior
                if temp_array[i*2] < lower_limit :
                    alarm_down_array[i*2] += 1
                    if alarm_down_array[i*2] > CONST_CONSECUTIVE_LIMIT :
                        modbus.turn_on_alarm()
                        

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
                if temp_array[(i*2)+1] > upper_limit :
                    alarm_up_array[(i*2)+1] += 1
                    if alarm_up_array[(i*2)+1] > CONST_CONSECUTIVE_LIMIT :
                        modbus.turn_on_alarm()

                        print(f"[{timestamp}] ALARME TEMPERATURA ALTA --- Sensor {(i*2)+1} com temperatura de %.2f" % temp_array[(i*2)+1])
                        #save_alarm_to_csv((i*2)+1,upper_limit,"Superior",temp_array[(i*2)+1],"Sim",alarm_up_array[(i*2)+1])
                    else: 
                        #save_alarm_to_csv((i*2)+1,upper_limit,"Superior",temp_array[(i*2)+1],"Não",alarm_up_array[(i*2)+1])
                        pass
                else :
                    alarm_up_array[(i*2)+1] = 0

                ### verifica se ultrapassou limite inferior
                if temp_array[(i*2)+1] < lower_limit :
                    alarm_down_array[(i*2)+1] += 1
                    if alarm_down_array[(i*2)+1] > CONST_CONSECUTIVE_LIMIT :
                        modbus.turn_on_alarm()

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

        if tsensor_pipe["modo"] != modo :
            modo = tsensor_pipe["modo"]
            if modo == 'ligado':
                modbus.turn_on_alarm()
            else :
                modbus.turn_off_alarm()

        if alarm_on :
            if ((max(alarm_down_array) < CONST_CONSECUTIVE_LIMIT) and (max(alarm_up_array) < CONST_CONSECUTIVE_LIMIT)) :
                modbus.turn_off_alarm()
                pass
            else :
                modbus.turn_on_alarm()
                pass
        
        utils.save_data_csv()

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
