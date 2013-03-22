#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re, sys, json

def tag2msi(tag):
    return ""


if __name__ == '__main__':
    if sys.argv > 1:
        print(tag2msi(sys.argv[0]))

    else:
        expected = {"category": "adjetivo","type": "calificativo","grade": None,"gender": "masculino","number": "singular","function": None,"person": 3}
        expected_json = '{"category": "adjetivo", "function": "null", "grade": null, "gender": "masculino", "number": "singular", "person": 3, "type": "calificativo"}'

        result = tag2msi("AQ0MS0")
        result_json = json.dumps(result)
        
        assert result == expected
        assert result_json == expected_json
