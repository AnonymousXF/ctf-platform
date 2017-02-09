# -*- coding: utf-8 -*-
import operator

def sort(chal_failed, chal_solved):
    submits = []
    for chal in chal_failed:
        submits.append(chal)
    for chal in chal_solved:
        submits.append(chal)
    cmpfuc = operator.attrgetter("time")
    submits.sort(key = cmpfuc, reverse = True)
    return submits

def handle_solving(obj_list):
    results = []
    for i in range(len(obj_list)):
        try:
            if obj_list[i].attempt is not None:
                results.append({"teamname":obj_list[i].team.name, "chal_name":obj_list[i].challenge.name, "submit_time":obj_list[i].time, "status":"Failed"})
        except AttributeError:
            results.append({"teamname": obj_list[i].team.name, "chal_name": obj_list[i].challenge.name, "submit_time": obj_list[i].time, "status": "Success"})
    return results