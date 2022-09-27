
header_ms2_template = 'H\tExtractor\tTimsTOF_extractor\n' \
                 'H\tExtractorVersion\t{version}\n' \
                 'H\tPublicationDate\t20-02-2020\n' \
                 'H\tDate Converted\t{date_of_creation}\n' \
                 'H\tComments\tTimsTOF_extractor written by Yu Gao, 2018\n' \
                 'H\tComments\tTimsTOF_extractor modified by Titus Jung, 2019\n' \
                 'H\tExtractorOptions\tMSn\n' \
                 'H\tAcquisitionMethod\tData-Dependent\n' \
                 'H\tInstrumentType\tTIMSTOF\n' \
                 'H\tDataType\tCentroid\n' \
                 'H\tScanType\tMS2\n' \
                 'H\tResolution\n' \
                 'H\tIsolationWindow\n' \
                 'H\tFirstScan\t{first_scan:d}\n' \
                 'H\tLastScan\t{last_scan:d}\n' \
                 'H\tMonoIsotopic PrecMz\tTrue\n'

header_ms1_template = 'H\tExtractor\tTimsTOF_extractor\n' \
                 'H\tExtractorVersion\t{}\n' \
                 'H\tPublicationDate\t20-02-2020\n' \
                 'H\tComments\tTimsTOF_extractor written by Yu Gao, 2018\n' \
                 'H\tComments\tTimsTOF_extractor modified by Titus Jung, 2019\n' \
                 'H\tExtractorOptions\tMSn\n' \
                 'H\tAcquisitionMethod\tData-Dependent\n' \
                 'H\tInstrumentType\tTIMSTOF\n' \
                 'H\tScanType\tMS1\n'


dda_ms2_scan_template = "S\t{scan_id:06d}\t{scan_id:06d}\t{prc_mass_mz:.4f}\n" \
                "I\tTIMSTOF_Frame_ID\t{parent_index}\n" \
                "I\tTIMSTOF_ParentTable_ID\t{prc_id:d}\n" \
                "I\tIon Mobility\t{k0:.4f}\n" \
                "I\tRetTime\t{ret_time:.4f}\n" \
                "Z\t{cs:d}\t{prc_mass:.4f}\n"


