import random
import json
import time
import copy
from modules.ProbabilisticClassifier import *
from modules.StatusEffect import *
from modules.ArithmeticMachine import *
from modules.DamageCalculate import *
from modules.Field import *

#创建了Character_GameVar类
class Character_GameVar:
    #成员存储
    CampDictionary = {}
    #游戏预设存储
    DefaultDict = {}
    #战斗场地
    environment = {}
    #场地领域
    field = {"identify":"init",
             "owner": "none", 
             "owner_camp": "init", 
             "Absolute_Weight":0 ,
             "init_value":0,
             "value": 0,
             "maintain_log":[],
             "break_log":"",
             "die_log":"",
             "unique_skill":[]}
    #计数器
    counter = [0]
    #控制是否外部批量输入
    InPut = 1
    #日志构建
    START = False
    time = time.strftime('%Y-%m-%d_%H%M%S')
    game_log = open("log/"+time+"_FightLOG.txt", "w",encoding='utf-8')
    last_log = False

def pre_output():
    if Character_GameVar.START:
        trueBREAK = False
        for camp in Character_GameVar.CampDictionary:
            if trueBREAK:
                break
            for member_index in range(len(Character_GameVar.CampDictionary[camp])):
                if trueBREAK:
                    break
                delete_index = []
                if Character_GameVar.CampDictionary[camp][member_index]["status"]:
                    for status_index in range(len(Character_GameVar.CampDictionary[camp][member_index]["status"])):
                        if trueBREAK:
                            break
                        #侦测所有outputing类型的状态效果触发
                        _tempState = Character_GameVar.CampDictionary[camp][member_index]["status"][status_index]
                        for occasion, type_dict in _tempState["normal"].items():
                            if trueBREAK:
                                break
                            if occasion == "outputing":
                                for type , value in type_dict.items():
                                    if trueBREAK:
                                        break
                                    if type == "instant_health":
                                        _result = instant_health(Character_GameVar.CampDictionary,
                                                    value["probability"],_tempState["affected_target"],
                                                    value["action"],value["calculate_function"],value["VFX"],value["attributes"])
                                        if _result == False:
                                            continue
                                        elif _result[0] == "heal":
                                             output_log(_result[1])
                                             Character_GameVar.CampDictionary = _result[2]
                                        elif _result[0] == "damage":
                                            skill = _result[1].split("||")
                                            att_list = skill[2].split("*")
                                            att_list[0] = int(att_list[0])
                                            att_list[1] = int(att_list[1])
                                            addition = 0
                                            target = _result[2]
                                            for i in range(att_list[1]):
                                                returnS = inflict_damage(skill, "state_damage", 
                                                            Character_GameVar.CampDictionary[target["camp"]][target["character_index"]], 
                                                            att_list, target["character_index"], target["camp"],addition,unusual="state_damage")   
                                                if returnS == "DIE":
                                                    trueBREAK = True
                                                    break
        #侦测状态效果是否过时
        for camp in Character_GameVar.CampDictionary:
            for member_index in range(len(Character_GameVar.CampDictionary[camp])):
                delete_index = []
                if Character_GameVar.CampDictionary[camp][member_index]["status"]:
                    for status_index in range(len(Character_GameVar.CampDictionary[camp][member_index]["status"])):
                        _effect_expire = effect_expire(Character_GameVar.CampDictionary[camp][member_index]["status"][status_index],Character_GameVar.counter[0])
                        if _effect_expire[0]:
                            output_log(_effect_expire[1].replace("***",
                                Character_GameVar.CampDictionary[camp][member_index]["status"][status_index]["affected_target"]["name"]))
                            delete_index.append(status_index)
                        else:
                            if _effect_expire[1] != False:
                                output_log(_effect_expire[1].replace("***",
                                    Character_GameVar.CampDictionary[camp][member_index]["status"][status_index]["affected_target"]["name"]))
                    Character_GameVar.CampDictionary[camp][member_index]["status"] = [status for i, 
                        status in enumerate(Character_GameVar.CampDictionary[camp][member_index]["status"]) if i not in delete_index]

