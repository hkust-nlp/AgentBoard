import gym
from jericho import *
import subprocess
import os
import re
import random
from environment.base_env import BaseEnvironment
from common.registry import registry

@registry.register_environment("jericho")
class Jericho(BaseEnvironment):
    def __init__(self, game_file=None, 
                 game_name="905",
                 game_config=None, # no seed for this environment, as it is deterministic
                 obs_to_reward=None,
                 difficulty=None,
                 ):
        
        super().__init__()
        self.game_file = game_file
        self.game_name = game_name
        self.game_config = game_config
        self.difficulty = difficulty
        
        if not os.path.exists(self.game_file):
            raise ValueError(f"Game file {self.game_file} does not exist.")
        
        self.env = FrotzEnv(game_file)
        self.store_all_obs_to_reward = obs_to_reward
        self.obs_to_reward = obs_to_reward
        if self.obs_to_reward is not None:
            self.num_obs_to_reward = len(self.obs_to_reward)
        self.reset()
        
        
        
    
    def _get_info(self):
        return self.infos
    
    def _get_obs(self):
        return self.states[-1]
    
    def _get_goal(self):
        return self.goal
    
    def _get_history(self):
        return self.history
    
    def _get_action_space(self):
        # golden_actions = self.env.get_walkthrough()
        # for i in range(len(golden_actions)):
        #     if golden_actions[i] == "s":
        #         golden_actions[i] = "south"
        #     elif golden_actions[i] == "n":
        #         golden_actions[i] = "north"
        #     elif golden_actions[i] == "e":
        #         golden_actions[i] = "east"
        #     elif golden_actions[i] == "w":
        #         golden_actions[i] = "west"
        #     elif golden_actions[i] == "u":
        #         golden_actions[i] = "up"
        #     elif golden_actions[i] == "d":
        #         golden_actions[i] = "down"
        #     elif golden_actions[i] == "ne":
        #         golden_actions[i] = "northeast"
        #     elif golden_actions[i] == "se":
        #         golden_actions[i] = "southeast"
        #     elif golden_actions[i] == "nw":
        #         golden_actions[i] = "northwest"
        #     elif golden_actions[i] == "sw":
        #         golden_actions[i] = "southwest"
        
        #     elif 'x' in golden_actions[i]:
        #         golden_actions.replace('x', 'examine')
                
        # golden_actions = list(set(golden_actions))
        # valid_actions = self.env.get_valid_actions()
        
        # valid_actions_only = [action for action in valid_actions if action not in golden_actions]
        # valid_actions_only = random.sample(valid_actions_only, min(3, len(valid_actions_only)))
        
        # return  golden_actions + valid_actions_only + ["check valid actions"] # return a list of valid actions
        return self.env.get_valid_actions() + ["check valid actions"]
    
    def is_done(self):
        return self.done
    
    def match_style(self, obs, pattern):
        # remove all non-alphanumeric characters, but keep spaces
        obs = re.sub(r'[^a-zA-Z0-9\s]', '', obs)
        pattern = re.sub(r'[^a-zA-Z0-9\s]', '', pattern)
        if pattern in obs:
            return True
        else:
            return False
    
    def update_reward(self, obs):
        if self.obs_to_reward is None:
            return
        if len(self.obs_to_reward) == 0:
            return
        
        for pattern in self.obs_to_reward:
            if self.match_style(obs, pattern):
                self.points += 1
                self.reward = max(self.reward, self.points/self.num_obs_to_reward)
                self.obs_to_reward.remove(pattern)
                break
    
    def update(self, action, obs, reward, done, info): # update the environment after taking an action
        # for k, v in infos.items():
        #     self.infos[k] = v
        # nothing useful in info for jericho
        
        if self.obs_to_reward is not None:
            self.update_reward(obs)
            self.done = (self.reward == 1) | done 
            self.won = (self.reward == 1)
        else:
            self.reward = reward
            self.done = done
            self.won = done
            
        self.history.append(("action", action))
        self.history.append(("reward", reward))
        self.history.append(("state", obs))
        self.states.append(obs)
        
        self.steps += 1
        
        self.infos["goal"] = self.goal
        self.infos["states"] = self.states
        self.infos["history"] = self.history
        self.infos["steps"] = self.steps
        self.infos["state"] = self.states[-1]
    
    def update_info(self, action, info):
        self.history.append(("action", action))
        self.history.append(("reward", self.reward))
        self.history.append(("state", info))
        self.states.append(info)
        
        self.steps += 1
        self.infos["goal"] = self.goal
        self.infos["states"] = self.states
        self.infos["history"] = self.history
        self.infos["steps"] = self.steps
        self.infos["state"] = self.states[-1]
    
    def reset(self):
        if self.store_all_obs_to_reward is not None:
            self.obs_to_reward = self.store_all_obs_to_reward.copy()
        else:
            self.obs_to_reward = None
        obs, infos = self.env.reset() 
        self.goal = self.game_config["goal"] # currently only support handwritten goal
        self.init_obs = self.game_config["init_obs"] # initial observation, remove format not needed
        self.infos = dict() # record last step info
        self.states = [self.init_obs]  # record a stream of states
        self.history = [("state", self.init_obs)] # record a stream of s0, a0, r0, s1, a1, r1, ...
        self.steps = 0
        
        self.infos["goal"] = self.goal
        self.infos["states"] = self.states
        self.infos["history"] = self.history
        self.infos["steps"] = self.steps
        self.infos["state"] = self.states[-1]
        
        self.reward = 0
        self.points = 0
        self.done = False
        self.won = False
    
    def validate_check_valid_actions(self, action):
        action = action.strip().lower()
        if "check" in action and "action" in action:
            return True
        else:
            return False
        
    def step(self, action):
        if self.validate_check_valid_actions(action): # add a special action to check valid actions
            obs = "You can take the following actions: " + ", ".join(self._get_action_space())
            self.update_info(action, obs) 
            self.infos["action_is_valid"] = True
            return self._get_obs(), self.reward, self.done, self.infos
        else:
            observation, reward, done, info = self.env.step(action)
            observation = self.clean_up_text(observation)
            self.update(action, observation, reward, done, info)
            if '[!' in observation:
                self.infos["action_is_valid"] = False
            else:
                self.infos["action_is_valid"] = True
            return self._get_obs(), self.reward, self.done, self.infos
    
    def clean_up_text(self, observation):
        cleaned_text = re.sub(r'\n', ' ', observation)
        cleaned_text = re.sub(r' {2,}', ' ', cleaned_text) 
        cleaned_text = re.sub(r'\[Your score .*?\]', '', cleaned_text)  
        return cleaned_text
    
    def get_init_obs(self, init_obs): # this step needs case specific checking for each game
        text =  re.sub(r'-----([\s\S]*?)-----', '', init_obs)  # remove the copyright line
  
        # Remove all \n   
        text = re.sub(r'\n', ' ', text)
        
        # Remove more than one space  
        text = re.sub(r' {2,}', ' ', text)  

        return text
    
    @classmethod
    def from_config(cls, cfg):
        game_file = cfg.get("game_file")
        game_config = dict()
        game_name = cfg.get("game_name", "905") # The name of the game: tw-simple, tw-cooking, tw-treasure_hunter, tw-coin_collector
        obs_to_reward= cfg.get("obs_to_reward", None)
        difficulty = cfg.get("difficulty", None)
        # if game_name not in solution_lengths or game_name not in game_goals:
        #     raise ValueError(f"Game {game_name} is not supported, as it's solution is over 60 steps.")
        # quest_length = solution_lengths[game_name] 
        
        if game_name not in game_goals:
            quest_goal = "Not written yet."
        else:
            quest_goal = game_goals[game_name]
            
        if game_name not in game_init_obs:
            quest_init_obs = "Not written yet."
        else:
            quest_init_obs = game_init_obs[game_name]
        # game_config["quest_length"] = quest_length
        game_config["goal"] = quest_goal
        game_config["init_obs"] = quest_init_obs
        env = cls(game_file=game_file, 
                   game_name=game_name,
                   game_config=game_config,
                   obs_to_reward=obs_to_reward,
                   difficulty=difficulty,
                   )
        return env


