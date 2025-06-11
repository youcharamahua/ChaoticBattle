import random

#归一化随机选择器
def Probabilistic_classifier(weights=[1,1,1,1,1,1]):
    action_dict = {
        'normal_attack':300+weights[0],
        'attribute_promotion': 140+weights[1],
        'resistance_enhancement':50+weights[2],
        'effect_application':45+weights[3],
        'morphology_skill':20+weights[4],
        'field':20+weights[5]
    }
    total = sum(action_dict.values())
    choices = list(action_dict.keys())
    weights = [value / total for value in action_dict.values()]
    selected_action = str(random.choices(choices, weights=weights, k=1)[0])
    
    return selected_action

def dodge_decision(att_type,field,randomCamp,random_charA,random_charB):
    
    #检测是否触发领域能力
    if field["owner_camp"] == randomCamp[0]:
        #如果为攻击则触发
        if att_type == 'normal_attack':
            if field["owner"] == random_charA["name"]:
                log = "%s 试图躲避来自 %s 的进攻,但是在 %s 的领域【%s】下， %s无法躲避！\n" %(random_charB["name"], random_charA["name"],random_charA["name"],field["identify"],random_charB["name"])
                att_type = 'normal_attack'
                if random.randint(1,10) == 10 and field["unique_skill"]:
                    att_type = 'unique_skill'
                return [log,1]
            else:
                log = "%s 试图躲避来自 %s 的进攻,但是 %s 处在 %s 队友 %s 的领域【%s】内， %s无法躲避！\n" %(random_charB["name"], random_charA["name"],random_charB["name"],random_charA["name"],field["owner"],field["identify"],random_charB["name"])
                att_type = 'normal_attack'
                return [log,1]
        else:
            return [0,1]
    else:
        avoid = random.randint(1, 150+random_charB["speed"])
        if random_charB["speed"] > avoid:
            log = "%s 试图攻击 %s ,但是被躲开了\n" %(random_charA["name"], random_charB["name"])
            return [log,0]
        return [0,1]

def NCrandom(a, b, c):
    while True:
        random_number = random.randint(a, b)
        if random_number != c:
            return random_number