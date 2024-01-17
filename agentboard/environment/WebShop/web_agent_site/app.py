import argparse, json, logging, random
from pathlib import Path
from ast import literal_eval
import sys
import itertools
import os
from dotenv import load_dotenv
from flask import (
    Flask,
    request,
    redirect,
    url_for,
    session
)

from web_agent_site.engine.engine import (
    load_products,
    init_search_engine,
    convert_web_app_string_to_var,
    get_top_n_product_from_keywords,
    get_product_per_page,
    map_action_to_html,
    END_BUTTON
)
from web_agent_site.engine.goal import get_reward, get_goals
from web_agent_site.utils import (
    generate_mturk_code,
    DEFAULT_FILE_PATH,
    DEBUG_PROD_SIZE,
)
app = Flask(__name__)

search_engine = None
all_products = None
product_item_dict = None
product_prices = None
attribute_to_asins = None
goals = None
weights = None
global sub_reward
sub_reward =[]
global s_s
global i_s
global b_s
s_s = [0.0]
i_s = [0.0]
b_s = [0.0]


user_sessions = dict()
user_log_dir = None
subreward_log_dir = None
SHOW_ATTRS_TAB = False


@app.route('/')
def home():
    return redirect(url_for('index', session_id="abc"))

@app.route('/<session_id>', methods=['GET', 'POST'])
def index(session_id):
    global user_log_dir
    global subreward_log_dir
    global all_products, product_item_dict, \
           product_prices, attribute_to_asins, \
           search_engine, \
           goals, weights, user_sessions

    if search_engine is None:
        all_products, product_item_dict, product_prices, attribute_to_asins = \
            load_products(
                filepath=DEFAULT_FILE_PATH,
                num_products=DEBUG_PROD_SIZE
            )
        search_engine = init_search_engine(num_products=DEBUG_PROD_SIZE)
        goals = get_goals(all_products, product_prices)
        weights = [goal['weight'] for goal in goals]
    if session_id not in user_sessions and 'fixed' in session_id:
        goal_dix = int(session_id.split('_')[-1])
        goal = goals[goal_dix]
        instruction_text = goal['instruction_text']
        user_sessions[session_id] = {'goal': goal, 'done': False}
    elif session_id not in user_sessions:
        goal = random.choices(goals, weights)[0]
        instruction_text = goal['instruction_text']
        user_sessions[session_id] = {'goal': goal, 'done': False}
    else:
        instruction_text = user_sessions[session_id]['goal']['instruction_text']

    if request.method == 'POST' and 'search_query' in request.form:
        keywords = request.form['search_query'].lower().split(' ')
        return redirect(url_for(
            'search_results',
            session_id=session_id,
            keywords=keywords,
            page=1,
        ))


    if request.method == 'GET':
        sub_reward.append(s_s[0]/3.0 + i_s[0]/3.0 + b_s[0]/3.0)  # each part weight is 1/3


    return map_action_to_html(
        'start',
        session_id=session_id,
        instruction_text=instruction_text,
        progress_reward=sub_reward[-1]
    )


@app.route(
    '/search_results/<session_id>/<keywords>/<page>',
    methods=['GET', 'POST']
)
def search_results(session_id, keywords, page):
    instruction_text = user_sessions[session_id]['goal']['instruction_text']
    page = convert_web_app_string_to_var('page', page)
    keywords = convert_web_app_string_to_var('keywords', keywords)
    top_n_products = get_top_n_product_from_keywords(
        keywords,
        search_engine,
        all_products,
        product_item_dict,
        attribute_to_asins,
    )
    # Get product list from search result asins and get list of corresponding URLs
    products = get_product_per_page(top_n_products, page)

    if request.method == 'GET':
        # calculate sub-reward (search recall reward)
        goal = user_sessions[session_id]['goal']
        search_max = 0.0
        maxr = False
        for i in range(len(products)):
            product_r = []
            single_product = products[i]
            all_options = list(single_product['options'].values())
            all_combinations = list(itertools.product(*all_options))
            if len(all_combinations) > 0:
                for c in all_combinations:
                    single_product_asin = single_product['asin']
                    price = product_prices[single_product_asin]
                    reward, _ = get_reward(single_product, goal, price, dict(enumerate(c)),
                                           verbose=True)
                    product_r.append(reward)
                    if reward > search_max:
                        search_max = reward
                    if reward == 1.0:
                        maxr = True
                        search_max = reward

            else:
                price = single_product['pricing'][0]
                reward, _ = get_reward(single_product, goal, price, [], verbose=True)
                if reward == 1.0:
                    maxr = True
                if reward > search_max:
                    search_max = reward
        if search_max > s_s[0]:
            s_s.pop(0)
            s_s.append(search_max)
        sub_reward.append(s_s[0]/3.0 + i_s[0]/3.0 + b_s[0]/3.0)  # each part weight is 1/3



    html = map_action_to_html(
        'search',
        session_id=session_id,
        products=products,
        keywords=keywords,
        page=page,
        total=15,
        instruction_text=instruction_text,
        progress_reward=sub_reward[-1]
    )
    return html