# only include games with less than 60 steps
solution_lengths = {
    "detective": 51,
    "library": 52,
    "pentari": 34,
    "loose": 51,
    "awaken": 57,
    "snacktime": 34,
    "905": 22,
    "moonlit": 59,
    "partyfoul": 56,
}

game_goals = {
    "detective": "Search for the culprit around town. He is rumored to be staying at holiday inn. Beware of suspicious people and get a weapon and use it.",
    "905": "Get out of the house. Then escape the city without getting caught via driving.",
    "acorncourt": "You need to unlock and open the gate. The key to the gate is in a stone well. You can use a broken bucket to get the key in the well.",
    "afflicted": "Find your way into Nikolai’s restaurant and find him without being caught.",
    "balances":"You are in a magical world where you can learn spells from spell books. Try to learn rezrov spell, lleps spell, and bozbar spell. Note that books or scrolls containing these spells may be hidden in furniture or oats or boxes. You need to use these spells to find all spell books. Note that when you use a spell, the format is: cast spell <spell name> on <obj name>, e.g. cast spell reznov on door",
    "dragon":"search for a mug in an inn. ",
    "jewel": "Get to the Fifth Layer Dropoff area. You can try to get a pathway upward by pulling quartz out of mineral cave ceiling.",
    "library":"Find a book on Graham Nelson in the library.",
    "omniquest": "You are a treasure hunter who wants to seek out a mysterious cylindrical room under a rock on an island, remember to use a tool to help you breathe when you swim in the ocean.",
    "reverb":"You are a pizza delivery man. Today you are making a new delivery on your boss’s order. You need to find out by yourself who to deliver.",
    "snacktime": "You are a bulldog and your pet is sleeping by you in the room. You need to wake him and feed him.",
    "zenon": "You are prisoner on ship Zenon, locked in your cell. You need to get out of your cell out into the corridor without getting caught. You could use a distraction.",
    "zork1": "You need to find your way into a secret passage where the entrance is in the living room of the house.",
    "zork2": "You are an explorer in the underground world. Your quest is to find a unicorn in the underground maze. You will be needing light to avoid being eaten by Grue in the darkness.",
    "zork3": "You need to find your way into a secret passage. Your best chance is to bribe the old gatekeeper at Engravings room with some bread. You need to search for bread somewhere.",
    "night": "You are a student at a university who needs to find the missing printer. It is rumored to be in a secret panel in the university that is dark and secret. The entrance to the panel is hidden and you should follow the buzzing of the printer . Also, you need to get the flashlight hidden in a box near the elevator first.",
    "pentari": "You are treasure hunting in your company, when you are suddenly transported to a fantasy world. In this world you must be seeking for a jewel encrusted dagger. Remember to hide from dark elf, as he could easily kill you. You should look for the dagger in the armory room.",
    "weapon": "You are trying to yield weapon Yi-Lono-Mordel. However, first you need to power it up. You need to successfully activate the power stud, though you need to recalibrate the contacts first.",
    "darkhunt": "You are a hunter and you need to hunt for a wumpus.",
    "loose": "You are a brave explorer who helps people on the way. Try to find a lost golden hairpin somewhere and return it to a girl called Mary. Note that the hairpin is hidden in a pot."
}


