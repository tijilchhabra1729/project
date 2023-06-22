import json

def calculator(qid, data, time):

    f = open('questions.json')
    g = open('metadata.json')
    s = json.load(f)
    t = json.load(g)

    total_per_time = data

    for i in s['questions']:
        if i['ques_id'] == qid:
            plastic_type = i['plastic_type']
            wt_per_cnt = i['wt_per_cnt']

    for i in t['emission']:
        if i['type_id'] == plastic_type:
            emission_factor = i['factor']

    if time == 'w':
        total_per_time *= 52
    elif time == 'm':
        total_per_time *= 12
    elif time == 'd':
        total_per_time *= 365
    elif time == 'q':
        total_per_time *= 4

    total_weight = (total_per_time * wt_per_cnt) / 1000

    emission = total_weight * emission_factor

    f.close()
    g.close()

    return (total_weight, emission)
    

