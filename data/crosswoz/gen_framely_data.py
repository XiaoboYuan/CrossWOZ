import json
import os
from collections import defaultdict
from random import choice

schema = {
    "景点": {
        "名称": "name",
        "地址": "location",
        "地铁": "metro",
        "电话": "phone",
        "门票": "ticketPrice",
        "游玩时间": "travellingHours",
        "评分": "rate",
        "周边景点": "nearbyScenes",
        "周边餐馆": "nearbyRestaurants",
        "周边酒店": "nearbyHotels",
    },
    "餐馆": {
        "名称": "name",
        "地址": "location",
        "地铁": "metro",
        "电话": "phone",
        "营业时间": "businessHours",
        "推荐菜": "travellingHours",
        "人均消费": "price",
        "评分": "rate",
        "周边景点": "nearbyScenes",
        "周边餐馆": "nearbyRestaurants",
        "周边酒店": "nearbyHotels",
    },
    "酒店": {
        "名称": "name",
        "地址": "location",
        "地铁": "metro",
        "电话": "phone",
        "酒店类型": "businessHours",
        "酒店设施": "travellingHours",
        "价格": "price",
        "评分": "rate",
        "周边景点": "nearbyScenes",
        "周边餐馆": "nearbyRestaurants",
        "周边酒店": "nearbyHotels",
    },
    "地铁": {
        "名称": "name",
        "地铁": "metro",
    },
    "出租": {
        "出发地": "location",
        "目的地": "location",
        "车型": "type",
        "车牌": "plate",
    },
}


def gen_tagged_contents(data_set_name):
    with open('%s.json' % data_set_name) as f:
        result = json.load(f)
    tagged_contents = []
    for taskId, item in result.items():
        for m in item['messages']:
            intent_tags = []
            slot_tags = []
            content = m['content']
            for d in m['dialog_act']:
                if d[0] == 'Request':
                    intent_tags.append(('%s%s' % (d[1], d[2])).replace('-', ''))
                elif d[0] == 'Inform' and d[3] != '否':
                    start_index = content.find(d[3])
                    if start_index < 0:
                        continue
                    slot_tags.append({'name': ('%s%s' % (d[1], d[2])).replace('-', ''), 'range': [start_index, start_index + len(d[3])]})
            if len(intent_tags) > 0 or len(slot_tags) > 0:
                tagged_contents.append({'content': content, 'intents': intent_tags, 'slots': slot_tags})
    return tagged_contents


def get_names(tagged_contents):
    intents = {}
    slots = {}
    for c in tagged_contents:
        for i in c['intents']:
            intents[i] = True
        for s in c['slots']:
            slots[s['name']] = True
    return {'intents': intents, 'slots': slots}


def replace_range_with_slot_name(original, slot_tags):
    slot_tags.sort(key=lambda x: x['range'][0])
    current = 0
    parts = []
    for t in slot_tags:
        parts.append(original[current: t['range'][0]])
        parts.append('<%s>' % t['name'])
        current = t['range'][1]
    if current < len(original):
        parts.append(original[current:])
    revised = ''.join(parts)
    return revised


def gen_intent_samples(tagged_contents):
    intent_map = defaultdict(list)
    for c in tagged_contents:
        intent_tags = c['intents']
        if len(intent_tags) == 0:
            continue
        slot_tags = c['slots']
        revised_content = replace_range_with_slot_name(c['content'], slot_tags)
        for intent in intent_tags:
            intent_map[intent].append(revised_content)

    return intent_map


def gen_slot_samples(tagged_contents):
    res = []
    all_slots = list(get_names(tagged_contents)['slots'].keys())
    for c in tagged_contents:
        slot_tags = c['slots']
        slot_set = set(map(lambda x: x['name'], slot_tags))
        for t in slot_tags:
            res.append({'content': c['content'], 'slot': t['name'], 'range': t['range']})
            other_slot = ""
            for i in range(0, 5):
                rs = choice(all_slots)
                if rs not in slot_set:
                    other_slot = rs
                    break
            if other_slot != '':
                res.append({'content': c['content'], 'slot': other_slot, 'range': [0, 0]})
    return res


def write_intent_samples(data_set_name):
    contents = gen_tagged_contents(data_set_name)
    intent_map = gen_intent_samples(contents)
    for k in intent_map:
        print("====================")
        print(k)
        for i in intent_map[k]:
            print(i)

    with open('intents.%s' % data_set_name, 'a') as f:
        for k in intent_map:
            contents = intent_map[k]
            res_list = []
            for i, c in enumerate(contents):
                for j, o in enumerate(contents[i + 1:]):
                    res_list.append({'label': '1', 'first': c, 'second': o})
            for r in res_list:
                f.write('%s\t%s\t%s\t%s' % ('旅行', r['label'], r['first'], r['second']))
                f.write(os.linesep)
            size = len(res_list)
            res_list = []
            for i in range(0, size):
                first = choice(contents)
                for j in range(0, 5):
                    second_intent = choice(list(intent_map.keys()))
                    if first not in intent_map[second_intent]:
                        second = choice(intent_map[second_intent])
                        res_list.append({'label': '0', 'first': first, 'second': second})
                        break
            for r in res_list:
                f.write('%s\t%s\t%s\t%s' % ('旅行', r['label'], r['first'], r['second']))
                f.write(os.linesep)


def write_slot_samples(data_set_name):
    contents = gen_tagged_contents(data_set_name)
    slot_samples = gen_slot_samples(contents)
    lines = []
    for s in slot_samples:
        line = '%s\t%s\t%s?\t%s\t%s' % ('旅行', s['content'], s['slot'], '0' if s['range'][1] == 0 else '1', ', '.join([str(x) for x in s['range']]))
        lines.append(line)
    with open('slots.%s' % data_set_name, 'w') as f:
        f.writelines(os.linesep.join(lines))


if __name__ == '__main__':
    write_intent_samples('train')


