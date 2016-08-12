# -*- coding: utf-8 -*-
import re
import datetime

class FactTimeUtils(object):

    def __init__(self):
        self.time_labels = ["day_of_week", "day", "month", "year", "hours", "minutes", "period"]

    def normalize_datainfo(self, datainfo, normalized_token = None):
        new_info = {}
        for a_label in self.time_labels:
            if a_label not in datainfo:
                new_info[a_label] = normalized_token
            else:
                new_info[a_label] = datainfo[a_label]

        return new_info

    def datainfo_to_timestamp(self, datainfo):
        normalized_info = self.normalize_datainfo(datainfo, "??")

        timestamp = ""
        if normalized_info["day_of_week"] != "??":
            timestamp += normalized_info["day_of_week"].title() + " "
        timestamp += str(normalized_info["day"]) + "/" + str(normalized_info["month"]) + "/" + str(normalized_info["year"]) + " "
        timestamp += str(normalized_info["hours"]) + ":" + str(normalized_info["minutes"])

        if normalized_info["period"] != "??":
            timestamp += " " + normalized_info["period"].upper()

        return timestamp


    def extract_data_info(self, clause, timebox=None):
        if timebox is None:
            time_lexical_forms = [" ".join([repr(l) for l in reference.leaves()]) for reference in clause.time_references]
            timebox = ", ".join(time_lexical_forms).lower()

        data_info = {}
        time_regex = re.compile(ur"^\[[0-9A-Z:?/.]+\]$", re.U | re.I)
        day_of_week_labels = {"L": "lunes", "M": "martes", "X": "miércoles", "J": "jueves", "V": "viernes", "S": "sábado", "G": "domingo"}

        for a_data in clause.node.nodes_with_labels("data"):
            for a_leaf in a_data.leaves():
                if time_regex.match(a_leaf.lemma):

                    standarized_time = a_leaf.lemma.replace("[", "").replace("]", "").replace("/", ":").replace(".", ":")
                    time_bits = standarized_time.split(":")

                    for idx, a_label in enumerate(self.time_labels):

                        if idx <= len(time_bits) and time_bits[idx] != "??":
                            if time_bits[idx].isdigit():
                                data_info[a_label] = int(time_bits[idx])
                            else:
                                data_info[a_label] = time_bits[idx]
                        else:
                            data_info[a_label] = None

                    if data_info["day_of_week"] in day_of_week_labels:
                        data_info["day_of_week"] = day_of_week_labels[data_info["day_of_week"]]

                    return data_info

        #NO DATA LABEL, EXTRACT FROM TIME BOX:
        now = datetime.datetime.now()
        today = {"year": now.year, "month": now.month, "day": now.day}

        year_regexp = re.compile(ur"(1\d{3}$|^2[012]\d{2})", re.U | re.I)

        if timebox is not None:
            if year_regexp.search(timebox):
                data_info = {"year": int(year_regexp.search(timebox).group(0))}
            elif "hoy" in timebox:
                data_info = today
            elif any(a_yesterday in timebox for a_yesterday in ["ayer", "anoche"]):
                timeframe = now - datetime.timedelta(1)
                data_info = {"year": timeframe.year, "month": timeframe.month, "day": timeframe.day}

        return data_info
