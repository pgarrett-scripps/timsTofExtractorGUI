import timsdata, sys, os
import numpy as np
from scipy import constants
import sqlite3
from sqlite3 import Error
import glob
import time
from datetime import datetime

from dia_frame import DiaFrame
from ms_string_templates import header_ms2_template, header_ms1_template, \
    dda_ms2_scan_template

place_high = 3
precursor_counter = 0
convert_ms2 = True
convert_ms1 = True
rename = True
version = "0.2.1"


def K0toCCS(K0, q, m_ion, m_gas, T):
    mu = m_ion * m_gas / (m_ion + m_gas)
    T0 = 273.15
    p0 = 1.0132e5  # 1 atm
    N0 = p0 / (constants.k * T0)
    return (3.0 / 16.0) * (1 / N0) * np.sqrt(2 * np.pi / (mu * constants.k * T)) * (q / K0)


def enhance_signal(intensity):
    return (intensity ** 1.414 + 100.232) ** 1.414


def create_connection(analysis_dir):
    import os
    db_file = os.path.join(analysis_dir, 'analysis.tdf')
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


def select_all_PasefFrameMsMsInfo(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM PasefFrameMsMsInfo")

    rows = cur.fetchall()

    data_all = np.array(rows)
    return data_all


def select_all_Frames(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM Frames")

    rows = cur.fetchall()

    data_all = np.array(rows)
    return data_all


def select_all_Precursors(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM Precursors")

    rows = cur.fetchall()

    data_all = np.array(rows)
    return data_all


def select_all_dia_frames(conn):
    cur = conn.cursor()
    rows = cur.execute('select DiaFrameMsMsWindows.windowgroup, frame, scannumbegin, scannumend, IsolationMz, '
                       'IsolationWidth, CollisionEnergy, Frames.time  from DiaFrameMsMsWindows join DiaFrameMsMsInfo on '
                       'DiaFrameMsMsWindows.windowgroup = DiaFrameMsMsInfo.windowgroup '
                       'join Frames on DiaFrameMsMsInfo.Frame = Frames.id')

    dia_list = [
        DiaFrame(window_group=window_group, frame=frame, scan_num_begin=scan_num_begin, scan_num_end=scan_num_end,
                 isolation_mz=isolation_mz, isolation_width=isolation_width, collision_energy=collision_energy, time=time)
        for window_group, frame, scan_num_begin, scan_num_end, isolation_mz, isolation_width, collision_energy,
            time in rows]

    return dia_list


def build_frame_id_ms1_scan_map(precursor_map, all_ms1_list):
    frame_id_ms1_scan_map = {}
    ms2_map = {}
    prev_scan = 0
    for row in all_ms1_list:
        frame_id = int(row[0])
        prev_scan += 1
        frame_id_ms1_scan_map[frame_id] = prev_scan
        if frame_id in precursor_map:
            if frame_id not in ms2_map:
                ms2_map[frame_id] = {}
            for count, rows in enumerate(precursor_map[frame_id], prev_scan + 1):
                prec_id = int(rows[0])
                ms2_map[frame_id][prec_id] = count
            prev_scan += len(precursor_map[frame_id])
    return frame_id_ms1_scan_map, ms2_map


def build_dia_frame_id_ms1_scan_map(all_ms1_frame, frame_dia_map):
    prev_scan = 0
    frame_id_ms1_scan_map = {}
    ms2_map = {}
    for row in all_ms1_frame:
        frame_id = int(row[0])
        prev_scan += 1
        frame_id_ms1_scan_map[frame_id] = prev_scan
        if frame_id in frame_dia_map:
            for dia in frame_dia_map[frame_id]:
                prev_scan += 1
                ms2_map.setdefault(dia.window_group, {})[dia.scan_num_begin] = prev_scan
    return frame_id_ms1_scan_map, ms2_map


def create_mz_int_spectra(mz_int_arr):
    mz_arr = mz_int_arr[0]
    str_list = []
    int_arr = mz_int_arr[1]
    for j in range(0, len(mz_arr)):
        str_list.append("%.4f %.1f \n" % (mz_arr[j], int_arr[j]))
    return ''.join([row for row in str_list])


def create_dia_ms2_file(td, dia_list):
    with open(ms2_file_name, 'w') as output_file:
        progress = 0
        filler_num = 1
        for dia in dia_list:
            scan_num_arr = [scan_num for scan_num in range(dia.scan_num_begin, dia.scan_num_end)]
            one_over_k0_arr = td.scanNumToOneOverK0(dia.frame, scan_num_arr)
            index_intensity_arr = td.readScans(dia.frame, dia.scan_num_begin, dia.scan_num_end)
            index_intensity_carr = np.concatenate(index_intensity_arr, axis=1)
            index_arr = index_intensity_carr[0]
            mass_array = td.indexToMz(dia.frame, index_arr)
            index_mass_dict = dict(zip(index_arr, mass_array))
            spectra = []
            for scan_num_index, row in enumerate(index_intensity_arr):
                ook0 = one_over_k0_arr[scan_num_index]
                for ii in range(len(row[0])):
                    mz = index_mass_dict[row[0][ii]]
                    intensity = row[1][ii]
                    spectra.append((mz, intensity, ook0))
            spectra.sort(key=lambda tup: tup[0])
            scan_head = dia.get_scan_head(filler_num)
            output_file.write(scan_head)
            for mz, intensity, ook0 in spectra:
                output_file.write("{:.4f} {:.4f} {:.4f}\n".format(mz, intensity, ook0))
            filler_num += 1


def create_dda_ms2_file(td, precursor_list, ms2_scan_map, all_frame, date_now, ms2_file_name):
    with open(ms2_file_name, 'w') as output_file:
        ms2_header = header_ms2_template.format(version=version, date_of_creation=date_now, first_scan=-1, last_scan=-1)
        output_file.write(ms2_header)
        progress = 0
        for row in precursor_list:
            prc_id, largest_preak_mz, average_mz, monoisotopic_mz, cs, scan_number, intensity, parent = row
            prc_id_int = int(prc_id)
            if monoisotopic_mz is not None and cs is not None and cs > 1:
                mz_int_arr = td.readPasefMsMs([prc_id_int])[prc_id_int]
                if len(mz_int_arr[0]) > 0:
                    prc_mass_mz = float(monoisotopic_mz)
                    prc_mass = (prc_mass_mz * cs) - (cs - 1) * 1.007276466
                    parent_index = int(parent)
                    scan_id = ms2_scan_map[parent_index][prc_id_int]
                    rt_time = float(all_frame[parent_index - 1][1])
                    k0 = td.scanNumToOneOverK0(parent_index, [scan_number])[0]
                    scan_head = dda_ms2_scan_template.format(scan_id=scan_id, prc_mass_mz=prc_mass_mz,
                                                             parent_index=parent_index, prc_id=prc_id_int,
                                                             ret_time=rt_time, k0=k0, cs=int(cs), prc_mass=prc_mass)
                    spectra = create_mz_int_spectra(mz_int_arr)
                    output_file.write(scan_head)
                    output_file.write(spectra)
            progress += 1
            if progress % 5000 == 0:
                print("progress ms2: %.1f%%" % (float(progress) / len(precursor_list) * 100),
                      time.process_time() - start_time)


def run_timstof_conversion(input, output='', dia_mode=False, convert_ms2=True, convert_ms1=False):
    global place_high
    global precursor_counter
    analysis_dir = input

    td = timsdata.TimsData(analysis_dir)
    conn = td.conn

    ms2_file_name = os.path.basename(analysis_dir).split('.')[0] + '.ms2'
    ms1_file_name = os.path.basename(analysis_dir).split('.')[0] + '.ms1'

    if len(output) > 0:
        ms2_file_name = output
        ms1_file_name = output.replace('.ms2', '.ms1')

    d = str(datetime.now().strftime("%B %d, %Y %H:%M"))
    if dia_mode:
        with conn:
            all_frame = select_all_Frames(conn)
            all_ms1_frames = [a for a in all_frame if a[4] == '0']
            dia_frame_list = select_all_dia_frames(conn)
            frame_dia_map = {}
            for dia in dia_frame_list:
                frame_dia_map.setdefault(dia.frame, []).append(dia)
            #build_dia_frame_id_ms1_scan_map(all_ms1_frames, frame_dia_map)
            create_dia_ms2_file(td, dia_frame_list)
    else:
        precursor_map = {}
        with conn:
            # print("2. Query all tasks")
            msms_data = select_all_PasefFrameMsMsInfo(conn)
            # print msms_data[0:5]
            all_frame = select_all_Frames(conn)
            # print all_frame[0:5]
            if not dia_mode:
                precursor_list = select_all_Precursors(conn)
                for row in precursor_list:
                    parent_id = int(row[-1])
                    if parent_id not in precursor_map:
                        precursor_map[parent_id] = []
                    precursor_map[parent_id].append(row)

        all_ms1_frames = [a for a in all_frame if a[4] == '0']

        frame_id_ms1_scan_map, ms2_scan_map = build_frame_id_ms1_scan_map(precursor_map, all_ms1_frames)
        if convert_ms2:
            create_dda_ms2_file(td=td, precursor_list=precursor_list, all_frame=all_frame, date_now=d,
                                ms2_scan_map=ms2_scan_map, ms2_file_name=os.path.join(analysis_dir, ms2_file_name))
        if convert_ms1:
            ms1_header = header_ms1_template.format(version)
            with open(ms1_file_name, 'w') as output_file:
                output_file.write(ms1_header)
                progress = 0
                prev_id = 0
                # scan_set = set()
                prev_scan = 0
                precursor_counter = 0
                lines = []
                for i, frame in enumerate(all_ms1_frames):
                    id = int(frame[0])
                    num_scans = int(frame[8])

                    index_intensity_arr = td.readScans(id, 0, num_scans)
                    index_intensity_carr = np.concatenate(index_intensity_arr, axis=1)
                    mobility_index = [i for i, row in enumerate(index_intensity_arr) for j in range(len(row[0]))]

                    mass_array = td.indexToMz(id, index_intensity_carr[0])
                    one_over_k0 = td.scanNumToOneOverK0(id, mobility_index)
                    voltage = td.scanNumToVoltage(id, mobility_index)
                    temp = np.array(list(zip(mass_array, index_intensity_carr[1], one_over_k0, voltage)))
                    mass_intensity = np.around(temp, decimals=4)
                    sorted_mass_intensity = mass_intensity[mass_intensity[:, 0].argsort()]
                    scan_num = frame_id_ms1_scan_map[id]
                    if len(sorted_mass_intensity) > 0:
                        rt_time = 0 if i == 0 else all_ms1_frames[i - 1][1]
                        lines.append("S\t%06d\t%06d\n" % (scan_num, scan_num))
                        lines.append("I\tTIMSTOF_Frame_id\t{}\n".format(id))
                        lines.append("I\tRetTime\t%.2f\n" % float(rt_time))
                        for row in sorted_mass_intensity:
                            x_str = "%.4f %.1f %.4f \n" % (row[0], row[1], row[-2])
                            lines.append(x_str)
                    # output_file.write("S\t%06d\t%06d\n" % (scan_num, scan_num))
                    # output_file.write("I\tTIMSTOF_Frame_id\t{}\n".format(id))
                    # output_file.write("I\tRetTime\t%.2f\n" % float(rt_time))
                    # output_file.writelines("%.4f %.1f %.4f\n" % (row[0], row[1],
                    # row[-1]) for row in sorted_mass_intensity)
                    if len(lines) > 1_000_000:
                        output_file.writelines(lines)
                        lines = []

                    progress += 1
                    if progress % 5000 == 0:
                        yield (float(progress) / len(precursor_list) * 100)
                output_file.writelines(lines)
                lines = []
    conn.close()
    if rename:
        for file in os.listdir(analysis_dir):
            if file == "analysis.tdf":
                tdf_new_name = ms2_file_name.replace(".ms2",".tdf")
                os.rename(os.path.join(analysis_dir, file), tdf_new_name)
            if file == "analysis.tdf_bin":
                tdf_bin_new_name = ms2_file_name.replace(".ms2", ".tdf_bin")
                os.rename(os.path.join(analysis_dir, file), tdf_bin_new_name)



def is_valid_timstof_dir(path):
    if os.path.isdir(path):
        tdf_file = os.path.join(path, "analysis.tdf")
        if os.path.exists(tdf_file):
            return True
    return False
