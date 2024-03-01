# flow_cytometer_python
Some Python scripts to analyse flow cytometer measurements as those from BD.

## facs_csv_import.py
Contains a selection of classes, functions to import and prepare data from BD FACS with HTS module saved in csv files. The software exports csv file with all measurements, but the formatting is poor. This module is intended to help to analyse experiments with the following procedure:
- cells are mixed 50:50 (GFP:non-GFP) in well plate in a certain number of wells starting at well A1
- after a specific time of head-to-head-growth, the cells are transferred to the same number of wells starting at a given position (usually to remaining wells on the same plate as before)
- selection coefficient is calculated by the fraction of GFP/non-GFP cells before and after head-to-head growth

Features:
- Provides class Plate to save plate layouts, sets date, calculates which wells have which sample from straightforward definition
- Automatically pairs measurements before and after as defined by plate layout and time interval between measurements
- Stores data into a nice pandas dataframe with sample_type and paired measurement

### Basic usage:
```
from facs_csv_import import *
facs_measurements = pd.read_csv(your-file.csv, sep=",", parse_dates=[3], date_format="%b %d, %Y %I:%M:%S %p")
# Add required columns
facs_measurements[["paired_well", "paired_GUID"]] = [None, None]

# Define plate layout
well_ranges = {  # plate1
    "hybrids": ("A1", 20),  # Specifies the start well and count
    "controls": ("B9", "B12"),  # Specifies the start well and end well
    "ancestors": ("C1", "C3"),  # Specifies the start well and end well
}
plate1 = Plate(well_ranges, "D1", ["2023-12-31"]) # class Plate from facs_csv_import
# second argument "D1" states, where the second measurements well begin
# third argument is a list containing at least one date where this plate layout was used

well_ranges = {  # plate2
    "hybrids": ("A1", 20),  # Specifies the start well and count
    "controls": ("B9", "B12"),  # Specifies the start well and end well
    "GFPs": ("C1", "C3"),  # Specifies the start well and end well
}
plate2 = Plate(well_ranges, "D1", ["2024-01-01"])

for i in [plate1, plate2]:
    facs_measurements = add_sample_info(facs_measurements, i) # Here the magic of facs_csv_import.py takes place

facs_measurements.head() # View result



def s(fractions_before, fractions_after, generation_time=25*60, time_to_grow=4*3600): # selection coefficient s
    ## fractions regarding your reporter strain, e.g. 4000 of 10000 are GFP -> 0.4
    return (generation_time / time_to_grow) * np.log(((1 - fractions_after) / fractions_after) / ((1 - fractions_before) / fractions_before) )

# Add selection coefficient s to dataframe
facs_measurements["s"] = list(map(s, facs_measurements["GFP positiv #Events"]/10000, facs_measurements["paired_GFP_positive_events"]/10000))
```