def output_log(log):
    try:
        if not isinstance(log, str):
            raise ValueError("Log must be a string")
        if not log and not Character_GameVar.last_log:
            return
        Character_GameVar.counter[0] += 1
        Character_GameVar.last_log = log
        if log.endswith('\n'):
            Character_GameVar.last_log = False
        print(log, file=Character_GameVar.game_log)
    except (AttributeError, TypeError) as e:
        print(f"Error in output_log: {e}")
    

#初始化方法
def G_init():
    #导入游戏预设
    with open("data/standard_data.json", 'rb') as data_1:
        Data_1 = data_1.read()
    Character_GameVar.DefaultDict = json.loads(Data_1)
    output_log("战场初始化完成！")
    with open("data/5O29_expansion.json", 'rb') as data_2:
        Data_2 = data_2.read()
    Character_GameVar.DefaultDict["characters"].update(json.loads(Data_2)["characters"])
    output_log("扩展包:[5Ω29]导入完成！")
    with open("data/Magiclegend_expansion.json", 'rb') as data_3:
        Data_3 = data_3.read()
    Character_GameVar.DefaultDict["characters"].update(json.loads(Data_3)["characters"])
    output_log("扩展包:[Legend]导入完成！")
    
    #测试包
    with open("data/generator_test.json", 'rb') as generator_test:
        Generator_test = generator_test.read()
    Character_GameVar.DefaultDict["characters"].update(json.loads(Generator_test)["characters"])
    
    #选择输入类型
    PInPut = input("是否批量输入T/F:")
    if PInPut == "T":
        Character_GameVar.InPut = 0
        with open(f"data/InPut.txt", 'rb') as c:
            for character in c:
                print(character.decode('utf-8'))
    else:
        Character_GameVar.InPut = 1

#进行游戏初始化操作
G_init()

while Character_GameVar.InPut:
    name = input("请输入一个角色:")
    roll = input("自定义数据T/F:")
    if roll == "T":
        '''
        [继承]
        如果发动了人物继承，则可以直接使用预设中人物的属性
        '''
        inherit = input("是否继承人物[F]:")
        if inherit == "F":
            inskill_list = input("选择攻击性技能继承[用-分隔]:").split("-")
            camp = input("input camp:")
            newD = {
                "name": name,
                "health": int(input("input health:")),
                "attack": int(input("input attack:")),
                "mana":   int(input("input mana:")),
                "speed":  int(input("input speed:")),
                "san":   int(input("input san:")),
                "camp":  camp,
                "normal_attack": ["P||会心一击||120*1||命中了***的要害"],
                "attribute_promotion": ["高级治愈术||health**attack||60**15||***的状态大幅恢复", "一往无前||attack||50||山岳般的力量增幅在***身上"],
                "special": {"special": "0"}
            }
            if inskill_list:
                for i in inskill_list:
                    if i in Character_GameVar.DefaultDict["AttackMethod"]:
                        newD["normal_attack"] += Character_GameVar.DefaultDict["AttackMethod"][i]
            if camp not in Character_GameVar.CampDictionary:
                Character_GameVar.CampDictionary[camp] = []
            Character_GameVar.CampDictionary[camp].append(newD)
            output_log("%s加入战场(%d/%d) 属于%s" % (Character_GameVar.CampDictionary[camp][-1]["name"], Character_GameVar.CampDictionary[camp]
                  [-1]["health"], Character_GameVar.CampDictionary[camp][-1]["health"], Character_GameVar.CampDictionary[camp][-1]["camp"]))
        else:
            if name and inherit != None:
                camp = input("input camp:")
                if camp == "init":
                    camp = Character_GameVar.DefaultDict["characters"][inherit]["camp"]
                if camp not in Character_GameVar.CampDictionary:
                    Character_GameVar.CampDictionary[camp] = []
                inskill_list = input("选择攻击性技能继承[用-分隔]:").split("-")
                if inherit in Character_GameVar.DefaultDict["characters"]:
                    character_copy = copy.deepcopy(Character_GameVar.DefaultDict["characters"][inherit])
                    character_copy["name"] = name
                    character_copy["camp"] = camp
                    Character_GameVar.CampDictionary[camp].append(character_copy)
                    if inskill_list:
                        for i in inskill_list:
                            if i in Character_GameVar.DefaultDict["AttackMethod"]:
                                Character_GameVar.CampDictionary[camp][-1]["normal_attack"] += Character_GameVar.DefaultDict["AttackMethod"][i]
                    output_log("%s加入战场(%d/%d) 属于%s" % (Character_GameVar.CampDictionary[camp][-1]["name"], Character_GameVar.CampDictionary[camp]
                          [-1]["health"], Character_GameVar.CampDictionary[camp][-1]["health"], Character_GameVar.CampDictionary[camp][-1]["camp"]))
            else:
                break
    else:
        if name:
            camp = input("input camp:")
            newD = {
                "name": name,
                "health": random.randint(1000, 2500),
                "attack": random.randint(5, 50),
                "mana": random.randint(5, 50),
                "speed": random.randint(5, 10),
                "san": random.randint(1, 40),
                "camp":  camp,
                "normal_attack": random.sample(Character_GameVar.DefaultDict["AttackMethod"]["P_skill"], 3)+random.sample(Character_GameVar.DefaultDict["AttackMethod"]["M_skill"], 3),
                "attribute_promotion": ["高级治愈术||health**attack||60**15||***的状态大幅恢复", "一往无前||attack||50||山岳般的力量增幅在***身上"],
                "special": {"special": "0"}
            }
            if camp not in Character_GameVar.CampDictionary:
                Character_GameVar.CampDictionary[camp] = []
            Character_GameVar.CampDictionary[camp].append(newD)
            output_log("%s加入战场(%d/%d) 属于%s" % (Character_GameVar.CampDictionary[camp][-1]["name"], Character_GameVar.CampDictionary[camp]
                  [-1]["health"], Character_GameVar.CampDictionary[camp][-1]["health"], Character_GameVar.CampDictionary[camp][-1]["camp"]))
        else:
            break

