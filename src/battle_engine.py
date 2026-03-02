import random

class BattleEngine:
    """
    Core OOP logic for Pokemon combat according to grading rules.
    """
    def __init__(self, pokemon1_data, pokemon2_data, type_effectiveness_func):
        """
        Initializes the battle engine.
        
        Args:
            pokemon1_data (dict): Dictionary with keys: name, stats (dict), types (list), 
                                  move (dict with name, power, accuracy, type, damage_class).
            pokemon2_data (dict): Similarly structured.
            type_effectiveness_func (callable): Function that takes (move_type, defender_types) 
                                                and returns a float multiplier.
        """
        self.p1 = pokemon1_data
        self.p2 = pokemon2_data
        self.type_effectiveness_func = type_effectiveness_func
        
        # Initialize HP based on stats
        self.current_hp = {
            self.p1["name"]: self.p1["stats"]["hp"],
            self.p2["name"]: self.p2["stats"]["hp"]
        }
        
        self.battle_log = []
        self.hp_history = []
        
    def run_battle(self):
        """
        Executes the battle loop up to a max of 100 rounds.
        
        Returns:
            dict: {"battle_log": list[dict], "hp_history": list[dict], "winner": str}
        """
        round_num = 1
        winner = "Draw"
        
        # Determine speed order (faster first). Tie -> random
        p1_speed = self.p1["stats"]["speed"]
        p2_speed = self.p2["stats"]["speed"]
        
        if p1_speed > p2_speed:
            order = [(self.p1, self.p2), (self.p2, self.p1)]
        elif p2_speed > p1_speed:
            order = [(self.p2, self.p1), (self.p1, self.p2)]
        else:
            first = random.choice([self.p1, self.p2])
            second = self.p2 if first == self.p1 else self.p1
            order = [(first, second), (second, first)]
            
        # Initial state (Round 0)
        self.hp_history.append({"Round": 0, "Pokemon": self.p1["name"], "HP": self.current_hp[self.p1["name"]]})
        self.hp_history.append({"Round": 0, "Pokemon": self.p2["name"], "HP": self.current_hp[self.p2["name"]]})
            
        while round_num <= 100 and self.current_hp[self.p1["name"]] > 0 and self.current_hp[self.p2["name"]] > 0:
            
            attacker1, defender1 = order[0]
            self._execute_turn(attacker1, defender1, round_num)
            
            if self.current_hp[defender1["name"]] <= 0:
                winner = attacker1["name"]
                # Append final hp states and break
                self.hp_history.append({"Round": round_num, "Pokemon": self.p1["name"], "HP": self.current_hp[self.p1["name"]]})
                self.hp_history.append({"Round": round_num, "Pokemon": self.p2["name"], "HP": self.current_hp[self.p2["name"]]})
                break
                
            attacker2, defender2 = order[1]
            self._execute_turn(attacker2, defender2, round_num)
            
            if self.current_hp[defender2["name"]] <= 0:
                winner = attacker2["name"]
                # Append final hp states and break
                self.hp_history.append({"Round": round_num, "Pokemon": self.p1["name"], "HP": self.current_hp[self.p1["name"]]})
                self.hp_history.append({"Round": round_num, "Pokemon": self.p2["name"], "HP": self.current_hp[self.p2["name"]]})
                break
                
            # Log end of round
            self.hp_history.append({"Round": round_num, "Pokemon": self.p1["name"], "HP": self.current_hp[self.p1["name"]]})
            self.hp_history.append({"Round": round_num, "Pokemon": self.p2["name"], "HP": self.current_hp[self.p2["name"]]})
            round_num += 1

        return {
            "battle_log": self.battle_log,
            "hp_history": self.hp_history,
            "winner": winner
        }
        
    def _execute_turn(self, attacker, defender, round_num):
        move = attacker["move"]
        move_name = move["name"]
        move_power = move.get("power", 0)
        move_accuracy = move.get("accuracy", 100)
        if move_accuracy is None:
            # Some moves have True accuracy bypass -> None in pokeapi
            move_accuracy = 100
        move_type = move["type"]
        damage_class = move["damage_class"]
        
        # Accuracy check
        if move_accuracy != 100 and random.random() >= (move_accuracy / 100.0):
            # Miss
            self.battle_log.append({
                "Round": round_num,
                "Attacker": attacker["name"],
                "Defender": defender["name"],
                "Move": move_name,
                "Damage": 0,
                "Message": "Missed!"
            })
            return
            
        # Calculate Damage
        level = 50
        attacker_stats = attacker["stats"]
        defender_stats = defender["stats"]
        
        if damage_class == "physical":
            attack_stat = attacker_stats["attack"]
            defense_stat = defender_stats["defense"]
        else:
            attack_stat = attacker_stats["special-attack"]
            defense_stat = defender_stats["special-defense"]
            
        effectiveness = self.type_effectiveness_func(move_type, defender["types"])
        
        # Final formula
        damage = int(
            ((2 * level / 5 + 2) * move_power * (attack_stat / defense_stat) / 50 + 2)
            * effectiveness
        )
        
        # Construct message
        msg = ""
        if effectiveness >= 2.0:
            msg = "It's super effective!"
        elif effectiveness > 0 and effectiveness <= 0.5:
            msg = "It's not very effective..."
        elif effectiveness == 0:
            msg = "It had no effect!"
            
        # Apply damage
        self.current_hp[defender["name"]] -= damage
        if self.current_hp[defender["name"]] < 0:
            self.current_hp[defender["name"]] = 0
            
        self.battle_log.append({
            "Round": round_num,
            "Attacker": attacker["name"],
            "Defender": defender["name"],
            "Move": move_name,
            "Damage": damage,
            "Message": msg
        })
