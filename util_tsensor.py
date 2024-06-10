import time
import csv
import modbus_connect as modbus
from global_vars import modo, current_hour, csv_file_path_temp, csv_header_temp, csv_file_temp, temp_array



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


def create_csv_file():
    global csv_file_temp
    with open(csv_file_path_temp, mode='w', newline='') as csv_file_temp:
        csv_writer_temp = csv.writer(csv_file_temp)
        csv_writer_temp.writerow(csv_header_temp)  # Write the header to the CSV file

def update_csv_file():
    global csv_file_temp
    if time.localtime().tm_hour != current_hour:
        current_hour = time.localtime().tm_hour 
        if csv_file_path_temp:
            csv_file_temp.close()

        # Create a new CSV file
        current_datetime = time.strftime("%Y%m%d_%H%M%S")
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 
        csv_file_path_temp = f'./output/output_temp_{current_datetime}.csv'
        with open(csv_file_path_temp, mode='w', newline='') as csv_file_temp:
            csv_writer_temp = csv.writer(csv_file_temp)
            csv_writer_temp.writerow(csv_header_temp)  # Write the header to the CSV file
            print(f"[{timestamp}] Creating a new CSV file for the new hour.")

def save_data_csv():
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S') 
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
                                    , modbus.check_Alarme(), modbus.check_GA(), modo ])