output_log("\n战斗开始！！\n")
Character_GameVar.START = True

def inflict_damage(skill, attacker, defender, att_list, attacked_index , attacked_camp ,addition, unusual=False):
    damage = att_list[0]
    if unusual == False:
        if skill[0] == "P":
            damage = att_list[0] + \
                random.randint(attacker["attack"]//2, attacker["attack"])
        elif skill[0] == "M":
            damage = att_list[0] + \
                random.randint(attacker["mana"]//2, attacker["mana"])
        elif skill[0] == "S":
            damage = att_list[0] + \
                random.randint(attacker["san"]//2, attacker["san"])
        if addition:
            damage = int(damage*addition)
    if damage >= 10:
        damage = random.randint(int(damage*0.8), int(damage*1.2))

    #结算伤害
    damage = origin_damage_calculate(damage, skill, defender)
    if unusual == False:
        damage_log = settlement_output(damage, skill ,defender,attacker)
        output_log(damage_log)
    if unusual == "state_damage":
        damage_log = settlement_output(damage, skill ,defender,attacker)
        output_log(damage_log)

    
    #受伤以及死亡结算
    Character_GameVar.CampDictionary[attacked_camp][attacked_index]["health"] -= damage[0]
    if Character_GameVar.CampDictionary[attacked_camp][attacked_index]["health"] <= 0:
        if Character_GameVar.field["owner"] == defender["name"]:
            _field_break = field_break(Character_GameVar.field,defender["name"],0,0)
            output_log(_field_break[0])
            if _field_break[1] != 0:
                Character_GameVar.field = _field_break[1]
        returnS = DIE(
            Character_GameVar.CampDictionary[attacked_camp][attacked_index]["special"], attacked_index, attacked_camp)
        if returnS == "DIE":
            Character_GameVar.CampDictionary[attacked_camp].remove(defender)
            output_log("%s 倒下了" % (defender["name"]))
            return "DIE"
        else:
            output_log("%s%s" % (returnS[0], returnS[1]))
    else:
        output_log("%s 还剩%d点生命值" % (
            defender["name"], Character_GameVar.CampDictionary[attacked_camp][attacked_index]["health"]))

def Unique_Skill(skill_special,special_list, skill_name, skill_damage, skill_type, 
                         skill_prologue, skill_log, skill_res, skill_ele,
                         charA, charB, charACamp, charBCamp):
    
    output_log("在%s的领域【%s】的加持下，%s\n" %(charA["name"],Character_GameVar.field["identify"],
                                  skill_prologue.replace('***', charA["name"])))
    if skill_special == "DAMAGE":
        now_type = ''
        special_list = special_list.split("**")
        for i in range(len(special_list)):
            special_list[i] = special_list[i].split("::")
        for type in special_list:
            for index in range(len(type)):
                if index == 0:
                    now_type = type[index]
                    continue
                if now_type == "base":
                    damage_class = type[index].split("--")
                    Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][damage_class[0]] -= int(damage_class[1])
                    if Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][damage_class[0]] <= 1:
                        Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][damage_class[0]] = 1
                elif now_type == "resistances" or now_type == "element_resistances":
                    damage_class = type[index].split("--")
                    if damage_class[0] not in Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][now_type]:
                        Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][now_type][damage_class[0]] = [-int(damage_class[1]),-float(damage_class[2])]
                    else:
                        Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][now_type][damage_class[0]][0] -= int(damage_class[1])
                        Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][now_type][damage_class[0]][1] -= float(damage_class[2])
        
        #编辑攻击
        skill = [skill_type,skill_name,skill_damage,skill_log,skill_res]
        if skill_ele != "NO":
            skill = [skill_type,skill_name,skill_damage,skill_log,skill_res,skill_ele]
        att_list = skill_damage.split("*")
        att_list[0] = int(att_list[0])
        att_list[1] = int(att_list[1])
        #判定领域增加伤害
        addition = float('1.%d'%(random.randint(0,Character_GameVar.field["value"])))
        Character_GameVar.field["value"] -= (random.randint(int(Character_GameVar.field["value"]/20)+1500,int(Character_GameVar.field["value"]/8)+1500)+1000)
        #发动攻击
        for i in range(att_list[1]):
            returnS = inflict_damage(skill, charA, charB, 
                        att_list, CharacterIndex[1], charBCamp,addition)
            if returnS == "DIE":
                break
        #维持领域存在
        if Character_GameVar.field["value"]<= 0:
            _field_break = field_break(Character_GameVar.field,random_charA["name"],1,0)
            output_log(_field_break[0])
            if _field_break[1] != 0:
                Character_GameVar.field = _field_break[1]
    
    if skill_special == "PLUNDER":
        now_type = ''
        special_list = special_list.split("**")
        for i in range(len(special_list)):
            special_list[i] = special_list[i].split("::")
        for type in special_list:
            for index in range(len(type)):
                if index == 0:
                    now_type = type[index]
                    continue
                if now_type == "base":
                    damage_class = type[index].split("--")
                    Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][damage_class[0]] -= int(damage_class[1])
                    Character_GameVar.CampDictionary[charACamp][CharacterIndex[0]][damage_class[0]] += int(damage_class[1])
                    if Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][damage_class[0]] <= 1:
                        Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][damage_class[0]] = 1
                elif now_type == "resistances" or now_type == "element_resistances":
                    damage_class = type[index].split("--")
                    if damage_class[0] not in Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][now_type]:
                        Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][now_type][damage_class[0]] = [-int(damage_class[1]),-float(damage_class[2])]
                    else:
                        Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][now_type][damage_class[0]][0] -= int(damage_class[1])
                        Character_GameVar.CampDictionary[charBCamp][CharacterIndex[1]][now_type][damage_class[0]][1] -= float(damage_class[2])
                    #夺取
                    if damage_class[0] not in Character_GameVar.CampDictionary[charACamp][CharacterIndex[0]][now_type]:
                        Character_GameVar.CampDictionary[charACamp][CharacterIndex[0]][now_type][damage_class[0]] = [int(damage_class[1]),float(damage_class[2])]
                    else:
                        Character_GameVar.CampDictionary[charACamp][CharacterIndex[0]][now_type][damage_class[0]][0] += int(damage_class[1])
                        Character_GameVar.CampDictionary[charACamp][CharacterIndex[0]][now_type][damage_class[0]][1] += float(damage_class[2])
        
        #编辑攻击
        skill = [skill_type,skill_name,skill_damage,skill_log,skill_res]
        if skill_ele != "NO":
            skill = [skill_type,skill_name,skill_damage,skill_log,skill_res,skill_ele]
        att_list = skill_damage.split("*")
        att_list[0] = int(att_list[0])
        att_list[1] = int(att_list[1])
        #判定领域增加伤害
        addition = float('1.%d'%(random.randint(0,Character_GameVar.field["value"])))
        Character_GameVar.field["value"] -= (random.randint(int(Character_GameVar.field["value"]/20)+1500,int(Character_GameVar.field["value"]/8)+1500)+1000)
        #发动攻击
        for i in range(att_list[1]):
            returnS = inflict_damage(skill, charA, charB, 
                        att_list, CharacterIndex[1], charBCamp,addition)
            if returnS == "DIE":
                break
        #维持领域存在
        if Character_GameVar.field["value"]<= 0:
            _field_break = field_break(Character_GameVar.field,random_charA["name"],1,0)
            output_log(_field_break[0])
            if _field_break[1] != 0:
                Character_GameVar.field = _field_break[1]


