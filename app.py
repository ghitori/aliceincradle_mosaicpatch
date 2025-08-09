import os
import json
import random
import copy
from datetime import datetime, timedelta
from flask import Flask, render_template, session, redirect, url_for, request, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 调试模式设置
DEBUG_MODE = True

# 场景目录
SCENES_DIR = 'scenes'
# 对话目录
TALK_DIR = 'talk'
# 游戏状态初始化文件
GAME_STATE_INIT_FILE = 'game_state_init.json'
# 物品效果定义文件
ITEM_EFFECTS_FILE = 'item_effects.json'
# 咒语定义文件
SPELLS_FILE = 'spells.json'
# 敌人定义文件
ENEMY_FILE = 'enemy.json'
# 成就定义文件
ACHIEVEMENTS_FILE = 'achievements.json'

# 场景缓存
scenes_cache = {}
# 对话缓存
talk_cache = {}
# 物品效果缓存
item_effects_cache = {}
# 游戏状态初始化缓存
game_state_init_cache = {}
# 咒语缓存
spells_cache = {}
# 敌人缓存
enemies_cache = {}
# 成就缓存
achievements_cache = {}

def load_json_file(filepath):
    """加载JSON文件，如果文件不存在或读取失败则抛出异常"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} does not exist")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading {filepath}: {str(e)}")

def load_item_effects():
    """加载物品效果定义"""
    global item_effects_cache
    if not item_effects_cache:
        item_effects_cache = load_json_file(ITEM_EFFECTS_FILE)
    return item_effects_cache

def load_game_state_init():
    """加载游戏状态初始化数据"""
    global game_state_init_cache
    if not game_state_init_cache:
        game_state_init_cache = load_json_file(GAME_STATE_INIT_FILE)
    return game_state_init_cache

def load_spells():
    """加载咒语定义"""
    global spells_cache
    if not spells_cache:
        spells_cache = load_json_file(SPELLS_FILE)
    return spells_cache

def load_enemies():
    """加载敌人定义"""
    global enemies_cache
    if not enemies_cache:
        enemies_cache = load_json_file(ENEMY_FILE)
    return enemies_cache

def load_achievements():
    """加载成就定义"""
    global achievements_cache
    if not achievements_cache:
        achievements_cache = load_json_file(ACHIEVEMENTS_FILE)
    return achievements_cache

def load_scenes():
    """加载所有场景"""
    global scenes_cache
    scenes_cache = {}
    
    if not os.path.exists(SCENES_DIR):
        os.makedirs(SCENES_DIR)
        print(f"Created scenes directory: {SCENES_DIR}")
        return
    
    for filename in os.listdir(SCENES_DIR):
        if filename.endswith('.json'):
            scene_id = filename[:-5]
            filepath = os.path.join(SCENES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    scenes_cache[scene_id] = json.load(f)
                print(f"Loaded scene: {scene_id}")
            except Exception as e:
                raise Exception(f"Error loading scene {scene_id}: {str(e)}")

def load_talks():
    """加载所有对话事件"""
    global talk_cache
    talk_cache = {}
    
    if not os.path.exists(TALK_DIR):
        os.makedirs(TALK_DIR)
        print(f"Created talk directory: {TALK_DIR}")
        return
    
    for filename in os.listdir(TALK_DIR):
        if filename.endswith('.json'):
            talk_id = filename[:-5]
            filepath = os.path.join(TALK_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    talk_cache[talk_id] = json.load(f)
                print(f"Loaded talk: {talk_id}")
            except Exception as e:
                raise Exception(f"Error loading talk {talk_id}: {str(e)}")

def get_scene(scene_id):
    """获取场景数据"""
    if scene_id in scenes_cache:
        return scenes_cache[scene_id]
    
    filepath = os.path.join(SCENES_DIR, f"{scene_id}.json")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Scene file {filepath} does not exist")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            scene_data = json.load(f)
            scenes_cache[scene_id] = scene_data
            return scene_data
    except Exception as e:
        raise Exception(f"Error reloading scene {scene_id}: {str(e)}")

def get_talk(talk_id):
    """获取对话事件数据"""
    if talk_id in talk_cache:
        return talk_cache[talk_id]
    
    filepath = os.path.join(TALK_DIR, f"{talk_id}.json")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Talk file {filepath} does not exist")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            talk_data = json.load(f)
            talk_cache[talk_id] = talk_data
            return talk_data
    except Exception as e:
        raise Exception(f"Error reloading talk {talk_id}: {str(e)}")

def get_all_scene_ids():
    """获取所有场景ID"""
    scene_ids = []
    if os.path.exists(SCENES_DIR):
        for filename in os.listdir(SCENES_DIR):
            if filename.endswith('.json'):
                scene_ids.append(filename[:-5])
    return scene_ids

# 计算物品总数
def count_items(item_dict):
    return sum(item_dict.values()) if isinstance(item_dict, dict) and item_dict else 0

# 设置初始货币
def set_initial_currency():
    return {'galleons': random.randint(20, 50), 'sickle': random.randint(50, 100), 'knut': random.randint(100, 200)}

# 应用启动时加载所有场景、对话、咒语、敌人和成就
load_scenes()
load_talks()
load_spells()
load_enemies()
load_achievements()

# 初始化游戏状态
def init_game_state(name, gender):
    if 'game_state' in session:
        session.pop('game_state')
    
    initial_state = load_game_state_init()
    
    currency = set_initial_currency()
    initial_state['stats']['galleons'] = currency['galleons']
    initial_state['stats']['sickle'] = currency['sickle']
    initial_state['stats']['knut'] = currency['knut']
    initial_state['known_spells'] = []
    initial_state['achievements'] = []  # 初始化成就列表
    
    initial_state['character'] = {
        'name': name,
        'gender': gender
    }
    
    initial_state['current_scene'] = 'dormitory'
    initial_state['visited'] = ['dormitory']
    initial_state['unlocked_scenes'] = ['dormitory']
    initial_state['previous_state'] = None
    initial_state['current_talk'] = None
    initial_state['current_talk_node'] = None
    initial_state['grade'] = 1
    initial_state['battle'] = {
        'enemy': None,
        'battle_log': [],
        'selected_skills': [],
        'dodge': False,
        'defense': False,
        'persistent_damage': {'damage': 0, 'duration': 0},
        'buff': {'attack_boost': 0, 'duration': 0}
    }
    
    session['game_state'] = initial_state

# 开始游戏路由
@app.route('/')
def index():
    return render_template('index.html')

# 处理开始游戏
@app.route('/start_game', methods=['POST'])
def start_game():
    name = request.form.get('name')
    gender = request.form.get('gender')
    
    if not name or not gender:
        return redirect(url_for('index'))
    
    init_game_state(name, gender)
    return redirect(url_for('game'))

# 游戏主界面
@app.route('/game')
def game():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session['game_state']
    current_scene_id = game_state['current_scene']
    current_scene = get_scene(current_scene_id)
    
    is_gryffindor_dorm = current_scene_id == 'dormitory'
    
    event_message = None
    if 'last_scene' not in game_state or game_state['last_scene'] != current_scene_id:
        pass
    
    game_state['last_scene'] = current_scene_id
    session['game_state'] = game_state
    
    all_scene_ids = get_all_scene_ids()
    
    if DEBUG_MODE:
        scene_ids_for_debug = all_scene_ids
    else:
        scene_ids_for_debug = [sid for sid in all_scene_ids if sid in game_state['unlocked_scenes']]
    
    can_undo = game_state['previous_state'] is not None
    
    if game_state.get('current_talk') and game_state.get('current_talk_node'):
        talk_data = get_talk(game_state['current_talk'])
        current_node = talk_data['dialogue'][game_state['current_talk_node']]
        return render_template('game.html',
                             game_state=game_state,
                             scene=talk_data,
                             stats=game_state['stats'],
                             inventory=game_state['inventory'],
                             containers=game_state['containers'],
                             equipment=game_state['equipment'],
                             character=game_state['character'],
                             event_message=session.pop('action_event', None),
                             debug_mode=DEBUG_MODE,
                             all_scene_ids=scene_ids_for_debug,
                             last_action=game_state.get('last_action'),
                             current_scene_id=current_scene_id,
                             can_undo=can_undo,
                             is_gryffindor_dorm=is_gryffindor_dorm,
                             is_talk=True,
                             current_talk_node=current_node)

    return render_template('game.html',
                         game_state=game_state,
                         scene=current_scene,
                         stats=game_state['stats'],
                         inventory=game_state['inventory'],
                         containers=game_state['containers'],
                         equipment=game_state['equipment'],
                         character=game_state['character'],
                         event_message=session.pop('action_event', None),
                         debug_mode=DEBUG_MODE,
                         all_scene_ids=scene_ids_for_debug,
                         last_action=game_state.get('last_action'),
                         current_scene_id=current_scene_id,
                         can_undo=can_undo,
                         is_gryffindor_dorm=is_gryffindor_dorm,
                         is_talk=False)

# 处理玩家选择
@app.route('/choose', methods=['POST'])
def choose():
    game_state = session['game_state']
    
    previous_state = copy.deepcopy(game_state)
    game_state['previous_state'] = previous_state
    
    choice_index = int(request.form['choice'])
    current_scene_id = game_state['current_scene']
    current_scene = get_scene(current_scene_id)
    
    if choice_index < 0 or choice_index >= len(current_scene['choices']):
        return redirect(url_for('game'))
    
    choice = current_scene['choices'][choice_index]
    
    if choice.get('type') == 'talk':
        talk_id = random.choice(choice['talk_files'])
        game_state['current_talk'] = talk_id
        game_state['current_talk_node'] = '1-1'
        session['game_state'] = game_state
        return redirect(url_for('game'))
    
    action_event = None
    item_messages = []
    if 'random_events' in choice:
        for event in choice.get('random_events', []):
            if random.random() < event['chance']:
                action_event = event['event']
                if 'next' in event and 'battle' in event['next']:
                    enemy_name = event.get('enemy')
                    if enemy_name:
                        enemies = load_enemies()
                        enemy = next((e for e in enemies['enemies'] if e['name'] == enemy_name), None)
                        if enemy:
                            enemy_copy = copy.deepcopy(enemy)
                            game_state['battle']['enemy'] = enemy_copy
                            game_state['battle']['battle_log'] = []
                            game_state['battle']['selected_skills'] = []
                            game_state['battle']['dodge'] = False
                            session['game_state'] = game_state
                            return redirect(url_for('battle'))
                        else:
                            session['action_event'] = f"未找到敌人：{enemy_name}"
                    else:
                        session['action_event'] = "随机事件中未指定敌人"
                # 处理其他事件（物品、效果等）
                if 'effect' in event:
                    for key, value in event['effect'].items():
                        game_state['stats'][key] = min(max(game_state['stats'][key] + value, 0), 100)
                if 'item' in event:
                    item = event['item']
                    quantity = 1
                    if count_items(game_state['inventory']) + quantity <= 10:
                        game_state['inventory'][item] = game_state['inventory'].get(item, 0) + quantity
                        item_messages.append(f"获得了 {item} x{quantity}")
                        # 检查获得物品的成就
                        achievements = load_achievements()
                        for ach in achievements:
                            if ach['id'] == "collect_first_item" and ach['id'] not in game_state['achievements']:
                                game_state['achievements'].append(ach['id'])
                                session['action_event'] = f"成就解锁：{ach['name']}"
                break
    
    if 'items' in choice:
        for item_action in choice['items']:
            if random.random() < item_action.get('chance', 1.0):
                action = item_action['action']
                item = item_action['item']
                container = item_action.get('container', '')
                quantity = item_action.get('quantity', 1)
                
                if action == 'add' and count_items(game_state['inventory']) + quantity <= 10:
                    game_state['inventory'][item] = game_state['inventory'].get(item, 0) + quantity
                    item_messages.append(f"获得了 {item} x{quantity}")
                    # 检查获得物品的成就
                    achievements = load_achievements()
                    for ach in achievements:
                        if ach['id'] == "collect_first_item" and ach['id'] not in game_state['achievements']:
                            game_state['achievements'].append(ach['id'])
                            session['action_event'] = f"成就解锁：{ach['name']}"
                elif action == 'remove' and item in game_state['inventory']:
                    if game_state['inventory'][item] > quantity:
                        game_state['inventory'][item] -= quantity
                        item_messages.append(f"失去了 {item} x{quantity}")
                    else:
                        quantity_removed = game_state['inventory'][item]
                        del game_state['inventory'][item]
                        item_messages.append(f"失去了 {item} x{quantity_removed}")
    
    time_cost = choice.get('time', 0)
    current_time = datetime.strptime(game_state['stats']['time'], '%I:%M %p')
    new_time = current_time + timedelta(minutes=time_cost)
    game_state['stats']['time'] = new_time.strftime('%I:%M %p')
    
    if 'effect' in choice:
        for stat, value in choice['effect'].items():
            game_state['stats'][stat] = min(max(game_state['stats'][stat] + value, 0), 100)
    
    game_state['current_scene'] = choice['next']
    
    if game_state['current_scene'] not in game_state['visited']:
        game_state['visited'].append(game_state['current_scene'])
        # 检查访问场景的成就
        new_scene = get_scene(game_state['current_scene'])
        if 'achievements' in new_scene:
            for ach in new_scene['achievements']:
                if ach['condition'] == 'visit' and ach['id'] not in game_state['achievements']:
                    game_state['achievements'].append(ach['id'])
                    achievements = load_achievements()
                    for achievement in achievements:
                        if achievement['id'] == ach['id']:
                            session['action_event'] = f"成就解锁：{achievement['name']}"
                            break
    
    if action_event or item_messages:
        session['action_event'] = action_event or ""
        if item_messages:
            session['action_event'] = (action_event + " " if action_event else "") + "; ".join(item_messages)
    
    session['game_state'] = game_state
    return redirect(url_for('game'))

# 战斗页面
@app.route('/battle')
def battle():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session['game_state']
    if not game_state['battle']['enemy']:
        return redirect(url_for('game'))
    
    enemy = game_state['battle']['enemy']
    battle_log = game_state['battle']['battle_log']
    
    return render_template('battle.html',
                         game_state=game_state,
                         enemy=enemy,
                         battle_log=battle_log,
                         battle_choices=[{'text': '闪避', 'time': 5}],
                         stats=game_state['stats'],
                         inventory=game_state['inventory'],
                         equipment=game_state['equipment'],
                         character=game_state['character'],
                         event_message=session.pop('action_event', None),
                         debug_mode=DEBUG_MODE,
                         all_scene_ids=get_all_scene_ids())

# 处理战斗选择
@app.route('/battle_choose', methods=['POST'])
def battle_choose():
    game_state = session['game_state']
    choice_index = int(request.form['choice'])
    
    if choice_index == 0:  # 闪避
        # 重置战斗状态
        game_state['battle'].update({
            'dodge': True,
            'selected_skills': [],
            'defense': False,
            'persistent_damage': {'damage': 0, 'duration': 0},
            'buff': {'attack_boost': 0, 'duration': 0}
        })
        perform_battle_round()
        session['game_state'] = game_state
        return redirect(url_for('battle'))
    
    return redirect(url_for('battle'))

# 处理技能选择
@app.route('/select_skills', methods=['POST'])
def select_skills():
    game_state = session['game_state']
    selected_skills = request.form.getlist('skills')
    
    if len(selected_skills) <= 3:
        # 重置战斗状态
        game_state['battle'].update({
            'selected_skills': selected_skills,
            'dodge': False,
            'defense': False,
            'persistent_damage': {'damage': 0, 'duration': 0},
            'buff': {'attack_boost': 0, 'duration': 0}
        })
        perform_battle_round()
        session['game_state'] = game_state
    
    return redirect(url_for('battle'))

# 执行战斗回合
def perform_battle_round():
    game_state = session['game_state']
    enemy = game_state['battle']['enemy']
    player_stats = game_state['stats']
    battle_log = game_state['battle']['battle_log']
    
    # 应用持续伤害
    if game_state['battle']['persistent_damage']['duration'] > 0:
        damage = game_state['battle']['persistent_damage']['damage']
        enemy['health'] -= damage
        battle_log.append(f"{enemy['name']} 受到 {damage} 点持续伤害")
        game_state['battle']['persistent_damage']['duration'] -= 1
        if game_state['battle']['persistent_damage']['duration'] == 0:
            battle_log.append("持续伤害效果已结束！")
    
    # 敌人行动
    enemy_skill = random.choice(enemy['skills'])
    battle_log.append(f"{enemy['name']} 使用了 {enemy_skill['name']}！")
    
    if game_state['battle']['dodge']:
        dodge_chance = 0.5
        if random.random() < dodge_chance:
            battle_log.append("你成功闪避了敌人的攻击！")
        else:
            battle_log.append("闪避失败！")
            if game_state['battle']['defense']:
                battle_log.append("你的防御屏障抵挡了攻击！")
                game_state['battle']['defense'] = False
            else:
                apply_skill_effect(enemy_skill, player_stats)
    else:
        if game_state['battle']['defense']:
            battle_log.append("你的防御屏障抵挡了攻击！")
            game_state['battle']['defense'] = False
        else:
            apply_skill_effect(enemy_skill, player_stats)
    
    # 玩家行动
    if not game_state['battle']['dodge']:
        for skill_name in game_state['battle']['selected_skills']:
            skill = next((s for s in load_spells()['spells'] if s['name'] == skill_name), None)
            if skill:
                success_chance = calculate_success_chance(player_stats)
                if random.random() < success_chance:
                    battle_log.append(f"你成功释放了 {skill['name']}！")
                    apply_player_skill_effect(skill, enemy, game_state['grade'], battle_log)
                else:
                    battle_log.append(f"释放 {skill['name']} 失败！")
    
    # 更新增益效果
    if game_state['battle']['buff']['duration'] > 0:
        game_state['battle']['buff']['duration'] -= 1
        if game_state['battle']['buff']['duration'] == 0:
            battle_log.append("增益效果已结束！")
            game_state['battle']['buff']['attack_boost'] = 0
    
    # 检查战斗结束
    if player_stats['health'] <= 0:
        battle_log.append("你被击败了！")
        game_state['battle']['enemy'] = None
        game_state['current_scene'] = 'forbidden_forest'
    elif enemy['health'] <= 0:
        battle_log.append(f"你击败了 {enemy['name']}！")
        for reward in enemy['rewards']:
            if random.random() < reward['chance']:
                item = reward['item']
                quantity = reward['quantity']
                game_state['inventory'][item] = game_state['inventory'].get(item, 0) + quantity
                battle_log.append(f"获得了 {item} x{quantity}")
                # 检查获得物品的成就
                achievements = load_achievements()
                for ach in achievements:
                    if ach['id'] == "collect_first_item" and ach['id'] not in game_state['achievements']:
                        game_state['achievements'].append(ach['id'])
                        session['action_event'] = f"成就解锁：{ach['name']}"
        game_state['battle']['enemy'] = None
        game_state['current_scene'] = 'forbidden_forest'

def calculate_success_chance(player_stats):
    base_chance = 0.5
    san_bonus = player_stats['san'] / 100.0
    fatigue_penalty = player_stats['fatigue'] / 100.0
    return min(max(base_chance + san_bonus - fatigue_penalty, 0), 1)

def apply_skill_effect(skill, target_stats):
    for stat, value in skill['effect'].items():
        target_stats[stat] = min(max(target_stats[stat] + value, 0), 100)

def apply_player_skill_effect(skill, enemy, grade, battle_log):
    game_state = session['game_state']
    if skill.get('type') == 1:  # 伤害
        damage = skill['effect'].get('damage', 10)
        grade_bonus = grade * 0.05
        buff_bonus = game_state['battle']['buff']['attack_boost'] if game_state['battle']['buff']['duration'] > 0 else 0
        damage = int(damage * (1 + grade_bonus + buff_bonus))
        enemy['health'] -= damage
        battle_log.append(f"对 {enemy['name']} 造成了 {damage} 点伤害")
    elif skill.get('type') == 2:  # 防御
        game_state['battle']['defense'] = True
        battle_log.append("你抵挡了下一次攻击！")
    elif skill.get('type') == 3:  # 持续伤害
        damage = skill['effect'].get('damage', 5)
        duration = skill['effect'].get('duration', 3)
        game_state['battle']['persistent_damage'] = {'damage': damage, 'duration': duration}
        enemy['health'] -= damage
        battle_log.append(f"对 {enemy['name']} 造成了 {damage} 点持续伤害")
    elif skill.get('type') == 4:  # 增益
        boost = skill['effect'].get('attack_boost', 0.2)
        duration = skill['effect'].get('duration', 3)
        game_state['battle']['buff'] = {'attack_boost': boost, 'duration': duration}
        battle_log.append(f"你的攻击力增加了 {boost*100}%，持续 {duration} 回合！")

@app.route('/restore_stats', methods=['POST'])
def restore_stats():
    if not DEBUG_MODE:
        return jsonify({'message': '调试模式未启用'})
    game_state = session['game_state']
    game_state['stats']['health'] = 100
    game_state['stats']['san'] = 100
    game_state['stats']['fatigue'] = 0
    session['game_state'] = game_state
    return jsonify({'message': '状态已恢复！'})

@app.route('/talk_choose', methods=['POST'])
def talk_choose():
    game_state = session['game_state']
    if not game_state.get('current_talk') or not game_state.get('current_talk_node'):
        return redirect(url_for('game'))
    
    previous_state = copy.deepcopy(game_state)
    game_state['previous_state'] = previous_state
    
    choice_index = int(request.form['choice'])
    talk_data = get_talk(game_state['current_talk'])
    current_node = talk_data['dialogue'][game_state['current_talk_node']]
    
    choice_node = next((item for item in current_node if item.get('type') == 'choice'), None)
    if not choice_node or choice_index < 0 or choice_index >= len(choice_node['choices']):
        return redirect(url_for('game'))
    
    chosen_option = choice_node['choices'][choice_index]
    next_node = chosen_option['next']
    
    if 'effect' in chosen_option:
        for stat, value in chosen_option['effect'].items():
            game_state['stats'][stat] = min(max(game_state['stats'][stat] + value, 0), 100)
    
    if next_node == 'end' or talk_data['dialogue'].get(next_node, [{}])[0].get('type') == 'end':
        next_scene = talk_data['dialogue'].get(next_node, [{}])[0].get('next_scene', 'corridor')
        game_state['current_talk'] = None
        game_state['current_talk_node'] = None
        game_state['current_scene'] = next_scene
        session['game_state'] = game_state
        return redirect(url_for('game'))
    
    game_state['current_talk_node'] = next_node
    session['game_state'] = game_state
    return redirect(url_for('game'))

@app.route('/undo')
def undo_action():
    if 'game_state' not in session:
        return redirect(url_for('game'))
    
    game_state = session['game_state']
    previous_state = game_state.get('previous_state')
    
    if previous_state:
        session['game_state'] = previous_state
        session['game_state']['previous_state'] = None
        session['action_event'] = "已回退到上一步"
    
    return redirect(url_for('game'))

@app.route('/navigate/<scene_id>')
def navigate(scene_id):
    game_state = session['game_state']
    
    if DEBUG_MODE or (scene_id in game_state['unlocked_scenes']):
        game_state['current_talk'] = None
        game_state['current_talk_node'] = None
        game_state['current_scene'] = scene_id
        if scene_id not in game_state['visited']:
            game_state['visited'].append(scene_id)
            # 检查访问场景的成就
            new_scene = get_scene(scene_id)
            if 'achievements' in new_scene:
                for ach in new_scene['achievements']:
                    if ach['condition'] == 'visit' and ach['id'] not in game_state['achievements']:
                        game_state['achievements'].append(ach['id'])
                        achievements = load_achievements()
                        for achievement in achievements:
                            if achievement['id'] == ach['id']:
                                session['action_event'] = f"成就解锁：{achievement['name']}"
                                break
        session['game_state'] = game_state
    
    return redirect(url_for('game'))

@app.route('/scene_container/<container_id>')
def scene_container(container_id):
    game_state = session['game_state']
    if container_id == 'inventory':
        return jsonify({
            'inventory': game_state['inventory'],
            'inventory_length': count_items(game_state['inventory'])
        })
    else:
        if container_id not in game_state['containers']:
            game_state['containers'][container_id] = {}
            session['game_state'] = game_state
        return jsonify({
            'items': game_state['containers'][container_id],
            'inventory': game_state['inventory'],
            'inventory_length': count_items(game_state['inventory']),
            'container_exists': True
        })

@app.route('/item_action', methods=['POST'])
def item_action():
    item_effects = load_item_effects()
    game_state = session['game_state']
    action = request.form['action']
    item = request.form['item']
    container = request.form.get('container', '')
    event_message = None
    game_state['last_action'] = None
    
    game_state['previous_item_state'] = {
        'inventory': copy.deepcopy(game_state['inventory']),
        'containers': copy.deepcopy(game_state['containers']),
        'equipment': copy.deepcopy(game_state['equipment']),
        'stats': copy.deepcopy(game_state['stats'])
    }
    
    if container and container not in game_state['containers']:
        game_state['containers'][container] = {}
    
    if action == 'move_to_container' and container in game_state['containers']:
        if item in game_state['inventory'] and count_items(game_state['containers'][container]) < 15:
            quantity = 1
            game_state['inventory'][item] -= quantity
            game_state['containers'][container][item] = game_state['containers'][container].get(item, 0) + quantity
            if game_state['inventory'][item] == 0:
                del game_state['inventory'][item]
            event_message = f'已将 {item} 放入 {container}'
            game_state['last_action'] = {'action': 'move_to_container', 'item': item, 'quantity': quantity, 'container': container}
    
    elif action == 'move_to_inventory' and container in game_state['containers']:
        if item in game_state['containers'][container] and count_items(game_state['inventory']) < 10:
            quantity = 1
            game_state['containers'][container][item] -= quantity
            game_state['inventory'][item] = game_state['inventory'].get(item, 0) + quantity
            if game_state['containers'][container][item] == 0:
                del game_state['containers'][container][item]
            event_message = f'已从 {container} 取出 {item}'
    
    elif action == 'discard':
        if item in game_state['inventory']:
            quantity = 1
            game_state['inventory'][item] -= quantity
            if game_state['inventory'][item] == 0:
                del game_state['inventory'][item]
            event_message = f'已丢弃 {item}'
            game_state['last_action'] = {'action': 'discard', 'item': item, 'quantity': quantity, 'container': None}
    
    elif action == 'use':
        if item in item_effects:
            item_type = item_effects[item]['type']
            if item_type == 'consumable':
                for stat, value in item_effects[item]['effect'].items():
                    game_state['stats'][stat] = min(max(game_state['stats'][stat] + value, 0), 100)
                event_message = item_effects[item]['message']
                if item in game_state['inventory']:
                    game_state['inventory'][item] -= 1
                    if game_state['inventory'][item] == 0:
                        del game_state['inventory'][item]
    
    session['game_state'] = game_state
    return jsonify({
        'inventory': game_state['inventory'],
        'container_items': game_state['containers'].get(container, {}) if container else {},
        'event_message': event_message,
        'stats': game_state['stats'],
        'equipment': game_state['equipment'],
        'last_action': game_state['last_action'],
        'can_undo': True
    })

@app.route('/undo_item_action', methods=['POST'])
def undo_item_action():
    game_state = session['game_state']
    event_message = None
    
    if 'previous_item_state' in game_state:
        prev_state = game_state['previous_item_state']
        game_state['inventory'] = prev_state['inventory']
        game_state['containers'] = prev_state['containers']
        game_state['equipment'] = prev_state['equipment']
        game_state['stats'] = prev_state['stats']
        game_state.pop('previous_item_state', None)
        event_message = '已撤销上一次物品操作'
    
    session['game_state'] = game_state
    return jsonify({
        'inventory': game_state['inventory'],
        'container_items': {},
        'event_message': event_message,
        'stats': game_state['stats'],
        'equipment': game_state['equipment'],
        'last_action': None,
        'can_undo': False
    })

@app.route('/get_spells')
def get_spells():
    game_state = session['game_state']
    spells = load_spells()['spells']
    known_spells = []
    
    for spell in spells:
        if spell['name'] in game_state['known_spells']:
            known_spells.append({
                'name': spell['name'],
                'description': spell.get('description', '无描述')
            })
    
    return jsonify({'spells': known_spells})

@app.route('/gain_all_spells', methods=['POST'])
def gain_all_spells():
    if not DEBUG_MODE:
        return jsonify({'message': '调试模式未启用'})
    
    game_state = session['game_state']
    spells = load_spells()['spells']
    
    game_state['known_spells'] = [spell['name'] for spell in spells]
    # 检查学会咒语的成就
    achievements = load_achievements()
    for ach in achievements:
        if ach['id'] == "learn_first_spell" and ach['id'] not in game_state['achievements']:
            game_state['achievements'].append(ach['id'])
            session['action_event'] = f"成就解锁：{ach['name']}"
    
    session['game_state'] = game_state
    return jsonify({'message': '已获得所有咒语！'})

@app.route('/get_achievements')
def get_achievements():
    game_state = session['game_state']
    achievements = load_achievements()
    unlocked_achievements = [ach for ach in achievements if ach['id'] in game_state['achievements']]
    return jsonify({'achievements': unlocked_achievements})

@app.route('/reload_scenes')
def reload_scenes():
    if DEBUG_MODE:
        load_scenes()
        return "场景重新加载成功！"
    return "调试模式未启用"

if __name__ == '__main__':
    app.run(debug=True)