@app.route(
    '/item_page/<session_id>/<asin>/<keywords>/<page>/<options>',
    methods=['GET', 'POST']
)
def item_page(session_id, asin, keywords, page, options):
    options = literal_eval(options)
    product_info = product_item_dict[asin]
    goal_instruction = user_sessions[session_id]['goal']['instruction_text']
    product_info['goal_instruction'] = goal_instruction

    if request.method == 'GET':
        # calculate sub-reward (item page score)
        goal = user_sessions[session_id]['goal']
        single_product = product_info
        all_options = list(single_product['options'].values())
        # generate all possible combinations of options
        all_combinations = list(itertools.product(*all_options))
        if len(all_combinations) > 0:
            for c in all_combinations:
                maxr = -1  # whether contains goal item in item page
                price = product_prices[asin]
                reward, _ = get_reward(single_product, goal, price, dict(enumerate(c)),
                                       verbose=True)
                if reward > maxr:
                    maxr = reward
                    if reward == 1.0:
                        break
        else:
            price = single_product['pricing'][0]
            reward, _ = get_reward(single_product, goal, price, [], verbose=True)
            maxr = reward

        if maxr > i_s[0]:
            i_s.pop(0)
            i_s.append(maxr)
        sub_reward.append(s_s[0]/3.0 + i_s[0]/3.0 + b_s[0]/3.0)  # each part weight is 1/3


    html = map_action_to_html(
        'click',
        session_id=session_id,
        product_info=product_info,
        keywords=keywords,
        page=page,
        asin=asin,
        options=options,
        instruction_text=goal_instruction,
        show_attrs=SHOW_ATTRS_TAB,
        progress_reward=sub_reward[-1]
    )
    return html


@app.route(
    '/item_sub_page/<session_id>/<asin>/<keywords>/<page>/<sub_page>/<options>',
    methods=['GET', 'POST']
)
def item_sub_page(session_id, asin, keywords, page, sub_page, options):
    options = literal_eval(options)
    product_info = product_item_dict[asin]

    goal_instruction = user_sessions[session_id]['goal']['instruction_text']
    product_info['goal_instruction'] = goal_instruction

    if request.method == 'GET':
        # calculate sub-reward (item page score)
        goal = user_sessions[session_id]['goal']
        single_product = product_info
        all_options = list(single_product['options'].values())
        # generate all possible combinations of options
        all_combinations = list(itertools.product(*all_options))
        if len(all_combinations) > 0:
            for c in all_combinations:
                maxr = -1  # whether contains goal item in item page
                price = product_prices[asin]
                reward, _ = get_reward(single_product, goal, price, dict(enumerate(c)),
                                       verbose=True)
                if reward > maxr:
                    maxr = reward
                    if reward == 1.0:
                        break
        else:
            price = single_product['pricing'][0]
            reward, _ = get_reward(single_product, goal, price, [], verbose=True)
            maxr = reward


        if maxr > i_s[0]:
            i_s.pop(0)
            i_s.append(maxr)
        sub_reward.append(s_s[0]/3.0 + i_s[0]/3.0 + b_s[0]/3.0)  # each part weight is 1/3


    html = map_action_to_html(
        f'click[{sub_page}]',
        session_id=session_id,
        product_info=product_info,
        keywords=keywords,
        page=page,
        asin=asin,
        options=options,
        instruction_text=goal_instruction,
        progress_reward=sub_reward[-1]
    )
    return html


@app.route('/done/<session_id>/<asin>/<options>', methods=['GET', 'POST'])
def done(session_id, asin, options):
    options = literal_eval(options)
    goal = user_sessions[session_id]['goal']
    purchased_product = product_item_dict[asin]
    price = product_prices[asin]

    reward, reward_info = get_reward(
        purchased_product,
        goal,
        price=price,
        options=options,
        verbose=True
    )
    user_sessions[session_id]['done'] = True
    user_sessions[session_id]['reward'] = reward

    b_s.pop(0)
    b_s.append(reward)
    sub_reward.append(s_s[0]/3.0 + i_s[0]/3.0 + b_s[0]/3.0)  # each part weight is 1/3
    last_sub_reward = sub_reward[-1]
    del sub_reward[:]
    del s_s[:]
    s_s.append(0.0)
    del i_s[:]
    i_s.append(0.0)
    del b_s[:]
    b_s.append(0.0)


    return map_action_to_html(
        f'click[{END_BUTTON}]',
        session_id=session_id,
        reward=reward,
        asin=asin,
        options=options,
        reward_info=reward_info,
        query=purchased_product['query'],
        category=purchased_product['category'],
        product_category=purchased_product['product_category'],
        goal_attrs=user_sessions[session_id]['goal']['attributes'],
        purchased_attrs=purchased_product['Attributes'],
        goal=goal,
        mturk_code=generate_mturk_code(session_id),
        progress_reward=last_sub_reward
    )

@app.route('/failed', methods=['HEAD'])
def failed():
    b_s.pop(0)
    b_s.append(0.0)
    sub_reward.append(s_s[0] / 3.0 + i_s[0] / 3.0 + b_s[0] / 3.0)  # each part weight is 1/3
    del sub_reward[0:]
    del s_s[:]
    s_s.append(0.0)
    del i_s[:]
    i_s.append(0.0)
    del b_s[:]
    b_s.append(0.0)
    return ''


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebShop flask app backend configuration")
    parser.add_argument("--log", action='store_true', help="Log actions on WebShop in trajectory file")
    parser.add_argument("--attrs", action='store_true', help="Show attributes tab in item page")

    args = parser.parse_args()
    if args.log:
        subreward_log_dir = Path('subreward_log')
        subreward_log_dir.mkdir(parents=True, exist_ok=True)
    SHOW_ATTRS_TAB = args.attrs

    app.run(host='0.0.0.0', port=3000)