def Buff_skill(skill, random_charA, increaseList, increaseNUM, len, camp):
    for i in range(len):
        Character_GameVar.CampDictionary[camp][CharacterIndex[0]][increaseList[i]] += int(increaseNUM[i])
        if increaseList[i] == "health":
            if Character_GameVar.CampDictionary[camp][CharacterIndex[0]]["health"] >= Character_GameVar.CampDictionary[camp][CharacterIndex[0]]["original_health"]:
                Character_GameVar.CampDictionary[camp][CharacterIndex[0]]["health"] = Character_GameVar.CampDictionary[camp][CharacterIndex[0]]["original_health"]
    if skill[3] != "NOD":
        SkillD = ','+skill[3]
        output_log("%s发动了%s%s" % (random_charA["name"], skill[0], SkillD.replace(
            '***', random_charA["name"])))
    else:
        output_log("%s发动了%s" % (random_charA["name"], skill[0]))
    pre_output()

def RES_skill(skill,index,random_charA, increaseList, camp):
    for one in increaseList:
        effect = one.split("--")
        Character_GameVar.CampDictionary[camp][CharacterIndex[0]][effect[0]][effect[1]][0] += float(effect[2])
        Character_GameVar.CampDictionary[camp][CharacterIndex[0]][effect[0]][effect[1]][1] += float(effect[3])
    
    skill_time = "==="+str(int(skill[3].replace("===",""))-1)+"==="
    #output_log("%s使用次数-1，还剩%s次" % (skill[0],skill_time))

    change = Character_GameVar.CampDictionary[camp][CharacterIndex[0]]["resistance_enhancement"][index].replace(skill[3],skill_time)
    Character_GameVar.CampDictionary[camp][CharacterIndex[0]]["resistance_enhancement"][index] = change

    if skill[2] != "NOD":
        description = skill[2].replace('***', random_charA["name"])
        output_log("%s发动了%s,%s" % (random_charA["name"], skill[0], description))
    else:
        output_log("%s发动了%s" % (random_charA["name"], skill[0]))
    pre_output()
    

