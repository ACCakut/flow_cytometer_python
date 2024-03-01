## This module contains a selection of classes, functions to import and prepare data from BD FACS saved in csv files.

## Info
if __name__ == "__main__":
    print(
        "This python file is meant to be included as module to other code, not to be run solely."
    )


import numpy as np
import pandas as pd
import datetime
from dateutil.parser import parse


### Definition of functions and classes


def add_sample_info(df, plate):
    # Helper function to get the sample type, index, and measurement for a given well.
    def get_sample_info(well):
        for sample_type, well_list in plate.wells.items():
            if well in well_list:
                initial_measurement = True if "_second" not in sample_type else False
                sample_type = sample_type.replace("_second", "")
                index = well_list.index(well) + 1
                return sample_type, int(index), initial_measurement
        return "", np.nan, None

    # Apply the helper function to the "well" column of the DataFrame
    # and add the resulting sample type, index, and measurement as new columns.
    # Only apply to rows with the correct date.
    if hasattr(plate, "date"):
        condition = df["Record Date"].dt.date.isin(plate.date)
    else:
        raise ValueError("Please give your plates a date.")
        # condition = df["Well Name"] == None
    for temp_columnname in ["sample_type", "sample_index", "initial_measurement"]:
        if temp_columnname not in df:
            df[temp_columnname] = None

    df.loc[condition, ["sample_type", "sample_index", "initial_measurement"]] = list(
        (df.loc[condition, "Well Name"].astype(str).apply(get_sample_info))
    )

    # Change the data types of the new columns
    df = df.astype(
        {
            "sample_type": str,
            "sample_index": pd.Int64Dtype(),
            "initial_measurement": bool,
        }
    )

    # Go through dataframe for all given dates and correlate first and second measurements

    def pair_wells(row, plate_date, plate_well_pairings):
        ## skip if already paired and just return the already existing values
        ## important, since otherwise, they got overwritten with 'None' by last run
        if "paired_well" in row and not pd.isnull(row["paired_well"]):
            return pd.Series(
                [
                    row["paired_well"],
                    row["paired_GUID"],
                    row["paired_GFP_positive_events"],
                ]
            )
        else:
            # check date, set temporary boolean
            is_date_correct = False
            # go through all dates of the plate and check if this row is taken on right date
            for date in plate_date:
                if date == row["Record Date"].to_pydatetime().date():
                    # if date matches, set True
                    is_date_correct = True

            # get name of corresponding well as given in plate
            paired_well = plate_well_pairings.get(row["Well Name"], None)
            # if paired well is found and dates match
            if paired_well is not None and is_date_correct:
                # find wells named == paired_well and in according time interval 3-6 hours
                paired_rows = df[
                    (df["Well Name"] == paired_well)
                    & (
                        df["Record Date"]
                        <= row["Record Date"] + datetime.timedelta(hours=8)
                    )
                    & (
                        df["Record Date"]
                        >= row["Record Date"] + datetime.timedelta(hours=1)
                    )
                ]
                if not paired_rows.empty:  # if matches exists (doubles with next line)
                    if len(paired_rows) == 1:  # and there is exactly one match
                        paired_row = paired_rows.iloc[0]  # get this one (first) match
                        # check if match also has the same date (doubles somehow with time interval check, but two is better than one)
                        is_paired_date_correct = False
                        for date in plate_date:
                            if (
                                date == paired_row["Record Date"].to_pydatetime().date()
                            ):  ## should be ensured by time difference also
                                is_paired_date_correct = True
                        if is_paired_date_correct:
                            return pd.Series(
                                [
                                    paired_well,
                                    paired_row["GUID"],
                                    paired_row["GFP positiv #Events"],
                                ]
                            )
                        else:
                            return pd.Series([None, None, None])
                    else:
                        print("Cannot pair wells for row ", row, "unambigously.")
                        raise ValueError("Cannot pair wells unambigously.")
                        return pd.Series([None, None, None]) # should be unneccessary due to raise
                else:
                    return pd.Series([None, None, None])

            else:
                return pd.Series([None, None, None])

    df[["paired_well", "paired_GUID", "paired_GFP_positive_events"]] = df.apply(
        pair_wells,
        axis=1,
        plate_date=plate.date,
        plate_well_pairings=plate.well_pairings,
    )

    return df


# list of experiments with time and sample <-> well definitions
# experiments = [
#        [datetime.date(2023,12,1), ]
# ]


