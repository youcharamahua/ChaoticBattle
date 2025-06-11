import random


occasion_list = ['outputing','pre-attack','post-attack','pre-die']
type_list = ['instant_health','attribute_change','resistance_change']
#_cache = [0,0,0,0,0,0,0,0,0]

def infliction_effect(series_number, effect, target, duration, level, normal, special, cache, VFX_log, die_log):
    StatusEffect = {
        'series_number' : series_number,
        'effectName':effect,
        'affected_target':{"camp":target[0],"character_index":target[1],"name":target[2]},
        'duration':[duration[0],duration[1]],
        'level':level,
        'normal':normal,
        'special': special,
        'cache':cache,
        'VFX_log':VFX_log,
        'die_log':die_log
    }
    return StatusEffect

def detector_outputing_effect(CampDictionary):
    pass

def effect_expire(effect,counter):
    if effect["duration"][0]+effect["duration"][1] <= counter:
        return [True, effect["die_log"]]
    else:
        _log = random.choice(effect["VFX_log"])
        if random.randint(1,100) <= _log[1]:
            return [False, _log[0]]
        else:
            return [False, False]
    
def instant_health(CampDictionary,probability,target,action,calculate_function,VFX,attributes):
    #const/percentage
    if random.randint(1,1000) >= probability:
        return False
    if action == "heal":
        if calculate_function[0] == "const":
            num = calculate_function[1]
            CampDictionary[target["camp"]][target["character_index"]]["health"] += num
        elif calculate_function[0] == "percentage":
            num = calculate_function[1]*CampDictionary[target["camp"]][target["character_index"]]["original_health"]
            num = random.randint(int(num*0.8),int(num*1.2))
            CampDictionary[target["camp"]][target["character_index"]]["health"] += num
        if CampDictionary[target["camp"]][target["character_index"]]["health"]>= CampDictionary[target["camp"]][target["character_index"]]["original_health"]:
            CampDictionary[target["camp"]][target["character_index"]]["health"] = CampDictionary[target["camp"]][target["character_index"]]["original_health"]
            return [action,VFX.replace("***",target["name"])+",使其恢复到了完全健康！",CampDictionary]
        return [action,VFX.replace("***",target["name"]+",为其恢复了%d点生命值"%(num)),CampDictionary]
    if action == "damage":
        attributes = attributes.split("||")
        if calculate_function[0] == "const":
            num = calculate_function[1]
        elif calculate_function[0] == "percentage":
            num = calculate_function[1]*CampDictionary[target["camp"]][target["character_index"]]["original_health"]
            num = random.randint(int(num*0.8),int(num*1.2))
        skill = "%s||%s||%d*%d||%s||%s"%(attributes[0],VFX[0],num,calculate_function[2],VFX[1],attributes[1])
        if len(attributes) >= 3:
            skill = "%s||%s||%d*%d||%s||%s||%s"%(attributes[0],VFX[0],num,calculate_function[2],VFX[1],attributes[1],attributes[2])
        return [action,skill,target]
    
def resistance_change():
    pass