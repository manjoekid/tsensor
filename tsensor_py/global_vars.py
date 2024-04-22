import time
import numpy as np 

current_hour = 0
current_hour_alarm = 0

alarm_on = True
modo = 'auto'

average_temp = 0.0   #temperatura média 

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

csv_file_temp = ''
### zera o array de temperaturas
temp_array = np.zeros(32, dtype='float32')      ## ARRAY COM VALORES QUE SÃO ENVIADOS PARA CSV
temp_shm = np.zeros(32, dtype='float32')        ## ARRAY COM VALORES QUE SÃO ENVIADOS PARA PÁGINA DO USUÁRIO - sem valores zerados
