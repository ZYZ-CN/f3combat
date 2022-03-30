from XivCombat.strategies import *
from XivCombat import define
from XivCombat.multi_enemy_selector import Rectangle, NearCircle, select

"""
53,连击,1
54,正拳,4
56,崩拳,6
60,金刚体势,15
61,双掌打,18
62,破坏神冲,26
66,破碎拳,30
70,地烈劲,30
73,疾风体势,34
71,罗刹冲,35
63,红莲体势,40
65,真言,42
16473,四面脚,45
69,震脚,50
74,双龙脚,50
4262,演武,52
3546,斗气,54
3547,阴阳斗气斩,54
3545,苍气炮,56
3543,斗魂旋风脚,60
7394,金刚极意,64
7395,红莲极意,68
7396,义结金兰,70
16474,万象斗气圈,74
16475,无我,78
16476,六合星导脚,80
"""
"""
107,魔猿形,摆出魔猿身形
108,盗龙形,摆出盗龙身形
109,猛豹形,摆出猛豹身形
110,震脚,能够打出三种身形的所有招式
2513,无相身形,能够打出三种身形的所有招式，并触发对应的追加效果
1861,连击效果提高,下次发动连击的威力提高
101,双掌打,攻击所造成的伤害提高
246,破碎拳,体力逐渐减少
"""

a1 = Rectangle(10, 2)
a2 = NearCircle(5)


def cnt_enemy(data: 'LogicData', ability):
    target, cnt = select(data, data.valid_enemies, ability)
    if not cnt: return data.target, 0
    if data.config['single'] == define.FORCE_SINGLE: return data.target, 1
    if data.config['single'] == define.FORCE_MULTI: return data.target, 3
    return target, cnt


def res_lv(data: 'LogicData'):
    match data.config['resource']:
        case define.RESOURCE_SQUAND:
            return 2
        case define.RESOURCE_NORMAL:
            return 1
        case define.RESOURCE_STINGY:
            return 0
        case _:
            return 1


def job_priority(actor):
    if actor.job.is_dps: return 3
    if actor.job.is_tank: return 2
    if actor.job.is_healer: return 1
    return 0


class MonkLogic(Strategy):
    name = "monk_logic"
    job = "Monk"

    default_data = {
        'jump_distance': 0,
    }

    def global_cool_down_ability(self, data: 'LogicData') -> AnyUse:
        if data.target_distance > 4:
            if data.me.level >= 54 and data.gauge.chakra_stacks < 5:
                return UseAbility(3546)
            return
        t, cnt = cnt_enemy(data, a2)
        if 108 in data.effects and data.me.level >= 4:
            if cnt > 2 and data.me.level >= 45 and 101 in data.effects: return UseAbility(16473)
            if data.me.level >= 18 and (101 not in data.effects or data.effects[101].timer <= 4 or res_lv(data) and data[7395] < 3):
                return UseAbility(61)
            return UseAbility(54)
        if 109 in data.effects and data.me.level >= 6:
            if cnt > 1 and data.me.level >= 30: return UseAbility(70)
            t_effect = data.target.effects.get_dict(source=data.me.id)
            if data.me.level >= 30 and (246 not in t_effect or t_effect[246].timer <= 6):
                return UseAbility(66)
            return UseAbility(56)
        if cnt > 2 and data.me.level >= 26: return UseAbility(62)
        if data.me.level >= 50 and 1861 not in data.effects:
            return UseAbility(74)
        return UseAbility(53)

    def non_global_cool_down_ability(self, data: 'LogicData') -> AnyUse:
        if not res_lv(data) or data.target_distance > 4: return
        buff_skills = [data[s] for s in [7396, 7395, 69] if data[s] < 70]
        t, cnt = cnt_enemy(data, a2)
        if buff_skills and max(buff_skills) < 5 and not min(buff_skills):
            if not data[7396] and 108 in data.effects:
                return UseAbility(7396)
            if not data[7395] and 109 in data.effects:
                return UseAbility(7395)
            if not data[69] and cnt < 3 and min(data[7396], data[7395]) > 80:
                return UseAbility(69)
        if data.gauge.chakra_stacks > 4:
            t, cnt = cnt_enemy(data, a1)
            return UseAbility(16474, t.id) if cnt > 1 and data.me.level >= 74 else UseAbility(3547)
        if data[71] < 5 and data.target_distance <= float(data.config['jump_distance']) <= 20:
            return UseAbility(71)
        if not data[3543]: return UseAbility(3543)
        if not data[3545]: return UseAbility(3545)