def DIE(special, num, camp):
    if "immortal" in special:
        if special["immortal"][1] > 0:
            Character_GameVar.CampDictionary[camp][num]["special"]["immortal"][1] -= 1
            Character_GameVar.CampDictionary[camp][num]["health"] = Character_GameVar.CampDictionary[camp][num]["special"]["immortal"][2]
            return [Character_GameVar.CampDictionary[camp][num]["name"],special["immortal"][0]]
        else:
            return "DIE"
    elif "stage" in special:
        if special["stage"][1] > 0:
            Character_GameVar.CampDictionary[camp][num]["special"]["stage"][1] -= 1
            Character_GameVar.CampDictionary[camp][num]["health"] = Character_GameVar.CampDictionary[camp][num]["special"]["stage"][2]
            Character_GameVar.CampDictionary[camp][num]["attack"] = Character_GameVar.CampDictionary[camp][num]["special"]["stage"][3]
            Character_GameVar.CampDictionary[camp][num]["mana"] = Character_GameVar.CampDictionary[camp][num]["special"]["stage"][4]
            Character_GameVar.CampDictionary[camp][num]["speed"] = Character_GameVar.CampDictionary[camp][num]["special"]["stage"][5]
            Character_GameVar.CampDictionary[camp][num]["san"] = Character_GameVar.CampDictionary[camp][num]["special"]["stage"][6]
            temp_name = Character_GameVar.CampDictionary[camp][num]["name"]
            Character_GameVar.CampDictionary[camp][num]["name"] = Character_GameVar.CampDictionary[camp][num]["special"]["stage"][7]
            return [temp_name,special["stage"][0]]
    elif "new_state" in special:
        if special["new_state"][0] > 0:
            this_time = Character_GameVar.CampDictionary[camp][num]["special"]["new_state"][0]
            Character_GameVar.CampDictionary[camp][num]["special"]["new_state"][0] -= 1
            keys = Character_GameVar.CampDictionary[camp][num]["special"]["new_state"][this_time].keys()
            keys = list(keys)
            keys.remove("narrate")
            narrate = Character_GameVar.CampDictionary[camp][num]["special"]["new_state"][this_time]["narrate"]
            temp_name = Character_GameVar.CampDictionary[camp][num]["name"]
            for key in keys:
                Character_GameVar.CampDictionary[camp][num][key] = Character_GameVar.CampDictionary[camp][num]["special"]["new_state"][this_time][key]
            return [temp_name,narrate]
        else:
            return "DIE"
    return "DIE"


