

def mz_to_mh(mz, cs):
    return (mz * cs) - (cs - 1) * 1.007276466


class DiaFrame:
    dia_ms2_scan_template = "S\t{scan_id:06d}\t{scan_id:06d}\t{isolation_mz:.4f}\n" \
                            "I\tTIMSTOF_Frame_ID\t{frame}\n" \
                            "I\tTIMSTOF_WindowGroup_ID\t{window_group}\n" \
                            "I\tTIMSTOF_Scan_Begin\t{scan_begin}\n" \
                            "I\tRetTime\t{ret_time:.4f}\n" \
                            "I\tIsolationMz\t{isolation_mz:.4f}\n" \
                            "I\tIsolationWidth\t{isolation_width:.4f}\n" \
                            "I\tCollisionEnergy\t{collision_energy:.4f}\n" \
                            "Z\t2\t{mh2:.4f}\n" \
                            "Z\t3\t{mh3:.4f}\n"

    def __init__(self, window_group, frame, scan_num_begin, scan_num_end, isolation_mz, isolation_width,
                 collision_energy, time):
        self.scan_num_end = int(scan_num_end)
        self.isolation_mz = float(isolation_mz)
        self.isolation_width = float(isolation_width)
        self.collision_energy = float(collision_energy)
        self.scan_num_begin = int(scan_num_begin)
        self.window_group = int(window_group)
        self.frame = int(frame)
        self.time = float(time)

    def get_scan_head(self, scan_id):
        mh2 = mz_to_mh(self.isolation_mz, 2)
        mh3 = mz_to_mh(self.isolation_mz, 3)
        return DiaFrame.dia_ms2_scan_template.format(scan_id=scan_id, frame=self.frame, window_group=self.window_group,
                                                     scan_begin=self.scan_num_begin, ret_time=self.time,
                                                     isolation_mz=self.isolation_mz,
                                                     isolation_width=self.isolation_width,
                                                     collision_energy=self.collision_energy, mh2=mh2, mh3=mh3)
