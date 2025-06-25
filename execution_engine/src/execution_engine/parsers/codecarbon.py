import csv


def parse(file: str) -> list[tuple[float, float, float]]:
    """
    Parses codecarbon csv file and returns results as a list of tuples.
    :param file: Path to file
    :return: List of tuples of duration time in seconds (float), total kwh used (float)
             and total kg of co2 emitted (float)
    """
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        header = next(csv_reader)
        duration = header.index("duration")
        emissions = header.index("emissions")
        energy_consumed = header.index("energy_consumed")

        results = []
        for row in csv_reader:
            results.append(
                (float(row[duration]), float(row[emissions]), float(row[energy_consumed]))
            )

    return results