game_init_obs = {
    "905": "The phone rings. Oh, no - how long have you been asleep? Sure, it was a tough night, but... This is bad. This is very bad. Bedroom (in bed) - This bedroom is extremely spare, with dirty laundry scattered haphazardly all over the floor. Cleaner clothing can be found in the dresser. A bathroom lies to the south, while a door to the east leads to the living room. On the end table are a telephone, a wallet and some keys. The phone rings.",
    "acorncourt": "GREAT.  THEY'VE DONE IT TO ME AGAIN.  You think to yourself. THEY'VE STUCK ME IN ANOTHER ONE OF THEIR SILLY SCENARIOS.  You glance about with a look of irritation on your face.  WELL, I'LL SHOW THEM.  I'LL MAKE SHORT WORK OF THEIR STUPID LITTLE PUZZLE...Court Yard - A good sized courtyard with an air of late British colonialism about it.  To the west, in the direction the sun is setting, is a high, grey stone wall with an ornate iron gate set into the rock.  The walls of a large stone mansion rise several stories into the chilly evening air to the east, north, and south.  In the east wall, two or three stories up, is a large window.  On top of the west wall, above and to the right of the gate, is a large squirrels nest made of sticks, twigs, and leaves. Carpeting of old brown leaves from past winters rustle about on the ground in the breeze and drift listlessly across a cracked, stained, pale green tennis court with a rotting net.  In one corner of the court yard an impressively large oak tree casts long shadows in the dimming light.  The acorns nestled among the tree's massive branches and vividly healthy leaves are new and green.  Near the tree is a quaint looking well of crumbling stone. A rusty tin pail rests in the grass near the ball machine. The tennis ball launching machine sitting in one corner of the yard looks like a relic from the 1930s.",
    "afflicted": "This has never been your favorite part of the city. Nor is this neighborhood the safest one. But as a city sanitarian, you are charged with completing an annual health and safety inspection of every restaurant in your district. Each day you visit three or four restaurants. During those visits you take note of potential health code violations in your trusty notepad. Today\'s first target: Nikolai\'s Bar and Grill. A hazy sun barely peeks above the three-story tenements. 19th Street You are standing in front of Nikolai\'s Bar and Grill on 19th Street. A green awning shades the smudged window into Nikolai\'s dining room. The front entrance is north of you. The east/west sidewalk here is cracked and uneven, pocked by clumps of crabgrass. A storm gutter is built into the curb, littered with broken bottles. Across the street a neon sign flickers erratically. A few cars are parked nearby (including yours), but otherwise you see no evidence that anyone visits this neighborhood past daybreak. An aluminum placard is fixed to the front door. A damp sheet of newspaper has blown up against the curb.",
    "balances": "[How do spells work] You feel a little confused as to how you got here. Something to do with Helistar! That\'s right, and how the world is so far off balance nowadays, after the Great Change. Until quite recently, someone lived here, you feel sure. Now the furniture is matchwood and the windows are glassless. Outside, it is a warm, sunny day, and grasslands extend to the low hills on the horizon.",
    "dragon": "Welcome to Dragon Adventure. You start your quest on a mountain path in the North-East... A tiny sparrowhawk wheels and soars lazily in the cool empty air above. There is a steep pathway to the south leading down into dense woodland, and you can make out an old building by the path. In the distance you can just glimpse the steel-grey of the sea, far away to the west. You can go north, south, east or west.",
    "jewel": "Fifth Layer of the Earth's Crust Endless dark and foreboding passages surround you on all sides. You're cold, tired, and that musty smell in the air has really started getting to you lately. Spelunking seemed much more romantic when you first agreed to accept the mission for the Jewel. Untold riches, fame, glory; it seemed so perfect. Now you're a month into the expedition with little to show for it except for a few rock samples and the death of a party member. You're deep inside the fifth layer of the Earth's crust, surrounded by tight shafts and ominous pits. You are quickly descending to the sixth and final layer; the resting place of the fabled Jewel. Your good friend and fellow campaigner Jacob is here. He slowly scuttles through the underground by your side.",
    "library": "ALL QUIET ON THE LIBRARY FRONT. Every library should try to be complete on something, if it were only the history of pinheads. -- Oliver Wendell Holmes, The Poet at the Breakfast-Table You are a student at Anycollege, in Anytown, and it\'s the end of the semester! You\'ve been slacking off all semester long, and it\'s catching up to you. That final paper is due for your Computer Science class (The History of IF Games), and you desperately need to check out a comprehensive book on Graham Nelson, one of the foremost authors of the obscure genre of interactive-fiction. You know there is exactly one such book, but you have no idea where it might be! The circulation desk dominates the room, seemingly cobbled together over the course of several generations from an assortment of desks and tables. A pair of security gates stands before the front doors to prevent people from stealing books. A card catalog lurks in a dark and dusty corner of the room, seemingly cringing away from the harsh flourescent light. Glass doors to the west lead to the book stacks; an archway to the northwest is labelled Duplicating Services; a door to the north bears a sign marked Private in large friendly letters; and the exit is to the east You can see a circulation desk attendant here.",
    "omniquest": "There's nothing to do, and you're sort of tired, so you lay on your bed and think philosophical thoughts. (meaning of life, end of the world, etc.) As you philosophize, you begin to doze... You wake up with a horrible headache. As you glance around, you realize that you are not in Kansas anymore. You attempt to gain some bearing as to where you are...  Large Clearing You are standing in a large clearing surrounded by a dense forest. There is a path to the east. You can see a tree here.",
    "reverb": "Life sucks. Today has been just another crummy day in another dismal spring which you\'ve spent delivering pizzas. This afternoon has totally been dragging, except for that bit of excitement an hour ago when you broke the soda machine. You thought your boss was going to rip you a new orifice. Anyway, you\'ve just finished mopping up behind the counter. There\'s only one more hour left on your shift and you\'re anxious to get out of here. Go home, watch the tube, blast some tunes, maybe scan the new Surfers Monthly magazine... gonna be a nice relaxing evening. Shyeah, right. That\'s what YOU think. Behind the Counter You are behind the counter at Mr. Tasty\'s Pizza Parlor, where you are currently working. Not much of a job, but it keeps you from going broke during the nine months of the year when you can\'t pull down the bucks as surfing instructor. The rest of the parlor is southwest. There is something pressing that you think you have to do, but you can\'t think what it might be.",
    "snacktime": "<RRROWWGRROWL> Your stomach growls. You\'ve been vegging out in front of that flickering screen for hours, your pet by your side. Now your complaining stomach sets you up on your feet, and on a mission. Snack Time! Sitting Room This is the room where you sit a lot. Well, you sleep here sometimes too. But there is a different room that is just for sleeping, and it is to the north. There\'s another room to the west. It\'s the room with the food. That is a good room. Even though this is the sitting room you can\'t sit on everything. There are a lot of nos here, like the thing you can\'t scratch, and the tall thing and the four-legged thing that isn\'t alive but that stands still with the box of light on its back. Your pet is here, all stretched out on the long soft thing and snoring.",
    "zenon": "Escape from Starship Zenon. The story so far: Accused of multi-planaterial murder and thrown in the high-security brig of a large federal starship with a life sentence. What a downer. There's probably some fiendishly tricky and elusive way to escape from here if you put your mind to it, you know. Over to you. Type help for help. Please read the read me. If you ever get out of here, you really must complain to the prison's standards officers. This place is dirtier and dustier than a dirt factory. If you didn't have better things to do, you'd be in the right mind too give the place a jolly good clean just too spite it. There's a heavily built door to the south. You can see a door, a bed, a pressure guage and a light switch here.",
    "zork1": "You are standing in an open field west of a white house, with a boarded front door. There is a small mailbox here. ",
    "zork2": "Inside the Barrow You are inside an ancient barrow hidden deep within a dark forest. The barrow opens into a narrow tunnel at its southern end. You can see a faint glow at the far end. A strangely familiar brass lantern is lying on the ground. A sword of Elvish workmanship is on the ground.",
    "zork3": "Endless Stair You are at the bottom of a seemingly endless stair, winding its way upward beyond your vision. An eerie light, coming from all around you, casts strange shadows on the walls. To the south is a dark and winding trail. Your old friend, the brass lantern, is at your feet. ",
    "night": "This isn't happening, it really isn't.  You were just about to finish up a two week probationary period as a site operator at the University computer center on the third floor of Hodges Hall.  It was a quiet night, you were working on that interactive fiction game, nobody around...and then you saw a shadow out of the corner of your eye.  And one of the laser printers is gone.  Unless it's back before 7am, this job - the one you were counting on to pay your tuition next semester - is, shall we say, history.  You sigh.  It's not going to be just another...This is the computer site. You know, half a dozen PCs, couple of Macs, a printer table, the desk at which you write that interactive fiction game instead of study. An internet router hums quietly in the corner. The door is northeast.",
    "detective": " << Chief\'s office >> You are standing in the Chief\'s office. He is telling you The Mayor was murdered yeaterday night at 12:03 am. I want you to solve it before we get any bad publicity or the FBI has to come in. Yessir! You reply. He hands you a sheet of paper. Once you have read it, go north or west. You can see a piece of white paper here.",
    "pentari": "A beautiful day in Bostwin! After the challenges of the past year when you were first promoted and assumed command of Charlie Company you've nearly forgotton what free time is and what you're supposed to do with it. When you were a lowly lieutenant you had to share cramped quarters with a fellow lieutenant at your previous assignment. Commanding a company of your own affords you the luxury of private, spacious quarters just outside the barracks themselves. As a further abuse of your power your chest and bunk are not standard issue items from the Pentari millitary supply center. You can see a postcard here.",
    "weapon": "You pass the sentry watching the doorway to the Yi control room, hardly aware of his presence, and step inside, stopping before the owner of the familiar, frowning face just inside. Your escorts come to a halt behind you. Tolan, the tall, wiry woman says to you. You steel yourself for the need to speak. Cheryl, you reply. Dig Leader Cheryl Thadafel. I knew you would have need of the greatest Mechanist in the galaxy. Again. Tolan, this is going to be on my terms, or not at all. You turn your empty hands face-up. Cheryl, this is important to me. It is the Yi-Lono-Mordel. Whatever the restrictions, I cannot miss this opportunity. Control Room Most humans would probably find it the height of fashion, but this low ellipsoidal room makes you uncomfortable with its perfect symmetry and sterility. The featureless white wall is broken up only by the large elliptical window in the ceiling and the circular doorway through which you entered. A cluster of forms sits in the center, atop the slightly concave floor. Cheryl Thadafel stands here, watching you closely. ",
    "darkhunt": "The animal stink is rank and close. You raise your crossbow, try to peer beyond dark, wet stone.",
    "loose": "What was that?You freeze, all your senses on alert. Not mineral. Not vegetable, either. That means...animal? Your eyes scan the countryside, swiveling like searchlights, and pause briefly on a grove of trees to the north.No, not there! Up here! guides a voice edged with impatience. As you whirl around, peering up, you squint and shield your eyes against the sun\'s glare. Waving at you from the top of a rickety wooden fence is a well-groomed egg. Rickety Fence The ramshackle wooden fence in front of you seems to lurch from one horizon to the other. Although it hasn\'t fallen over yet, it threatens to at any moment, and if that egg isn\'t careful... The footpath running along the fence veers sharply north. The egg hums a little tune your mother used to sing at bedtime."
}