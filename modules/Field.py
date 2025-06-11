
def field_decision():
    pass


def field_break(field, owner,type,new_owner):
    if type == 0:
        log = "%s\n" %(field["die_log"].replace('***', owner))
        field = {"identify":"init","owner": "none", "owner_camp": "init", "Absolute_Weight":0 ,"init_value":0,
                "value": 0,"maintain_log":[],"break_log":"","die_log":"","unique_skill":[]}
        return [log,field]
    elif type == 1:
        log = "%s\n" %(field["break_log"].replace('***', owner))
        field = {"identify":"init","owner": "none", "owner_camp": "init", "Absolute_Weight":0 ,"init_value":0,
                "value": 0,"maintain_log":[],"break_log":"","die_log":"","unique_skill":[]}
        return [log,field]
    elif type == 2:
        log = "在 %s 爆发出的强势能量的肆虐下，%s\n" %(new_owner,field["break_log"].replace('***', owner))
        return [log,0]