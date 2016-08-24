# -*- coding: utf-8 -*-
import re
import datetime

class FactTimeUtils(object):

    def __init__(self):
        self.time_labels = ["day_of_week", "day", "month", "year", "hours", "minutes", "period"]

    def normalize_datainfo(self, datainfo, normalized_token = None):
        new_info = {}
        for a_label in self.time_labels:
            if a_label not in datainfo or datainfo[a_label] is None:
                new_info[a_label] = normalized_token
            else:
                new_info[a_label] = datainfo[a_label]

        return new_info

    def datainfo_to_timestamp(self, datainfo, with_time=False):
        normalized_info = self.normalize_datainfo(datainfo, "??")

        timestamp = "("
        if normalized_info["day_of_week"] != "??":
            timestamp += normalized_info["day_of_week"].title() + " "
        timestamp += str(normalized_info["year"]) + "/" + str(normalized_info["month"]) + "/" + str(normalized_info["day"])

        if with_time:
            timestamp += " " + str(normalized_info["hours"]) + ":" + str(normalized_info["minutes"])
            if normalized_info["period"] != "??":
                timestamp += " " + normalized_info["period"].upper()

        timestamp += ")"

        return timestamp


    def get_timebox(self, clause):
        time_lexical_forms = [" ".join([repr(l) for l in reference.leaves()]) for reference in clause.time_references]
        timebox = ", ".join(time_lexical_forms).lower()
        return timebox

    def extract_data_info(self, clause, timebox=None):
        if timebox is None:
            timebox = self.get_timebox(clause)

        data_info = {}
        time_regex = re.compile(ur"^\[[0-9A-Z:?/.]+\]$", re.U | re.I)
        day_of_week_labels = {"L": "lunes", "M": "martes", "X": "miércoles", "J": "jueves", "V": "viernes", "S": "sábado", "G": "domingo"}

        for a_data in clause.proper_tree().nodes_with_labels("data"):
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


        #NO DATA LABEL, EXTRACT FROM TIME BOX:
        now = datetime.datetime.now()
        today = {"year": now.year, "month": now.month, "day": now.day}

        year_regexp = re.compile(ur"(1\d{3}$|2[012]\d{2})", re.U | re.I)

        if len(data_info) == 0 and timebox is not None:
            if year_regexp.search(timebox):
                data_info = {"year": int(year_regexp.search(timebox).group(0))}
            elif "hoy" in timebox:
                data_info = today
            elif any(a_day_before_yesterday in timebox for a_day_before_yesterday in ["anteayer", "anteanoche"]):
                timeframe = now - datetime.timedelta(2)
                data_info = {"year": timeframe.year, "month": timeframe.month, "day": timeframe.day}
            elif any(a_yesterday in timebox for a_yesterday in ["ayer", "anoche"]):
                timeframe = now - datetime.timedelta(1)
                data_info = {"year": timeframe.year, "month": timeframe.month, "day": timeframe.day}

        if len(data_info) > 0 and ("year" not in data_info or data_info["year"] is None):
            data_info["year"] = 2016

        return data_info


    def parse_relative_time_info(self, timebox, input_reference_time=None):

        reference_time = {}

        if input_reference_time is not None:
            for a_label in input_reference_time:
                if input_reference_time[a_label] is not None:
                    reference_time[a_label] = input_reference_time[a_label]
        else:
            reference_time = None
        changed = False

        #DEFAULT VALUES:
        now = datetime.datetime.now()
        if not reference_time:
            today = {"year": now.year, "month": now.month, "day": now.day}
            reference_time = today
        if "month" not in reference_time or reference_time["month"] is None:
            reference_time["month"] = 1
        if "day" not in reference_time or reference_time["day"] is None:
            reference_time["day"] = 1
        if "year" not in reference_time or reference_time["year"] is None:
            reference_time["year"] = now.year

        #SANITIZE
        if not isinstance(timebox, unicode):
            timebox = timebox.decode("utf-8")
        timebox = timebox.lower()

        number_words = [ur"un(o|a)?", ur"dos", ur"tres", ur"cuatro", ur"cinco", ur"seis", ur"siete", ur"ocho", ur"nueve", ur"diez",
                        ur"once", ur"doce", ur"trece", ur"catorce", ur"quince", ur"dieciseis", ur"diecisiete", ur"dieciocho", ur"diecinueve", ur"veinte",
                        ur"(veintiun(o|a))|(veintiún)", ur"veintidos", ur"veintitrés", ur"veinticuatro", ur"veinticinco", ur"veintiseis", ur"veintisiete", ur"veintiocho", ur"veintinueve", ur"treinta"]

        date_magnitudes = {
                            ur"\bdías?\b"          : {"weigth": 1,     "overrides": []},
                            ur"\bsemanas?\b"       : {"weigth": 7,     "overrides": []},
                            ur"\bquincenas?\b"     : {"weigth": 15,    "overrides": []},
                            ur"\bmes(es)?\b"       : {"weigth": 31,    "overrides": ["day"]},
                            ur"\bbimestres?\b"     : {"weigth": 62,    "overrides": ["day"]},
                            ur"\btrimestres?\b"    : {"weigth": 93,    "overrides": ["day"]},
                            ur"\bcuatrimestres?\b" : {"weigth": 124,   "overrides": ["day"]},
                            ur"\bsemestres?\b"     : {"weigth": 186,   "overrides": ["day"]},
                            ur"\baños?\b"          : {"weigth": 366,   "overrides": ["day", "month"]},
                            ur"\bdécadas?\b"       : {"weigth": 3650,  "overrides": ["day", "month"]},
                            ur"\bsiglos?\b"        : {"weigth": 36500, "overrides": ["day", "month"]},
                        }

        #TYPES OF OPERATIONS: 0 => USE MAGNITUDE, +x => ADD WEIGTH, -x => SUBTRACT WEIGTH
        date_operations = {
                            ur"\bhace\b"           : {"use_number": True, "sign": -1},
                            ur"\bantes\b"          : {"use_number": True, "sign": -1},
                            ur"\batrás\b"          : {"use_number": True, "sign": -1},
                            ur"\bdespués\b"        : {"use_number": True, "sign": +1},
                            ur"\bpróxim(o|a)s\b"   : {"use_number": True, "sign": +1},
                            ur"\bvenider(o|a)s\b"  : {"use_number": True, "sign": +1},
                            ur"\banteriores\b"     : {"use_number": True, "sign": -1},
                            ur"\bpasad(o|a)s\b"    : {"use_number": True, "sign": -1},

                            ur"\bviene\b"          : {"use_number": False, "value": +1},
                            ur"\bpasad(o|a)\b"     : {"use_number": False, "value": -1},
                            ur"\banterior\b"       : {"use_number": False, "value": -1},
                            ur"\bsiguiente\b"      : {"use_number": False, "value": -1},
                            ur"\bpróxim(o|a)\b"    : {"use_number": False, "value": +1},
                            ur"\bvenider(o|a)\b"   : {"use_number": False, "value": +1},
                        }

        #NUMBER:
        number_regex = ur"\b[0-9]{1,3}\b"
        a_number = re.search(number_regex, timebox)
        if a_number:
            a_number = int(a_number.group(0))
        else:
            for idx, a_word in enumerate(number_words):
                if re.search(ur"\b"+a_word+ur"\b", timebox):
                    a_number = idx + 1

        #MODIFIER:
        selected_operation = None
        for an_operation_regex, an_operation in date_operations.iteritems():
            if re.search(an_operation_regex, timebox):
                selected_operation = an_operation
                if an_operation["use_number"]:
                    if a_number:
                        a_number = an_operation["sign"] * a_number
                else:
                    a_number = an_operation["value"]
                break
        print selected_operation
        #MAGNITUDE:
        if a_number:
            for a_regex, a_value in date_magnitudes.iteritems():
                if re.search(a_regex, timebox):
                    a_number = a_number * a_value["weigth"]

                    previous_time = datetime.date(reference_time["year"], reference_time["month"], reference_time["day"])
                    timeframe = previous_time + datetime.timedelta(a_number)
                    reference_time = {"year": timeframe.year, "month": timeframe.month, "day": timeframe.day}
                    changed = True
                    #Vague reference => blur calculated time!
                    if selected_operation["use_number"] == False:
                        for an_overriden_time in a_value["overrides"]:
                            reference_time.pop(an_overriden_time, None)

                    #Remove tags that were not present in the original date:
                    #THE PROCESSED DATE CANNOT BE MORE ACCURATE THAN THE INPUT DATE!
                    if input_reference_time is not None:
                        labels = []
                        for a_label in reference_time:
                            if a_label not in input_reference_time or input_reference_time[a_label] is None:
                                labels.append(a_label)

                        for a_label in labels:
                            reference_time.pop(a_label, None)
        if changed:
            return reference_time
        else:
            return input_reference_time




    def compare_dates(self, date1, date2):
        """Compare two dates (year defaults to 2016 if any other data is present).

        Keyword arguments:
        :param date1: Formated date1 [year: month: day: day_of_week:].
        :param date2: Formated date2 [year: month: day: day_of_week:].
        """

        labels = ["year", "month", "day", "day_of_week"]
        comparison_result = {"full_labels": 0, "coincidence_labels": 0}

        for a_label in labels:
            if a_label not in date1:
                date1[a_label] = None
            if a_label not in date2:
                date2[a_label] = None

            if date1[a_label] == None or date2[a_label] == None:
                comparison_result[a_label] = -1
            elif date1[a_label] == date2[a_label]:
                comparison_result[a_label] = 1
                comparison_result["full_labels"] += 1
                comparison_result["coincidence_labels"] += 1
            else:
                comparison_result[a_label] = 0
                comparison_result["full_labels"] += 1

        full_labels = comparison_result["full_labels"]
        coincidence_labels = comparison_result["coincidence_labels"]

        score = 0
        if full_labels == len(labels):
            if comparison_result["year"] == 1:
                if comparison_result["month"] == 1:
                    if comparison_result["day"] == 1:
                        score = 1
                    else:
                        score = 0.75
                else:
                    score = 0.0
            else:
                score = 0.0

        #DISPONIBLES 3
        if full_labels == len(labels) -1:

            #COINCIDEN 1
            if coincidence_labels == 1:
                score = 1
            else:
                score = 0

            #COINCIDEN 2
            if coincidence_labels == 2:
                if comparison_result["month"] == 1 and comparison_result["day"] == 1:
                    score = 0.25
                elif comparison_result["month"] == 1 and comparison_result["year"] == 1:
                    score = 0.25
                elif comparison_result["month"] == 1 and comparison_result["day_of_week"] == 1:
                    score = 0.5
                elif comparison_result["day"] == 1 and comparison_result["day_of_week"] == 1:
                    score = 0.25
                else:
                    score = 0

            #COINCIDEN 3
            if coincidence_labels == 3:
                if comparison_result["day"] == 1:
                    score = 1.0
                elif comparison_result["day"] == -1:
                    score = 0.75

        #DISPONIBLES 2
        elif full_labels == len(labels) -2:
            #COINCIDEN 1
            if coincidence_labels == 1:
                if comparison_result["month"] == 1 and comparison_result["year"] == 1:
                    score = 0.0
                elif comparison_result["month"] == 1 and comparison_result["day"] == 1:
                    score = 0.5
                else:
                    score = 0.0

            #COINCIDEN 2
            if coincidence_labels == 2:
                if comparison_result["month"] == 1 and comparison_result["year"] == 1:
                    score = 1.0
                elif comparison_result["month"] == 1 and comparison_result["day"] == 1:
                    score = 1.0
                elif comparison_result["day_of_week"] == 1 and comparison_result["day"] == 1:
                    score = 0.5

        #DISPONIBLES 1
        elif full_labels == len(labels) -3:
            if coincidence_labels == 1:
                score = 1.0
            else:
                score = 0.0

        if full_labels == 0:
            score = -1.0

        #print comparison_result
        #print score
        return float(score)
