import csv


def parse(file: str) -> tuple[float, float, float]:
    """
    Parses codecarbon csv file and returns results as a tuple.
    :param file: Path to file
    :return: Tuple of duration time in seconds (float), total kwh used (float)
             and total kg of co2 emitted (float)
    """
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        header = next(csv_reader)
        duration = header.index("duration")
        emissions = header.index("emissions")
        energy_consumed = header.index("energy_consumed")

        row = next(csv_reader)
        return float(row[duration]), float(row[emissions]), float(row[energy_consumed])
