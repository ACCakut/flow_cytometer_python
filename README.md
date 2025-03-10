# flow_cytometer_python
Some Python scripts to analyse flow cytometer measurements as those from BD.

This is a poorly maintained and updated repository of scripts I created that could also be useful for others. These scripts are neither well tested nor sophisticated nor documented properly. **Absolutely no warranty, that they function as intended.**

Feel free to use and adapt the code as you like. Pull requests and issues are welcome but I cannot give time-consuming support.

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



## Legacy code metrics (How reliable this code is)

O++ S++ I C-- E- M- V- !PS D-

Inspired by fefe.

### Legacy Code: Ownership, Contingency

**O++ Public domain / MIT / Apache**

O+  Copyleft

O   We own it. But if we go under, you get the source code.

O-  We own it. You get a license we can revoke at any time.

O-- We own it. We don't sell it. You can only rent it.

!O  You use our appliance / cloud service.

### Legacy Code: Source Code

**S++ The source code is public and you can change it**

S+  The source code is public

S   The source code leaked a while ago

S-  We let the government view the source code

S-- The source code is secret

!S  We lost the source code

### Legacy Code: Intent, Confidence

I+++ I make actual guarantees

I++  I have done this multiple times before. I know what I'm doing.

I+   I had to adapt the design a bit over time

**I    I tried to avoid security bugs while writing this**

I-   Look, they paid me to do this

I--  The guy left. Code now maintained by team in India

!I   I have no idea what I'm doing

### Legacy Code: Correctness

C+++ We have a correctness proof and you can understand/verify it

C++  We have a correctness proof

C+   No open bugs, 100% test coverage and we do regular code audits

C    We try to fix bugs that our users tell us about

C-   We have a bug backlog

**C--  At some point we are planning to gave a bug tracking system**

!C   That's not really a bug, that's just a crash!

### Legacy Code: Engineering, Design

E+++  Least Privilege, Privilege Separation, TCB minimized

E++   We sandbox ourselves away so nothing bad can happen

E     We try to detect bad arguments

**E-    Well... we fix bugs. That's good, right?**

E--   We just do what we are told. You call us wrong, that's on you!

E---  We run as root / in the kernel

E---- We sell it as an appliance so you don't see how bad it is

!E    We do a daily AI malware scan of our blockchain


### Legacy Code: Maintenance

M!   Author is Don Knuth / Dan Bernstein, makes no mistakes.

M+   Project is feature/complete, get occasional security updates

M    Project gets updated regularly

**M-   People send pull requests / patches to mailing list**

M--  Vendor publishes quarterly patch roundup with 512 fixes each

M--- Author killed project. Unoficial forks / backups still around.

!M   Author left / dead, project abandoned

### Legacy Code: Volatility

V!   Software is perfect, needed no updates since 1993

V++  Like V+ but has a way to notify you of new versions

V+   Regular patches and updates but you can't tell the difference 

**V-   Updating is such a hassle that backporting patches is a thing**

V--  The new version broke so much, most people use the old one 

V--- Agile. 5 updates/day, half of them break production

!V   Support ended

### Legacy Code: Protocol / Spec

PS++  The spec is public, short and precise

PS    The spec is OK but interoperability is a bitch

PS-   The spec is so large, nobody implements all of it

PS--  The spec cannot be implemented securely

PS--- There is a spec but it's paywalled

**!PS   The author made it up as he went**

### Legacy Code: Dependencies

!D   No dependencies. You boot our image directly.

D++  We depend only on things that come with the system

D+   We depend on sqlite and libz

D    We use somebody's Docker image from the Internet

**D-   We don't even have a list of the dependencies**

D--  We load extensions dynamically from the Internet

D--- Uses vendor specific lock-in APIs/features
