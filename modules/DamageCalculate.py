
def origin_damage_calculate(damage, skill ,defender):
    origin_damage = damage
    '''
    damage:伤害值
    绝对抗性为一定抵消的伤害，为负则额外受伤
    相对抗性大于0则具有抗性，小于0则会额外受到次属性的伤害
    '''

    type = skill[4].split('**')
    for i in range(len(type)):
        if type[i] == "element":
            ele_type = skill[5].split('**')
            for i in range(len(ele_type)):
                if ele_type[i] in defender["element_resistances"]:
                    damage = damage - (defender["element_resistances"][ele_type[i]][0] + defender["element_resistances"][ele_type[i]][1] * damage)
        else:
            if type[i] in defender["resistances"]:
                damage = damage - (defender["resistances"][type[i]][0] + defender["resistances"][type[i]][1] * damage)

    damage = int(damage)
    #结算后文字
    if damage < 0 or damage == 0:
        output_log_massage = "但是%s的强大的抗性免疫了这次攻击" %(defender["name"])
        damage = 0
        effect = 0
    elif damage == origin_damage:
        return [damage,-1,0]#没有抗性，原伤害
    elif damage >= origin_damage:
        if skill[3] != "NOD":
            damageD = skill[3].replace('***', defender["name"])
            output_log_massage = "效果极佳，%s,在%s身上造成了大量伤害" %(damageD,defender["name"])
        else:
            output_log_massage = "效果极佳，在%s身上造成了大量伤害" %(defender["name"])
        effect = 1
    else:
        res_damage = origin_damage-damage
        if res_damage >= origin_damage*0.6:
            output_log_massage = "%s凭借着自身强大的抗性，减少了%d点伤害" %(defender["name"],res_damage)
            effect = 0
        elif res_damage >= origin_damage*0.2:
            if skill[3] != "NOD":
                damageD = skill[3].replace('***', defender["name"])
                output_log_massage = "%s,%s的抗性抵御了%d点伤害" %(damageD,defender["name"],res_damage)
            else:
                output_log_massage = "%s的抗性抵御了%d点伤害" %(defender["name"],res_damage)
            effect = 1
        else:
            return [damage,-1,""]
        
    #output_log("原始伤害:%d，结算后伤害:%d"% (origin_damage,damage), file=Character_GameVar.game_log)

    return [damage,effect,output_log_massage]

def settlement_output(damage, skill ,defender,attacker):
    if attacker == "state_damage":
        damage_log = "[BUFF]：%s 在 %s 身上发动了,造成了%d点伤害,%s" %(skill[1],defender["name"], damage[0], damage[2])
        #输出日志模板化
        if damage[0] > 0 and skill[3] != "NOD" and (damage[1] == 1 or damage[1] == 0):
            damageD = skill[3].replace('***', defender["name"])
            return damage_log
        elif damage[0] > 0 and skill[3] == "NOD" and (damage[1] == 1 or damage[1] == 0):
            return damage_log

        elif damage[0] > 0 and damage[1] == -1:
            if skill[3] != "NOD":
                damageD = skill[3].replace('***', defender["name"])
                damage_log = "[BUFF]：%s 在 %s 身上发动了,造成了%d点伤害,%s" %(skill[1],defender["name"], damage[0], damageD)
                return damage_log
            else:
                damage_log = "[BUFF]：%s 在 %s 身上发动了,造成了%d点伤害" %(skill[1],defender["name"], damage[0])
                return damage_log
        else:
            damage_log = "[BUFF]：%s 在 %s 身上发动了, %s " %(skill[1],defender["name"], damage[2])
            return damage_log
        
    damage_log = "%s 对 %s 发动了%s,造成了%d点伤害,%s" %(attacker["name"], defender["name"], skill[1], damage[0], damage[2])
    #输出日志模板化
    if damage[0] > 0 and skill[3] != "NOD" and (damage[1] == 1 or damage[1] == 0):
        damageD = skill[3].replace('***', defender["name"])
        return damage_log
    elif damage[0] > 0 and skill[3] == "NOD" and (damage[1] == 1 or damage[1] == 0):
        return damage_log

    elif damage[0] > 0 and damage[1] == -1:
        if skill[3] != "NOD":
            damageD = skill[3].replace('***', defender["name"])
            damage_log = "%s 对 %s 发动了%s,造成了%d点伤害,%s" %(attacker["name"], defender["name"], skill[1], damage[0], damageD)
            return damage_log
        else:
            damage_log = "%s 对 %s 发动了%s,造成了%d点伤害" %(attacker["name"], defender["name"], skill[1], damage[0])
            return damage_log
    else:
        damage_log = "%s 对 %s 发动了%s, %s " %(attacker["name"], defender["name"], skill[1], damage[2])
        return damage_log