while len(Character_GameVar.CampDictionary) > 1:
    #攻守方阵营以及角色选择
    randomCamp = random.sample(Character_GameVar.CampDictionary.keys(), 2)
    if Character_GameVar.CampDictionary[randomCamp[0]] == []:
        del Character_GameVar.CampDictionary[randomCamp[0]]
        continue
    if Character_GameVar.CampDictionary[randomCamp[1]] == []:
        del Character_GameVar.CampDictionary[randomCamp[1]]
        continue
    random_charA = random.choice(Character_GameVar.CampDictionary[randomCamp[0]])
    random_charB = random.choice(Character_GameVar.CampDictionary[randomCamp[1]])
    CharacterIndex = [Character_GameVar.CampDictionary[randomCamp[0]].index(
        random_charA), Character_GameVar.CampDictionary[randomCamp[1]].index(random_charB)]
    if random_charA["camp"] == random_charB["camp"]:
        continue

    #判定是否躲避

    att_type = Probabilistic_classifier()
    _decision = dodge_decision(att_type,Character_GameVar.field,randomCamp,random_charA,random_charB)
    if _decision[1] == 0:
        output_log(_decision[0])
        continue
    else:
        if _decision[0] != 0:
            output_log(_decision[0])

    #判定是否领域技能
    if Character_GameVar.field["owner"] == random_charA["name"]:
        if att_type == 'normal_attack':
            if random.randint(1,20) == 1:
                att_type = 'unique_skill'

    if att_type == 'normal_attack':
        print("______________________")
        print(random_charA["name"],random_charA["health"])
        print(random_charB["name"],random_charB["health"])
        print("______________________")

        if random_charA["normal_attack"]:
            skill = random.choice(random_charA["normal_attack"]).split("||")
            att_list = skill[2].split("*")
            att_list[0] = int(att_list[0])
            att_list[1] = int(att_list[1])
            addition = 0
            #判定领域是否增加伤害
            if random_charA["name"] == Character_GameVar.field["owner"]:
                addition = float('1.%d'%(random.randint(0,Character_GameVar.field["value"])))
                output_log("%s, %s在【%s】的加持下，技能的威力上升了！\n" %(random.choice(Character_GameVar.field["maintain_log"]),
                            random_charA["name"],Character_GameVar.field["identify"]))
                Character_GameVar.field["value"] -= (random.randint(int(Character_GameVar.field["value"]/20)+500,int(Character_GameVar.field["value"]/8)+500)+1000)
            elif random_charB["name"] == Character_GameVar.field["owner"]:
                addition = 1-(float('0.%d'%(random.randint(0,Character_GameVar.field["value"]))))/2
                output_log("%s, %s在【%s】的加持下，抗性显著提高了！\n" %(random.choice(Character_GameVar.field["maintain_log"]),
                            random_charB["name"],Character_GameVar.field["identify"]))
                Character_GameVar.field["value"] -= (random.randint(int(Character_GameVar.field["value"]/20)+500,int(Character_GameVar.field["value"]/8)+500)+1000)
            for i in range(att_list[1]):
                returnS = inflict_damage(skill, random_charA, random_charB, 
                            att_list, CharacterIndex[1] , randomCamp[1],addition)   
                if returnS == "DIE":
                    break
            if random_charA["name"] == Character_GameVar.field["owner"]:
                if Character_GameVar.field["value"]<= 0:
                        _field_break = field_break(Character_GameVar.field,random_charA["name"],1,0)
                        output_log(_field_break[0])
                        if _field_break[1] != 0:
                            Character_GameVar.field = _field_break[1]
            elif random_charB["name"] == Character_GameVar.field["owner"]:
                if Character_GameVar.field["value"]<= 0:
                        _field_break = field_break(Character_GameVar.field,random_charB["name"],1,0)
                        output_log(_field_break[0])
                        if _field_break[1] != 0:
                            Character_GameVar.field = _field_break[1]
            pre_output()
        else:
            continue
    elif att_type == 'attribute_promotion':
        if random_charA["attribute_promotion"]:
            skill = random.choice(random_charA["attribute_promotion"]).split("||")
            increaseList = skill[1].split("**")
            increaseNUM = skill[2].split("**")
            Buff_skill(skill, random_charA, increaseList,
                    increaseNUM, len(increaseList), randomCamp[0])
        else:
            continue
    elif att_type == 'resistance_enhancement':
        if random_charA["resistance_enhancement"]:
            skill = random.choice(random_charA["resistance_enhancement"])
            index = Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]]["resistance_enhancement"].index(skill)
            skill = skill.split("||")
            if int(skill[3].replace("===","")) <= 0:
                #output_log("%s没有使用次数了，无法使用！" % (skill[0]))
                continue
            increaseList = skill[1].split("**")
            RES_skill(skill,index,random_charA, increaseList,randomCamp[0])
        else:
            continue
    elif att_type == 'effect_application':
        if random_charA["effect_application"]:
            effect_skill = random.choice(random_charA["effect_application"])
            if effect_skill["target"] == "self":
                target = [randomCamp[0],CharacterIndex[0],random_charA["name"]]
            elif effect_skill["target"] == "enemy":
                target = [randomCamp[1],CharacterIndex[1],random_charB["name"]]
            series_number = effect_skill["series_number"]
            narrate = effect_skill["narrate"]
            duration = [effect_skill["duration"],Character_GameVar.counter[0]]
            level = effect_skill["level"]
            normal = effect_skill["normal"]
            special = effect_skill["special"]
            cache = effect_skill["cache"]
            VFX_log = effect_skill["VFX_log"]
            die_log = effect_skill["die_log"]
            _invalid = False
            for state in Character_GameVar.CampDictionary[target[0]][target[1]]["status"]:
                if state["series_number"] == series_number:
                    _invalid = True
            if _invalid:
                continue
            effect = infliction_effect(series_number,effect_skill["name"], target, duration, level, normal, 
                                       special, cache, VFX_log, die_log)
            Character_GameVar.CampDictionary[target[0]][target[1]]["status"].append(effect)
            output_log("%s发动了%s，%s"%(random_charA["name"],effect_skill["name"],narrate.replace("***",target[2])))

    elif att_type == 'morphology_skill':
        if random_charA["morphology_skill"]:
            #序号存贮更改操作
            Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]]["morphology_skill"][random_charA["morphology_skill"][0]][2] = 0
            skill_num = NCrandom(1,len(random_charA["morphology_skill"])-1,random_charA["morphology_skill"][0])
            morphology_skill = random_charA["morphology_skill"][skill_num]
            origin_index = Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]]["morphology_skill"][0]
            Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]]["morphology_skill"][0] = skill_num
            Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]]["morphology_skill"][skill_num][2] = 1
            #形态转变
            skill_name = morphology_skill[0]
            morphology_name = morphology_skill[1]
            origin_morphology = random_charA["morphology"][random_charA["morphology_skill"][origin_index][1]]
            morphology = random_charA["morphology"][morphology_name]
            #编号临时保存
            origin_keys = origin_morphology.keys()
            origin_keys = list(origin_keys)
            keys = morphology.keys()
            keys = list(keys)
            #输出
            narrate = morphology["narrate"].replace("***",random_charA["name"])
            output_log("%s发动了%s，%s" % (random_charA["name"],skill_name,narrate))
            #退出原形态
            for key in origin_keys:
                if key == "name":
                    _changeName = Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key].replace(origin_morphology[key],"")
                    Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key] = _changeName
                elif key in ["health","attack","mana","speed","san"]:
                    Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key] -= origin_morphology[key]
                elif key in ["resistances","element_resistances"]:
                    for type,value in origin_morphology[key].items():
                        if type in Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key]:
                            if type in origin_morphology[key]:
                                origin_morphology_value = origin_morphology[key][type]
                                Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key][type][0] -= origin_morphology_value[0]
                                Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key][type][1] -= origin_morphology_value[1]
                else:
                    continue
            #进入新形态
            for key in keys:
                if key == "name":
                    Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key] += morphology[key]
                elif key in ["health","attack","mana","speed","san"]:
                    Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key] += morphology[key]
                elif key in ["resistances","element_resistances"]:
                    for type,value in morphology[key].items():
                        if type in Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key]:
                            Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key][type][0] += value[0]
                            Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key][type][1] += value[1]
                        else:
                            Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key][type] = value
                elif key in ["name","normal_attack","attribute_promotion","resistance_enhancement","field","special"]:
                    Character_GameVar.CampDictionary[randomCamp[0]][CharacterIndex[0]][key] = morphology[key]
                else:
                    continue
        else:
            continue
    elif att_type == 'field':
        if random_charA["field"]:
            char_field = random.choice(random_charA["field"])
            if Character_GameVar.field["owner"] == random_charA["name"]:
                continue
            if Character_GameVar.field["Absolute_Weight"] > (char_field[6]+2):
                continue
            if (Character_GameVar.field["value"]+5000) > char_field[5]:
                continue
            if Character_GameVar.field["identify"] != "init":
                _field_break = field_break(Character_GameVar.field,Character_GameVar.field["owner"],2,random_charA["name"])
                output_log(_field_break[0])
                if _field_break[1] != 0:
                    Character_GameVar.field = _field_break[1]
            Character_GameVar.field["identify"] = char_field[0]
            Character_GameVar.field["owner"] = random_charA["name"]
            Character_GameVar.field["owner_camp"] = randomCamp[0]
            Character_GameVar.field["Absolute_Weight"] = char_field[6]
            Character_GameVar.field["init_value"] = char_field[5]
            Character_GameVar.field["value"] = char_field[5]
            Character_GameVar.field["maintain_log"] = char_field[4].split("||")
            Character_GameVar.field["break_log"] = char_field[2]
            Character_GameVar.field["die_log"] = char_field[3]
            Character_GameVar.field["unique_skill"] = char_field[7]

            output_log("%s %s展开了领域！【%s】\n" % (char_field[1],random_charA["name"], 
                                       char_field[0]))
        else:
            continue
    elif att_type == 'unique_skill':
        if Character_GameVar.field["unique_skill"]:
            skill = random.choice(Character_GameVar.field["unique_skill"])
            skill = skill.split("||")
            skill_type = skill[0]
            skill_name = skill[1]
            skill_damage = skill[2]
            skill_special = skill[3]
            special_list = skill[4]
            skill_prologue = skill[5]
            skill_log = skill[6]
            skill_res = skill[7]
            skill_ele = skill[8]
            Unique_Skill(skill_special,special_list, skill_name, skill_damage, skill_type, 
                         skill_prologue, skill_log, skill_res, skill_ele,
                         random_charA, random_charB, randomCamp[0], randomCamp[1])
        else:
            continue

    output_log(" ")

for a, b in Character_GameVar.CampDictionary.items():
    output_log("最后的胜利阵营是%s" % (a))
    winner = []
    for i in b:
        winner.append(i["name"])
    output_log("胜利者是<%s>" % (",".join(winner)))
    
Character_GameVar.game_log.close()