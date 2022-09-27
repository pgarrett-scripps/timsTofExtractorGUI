import timsdata
import numpy as np

analysis_dir = "/home/yateslab/projectData/census/1610Timstof/projects2020_05_26_07_167734/IP_B07_CPP_rep1_1over10_052020_S4-A1_1_2059.d/"
td = timsdata.TimsData(analysis_dir)
conn = td.conn
cursor = conn.cursor();
param = (1700, 1800)
id_list = []
for row in cursor.execute("SELECT Id, NumScans FROM FRAMES WHERE TIME BETWEEN ? AND ? and MsMsType = 0 ",param):
    id_list.append(row)

filtered_peaks = []
peak_dict={}
total_peaks = 0

for id, num_scans in id_list:
    for scan_row in td.readScans(id, 0, num_scans):
        if len(scan_row[0]) > 0 :
            for entry in scan_row:
                print(entry)
    index_intensity_arr = td.readScans(id, 0, num_scans)
    index_intensity_carr = np.concatenate(index_intensity_arr, axis=1)
    mobility_index = [i for i, row in enumerate(index_intensity_arr) for j in range(len(row[0]))]

    mass_array = td.indexToMz(id, index_intensity_carr[0])
   # print(len(mass_array))
    one_over_k0 = td.scanNumToOneOverK0(id, mobility_index)
    voltage = td.scanNumToVoltage(id, mobility_index)
    temp = np.array(list(zip(mass_array, index_intensity_carr[1], one_over_k0, voltage, index_intensity_carr[0])))
   # peak_list = np.around(temp, decimals=4)
    total_peaks += len(temp)
    for peak in temp:
        if 877.464 < peak[0] < 877.499:
            #print(peak[-1])
            if peak[0] in peak_dict:
                peak_dict[peak[0]] += peak_dict[peak[0]] + peak[1]
            else:
                peak_dict[peak[0]] = peak[1]
            filtered_peaks.append(peak)

print(len(filtered_peaks))
print(total_peaks)
filtered_peaks.sort(key = lambda x: x[0])
for peak, intensity in peak_dict.items():
    print(peak, intensity)


conn.close()
