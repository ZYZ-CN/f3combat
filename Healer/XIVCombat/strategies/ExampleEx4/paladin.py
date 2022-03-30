from XivCombat.utils import a, s, cnt_enemy, res_lv, find_area_belongs_to_me
from XivCombat.strategies import *
from XivCombat import define
from XivCombat.multi_enemy_selector import Rectangle, NearCircle, circle, FarCircle
from .utils import mo_provoke_and_shirk

total_eclipse = NearCircle(5.)
confiteor = FarCircle(25, 5)
confiteor_combos = {a('悔罪'), a('信念之剑')}
dot_status = {s('英勇之剑'), s('沥血剑')}


def get_dot_targets(data: 'LogicData'):
    for enemy in data.valid_enemies:
        e_effects = enemy.effects.get_dict()
        if all(s not in e_effects or e_effects[s].timer < 3 for s in dot_status) and data.ttk(enemy) > 10:
            yield enemy


class Paladin(Strategy):
    name = 'ny/pld'
    job = 'Paladin'

    @mo_provoke_and_shirk
    def process_ability_use(self, data: 'LogicData', action_id: int, target_id: int) -> None | Tuple[int, int] | UseAbility:
        if action_id == a('保护') or action_id == a('干预') or action_id == a('盾牌猛击'):
            mo_entity = api.get_mo_target()
            if mo_entity and api.action_type_check(action_id, mo_entity):
                return UseAbility(action_id, mo_entity.id)

    def global_cool_down_ability(self, data: 'LogicData') -> UseAbility | UseItem | UseCommon | None:

        if data.target_distance <= 3:
            single_target = data.target
            target_distance = data.target_distance
        else:
            single_target = data.get_target(define.DISTANCE_NEAREST, data.enemy_can_attack_by(a('投盾')))
            if not single_target: return
            target_distance = data.actor_distance_effective(single_target)
            if target_distance > 25: return

        res = res_lv(data)
        aoe_target, aoe_cnt = cnt_enemy(data, total_eclipse, data.me)

        if target_distance < 5:
            if data.me.level >= 40 and data.combo_id == a('全蚀斩') and aoe_cnt:
                return UseAbility(a('日珥斩'), aoe_target.id)
            if aoe_cnt < 3:
                if s('忠义之剑') in data.effects and res:
                    return UseAbility(a('赎罪剑'), single_target.id)
                if data.me.level >= 26 and data.combo_id == a('暴乱剑'):
                    if data.me.level >= 54:
                        dot_targets = sorted(
                            (target for target in get_dot_targets(data) if data.actor_distance_effective(target) <= 3),
                            key=lambda x: x.current_hp,
                            reverse=True
                        )
                        if dot_targets: return UseAbility(a('沥血剑'), dot_targets[0].id)
                    if s('忠义之剑') in data.effects:
                        return UseAbility(a('赎罪剑'), single_target.id)
                    return UseAbility(a('战女神之怒'), single_target.id)
                if data.me.level >= 4 and data.combo_id == a('先锋剑'):
                    return UseAbility(a('暴乱剑'), single_target.id)

        if s('安魂祈祷') in data.effects and data.me.current_mp >= 1000 and (target_distance > 5 or s('战逃反应') not in data.effects):
            stack = data.effects[s('安魂祈祷')].param
            if data.me.level < 80 or (stack > 1 and data.me.current_mp >= 2000):
                return UseAbility(a('圣环') if aoe_cnt >= 2 and data.me.level >= 72 else a('圣灵'), single_target.id)
            return UseAbility(a('悔罪'), cnt_enemy(data, confiteor, single_target)[0].id)
        if data.me.level >= 90 and data.combo_id in confiteor_combos:
            return UseAbility(a('悔罪'), cnt_enemy(data, confiteor, single_target)[0].id)
        if target_distance >= 20: return
        if target_distance > 5:
            if not data.gcd:
                return UseAbility(
                    a('圣灵') if data.me.current_mp >= 2000 and data.me.level >= 64 and not data.is_moving else a('投盾'),
                    single_target.id
                )
        else:
            return UseAbility(a('日珥斩') if aoe_cnt > 2 and data.me.level > 6 else a('先锋剑'), single_target.id)

    def non_global_cool_down_ability(self, data: 'LogicData') -> AnyUse:
        if not res_lv(data): return

        if data.target_distance <= 3:
            single_target = data.target
        else:
            single_target = data.get_target(define.DISTANCE_NEAREST, data.enemy_can_attack_by(a('投盾')))
            if not single_target or data.actor_distance_effective(single_target) > 5: return

        if not data[a('战逃反应')] and s('安魂祈祷') not in data.effects and data.combo_id not in confiteor_combos:
            return UseAbility(a('战逃反应'), single_target.id, wait_until=lambda: s('战逃反应') in data.refresh_cache('effects'))

        if not data[a('安魂祈祷')] and data.effect_time(s('战逃反应')) < 10:
            return UseAbility(a('安魂祈祷'), single_target.id, wait_until=lambda: s('安魂祈祷') in data.refresh_cache('effects'))

        if s('战逃反应') in data.effects or data[a('战逃反应')] > 15:
            if not data[a('深奥之灵')]: return UseAbility(a('深奥之灵'), single_target.id)
            if not data[a('厄运流转')]:
                aoe_cnt = cnt_enemy(data, total_eclipse, data.me)[1]
                if aoe_cnt > len(data.valid_enemies) / 2:
                    return UseAbility(a('厄运流转'), single_target.id)
                # data.plugin.logger(aoe_cnt, len(data.valid_enemies))
        if not data.actor_distance_effective(single_target) and data[a('调停')] < 5:
            return UseAbility(a('调停'), single_target.id)