class Experiment:
    def __init__(
        self,
        dates,
        number_of_hybrids,
        number_of_controls,
        number_of_ancestors,
        number_of_reference,
        number_of_GFP,
        min_GFP_threshold_before,
        min_GFP_threshold_after,
        max_GFP_threshold_before,
        max_GFP_threshold_after,
    ):
        self.dates = dates  # dates of successful experiments
        self.number_of_hybrids = (
            number_of_hybrids  # hybrids = evolved strains with DNA added
        )
        self.number_of_controls = number_of_controls  # controls = (presumably not) evolved strains with no DNA added
        self.number_of_ancestors = number_of_ancestors  # ancestor strains
        self.number_of_reference = number_of_reference  # recipient strains
        self.number_of_GFP = number_of_GFP  # just GFP strains in well
        self.min_GFP_threshold_before = min_GFP_threshold_before  # lower fractions of GFP in the first measurement are ommited, e.g. 0.35 (35%)
        self.min_GFP_threshold_after = min_GFP_threshold_after  # lower fractions of GFP in the second measurement are ommited, e.g. 0.25 (25%)
        self.max_GFP_threshold_before = max_GFP_threshold_before  # higher fractions of GFP in the first measurement are ommited, e.g. 0.65 (65%)
        self.max_GFP_threshold_after = max_GFP_threshold_after  # higher fractions of GFP in the second measurement are ommited, e.g. 0.75 (75%)


class Plate:
    def __init__(self, well_ranges, after_measurements_start, date=None):
        # well_ranges is a dictionary where each key is a sample type and the value is a tuple.
        # The tuple can either be (start_well, end_well) or (start_well, count).
        self.well_ranges = well_ranges

        # Can be either a well name like D1 or an integer offset regarding the first well from well_ranges
        self.after_measurements_start = after_measurements_start

        # Define the rows and columns of the plate.
        self.plate_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
        self.plate_columns = list(range(1, 13))

        #
        if date is not None:
            if isinstance(date, str):
                # fine
                self.date = list(parse(date).date)
            elif isinstance(date, list) or isinstance(date, tuple):
                # fine, but check type of items
                if all(
                    (isinstance(item, str) or isinstance(item, datetime))
                    for item in date
                ):
                    self.date = [parse(item).date() for item in date]
                else:
                    raise TypeError(
                        "The data type of the elements in the date list/tuple must be datetime or strings."
                    )
            elif isinstance(date, datetime):
                # fine
                self.date = date.date()
            else:
                raise TypeError(
                    "The data type of parameter date must be datetime.date, string (containing date) or list/tuple (of dates/strings)."
                )

        # Generate the wells during initialization.
        self.generate_wells()

    def generate_wells(self):
        # Create empty dictionary to store well definitions.
        self.wells = {}
        self.well_pairings = {}
        # Iterate over each sample type and its well range.
        for sample_type, well_range in self.well_ranges.items():
            # Calculate the wells for the first compartment and store in dictionary.
            self.wells[sample_type] = self.calculate_wells(well_range)
            # setattr(self, sample_type, wells)

            # Generate the wells for the second compartment.
            if isinstance(self.after_measurements_start, int):
                offset = self.after_measurements_start
            else:  # If it's a starting well
                # Calculate the offset based on the first well of the first compartment.
                first_well = min(
                    well
                    for well_list in self.well_ranges.values()
                    for well in self.calculate_wells(well_list)
                )
                offset = self.plate_rows.index(
                    self.after_measurements_start[0]
                ) - self.plate_rows.index(first_well[0])

            # Calculate the wells for the second compartment based on the offset and store in dictionary.
            self.wells[sample_type + "_second"] = [
                self.plate_rows[self.plate_rows.index(well[0]) + offset] + well[1:]
                for well in self.wells[sample_type]
            ]

            # Add the first measurement cells as keys and second measurement wells as values to the dictionary.
            # my_dict = dict(zip(keys, values))
            self.well_pairings.update(
                dict(zip(self.wells[sample_type], self.wells[sample_type + "_second"]))
            )

    def calculate_wells(self, well_range):
        wells = []
        start_well = well_range[0]
        start_row, start_col = start_well[0], int(start_well[1:])

        if isinstance(well_range[1], int):  # If the second element is a count
            count = well_range[1]
            end_row_index = (start_col + count - 1) // len(
                self.plate_columns
            ) + self.plate_rows.index(start_row)
            end_col = (start_col + count - 1) % len(self.plate_columns)
        else:  # If the second element is an end well
            end_well = well_range[1]
            end_row, end_col = end_well[0], int(end_well[1:])
            end_row_index = self.plate_rows.index(end_row)

        for row in self.plate_rows[
            self.plate_rows.index(start_row) : end_row_index + 1
        ]:
            for col in self.plate_columns[
                start_col - 1
                if row == start_row
                else 0 : end_col
                if row == self.plate_rows[end_row_index]
                else len(self.plate_columns)
            ]:
                wells.append(f"{row}{col}")

        return wells
