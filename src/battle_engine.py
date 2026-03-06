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

        # Initialize HP based on stats — keyed by slot to support same-name battles
        self.p1["slot"] = "p1"
        self.p2["slot"] = "p2"
        self.current_hp = {
            "p1": self.p1["stats"]["hp"],
            "p2": self.p2["stats"]["hp"]
        }

        # Compute display labels — append (P1)/(P2) when both share the same name
        same_name = self.p1["name"].casefold() == self.p2["name"].casefold()
        self.p1_label = f"{self.p1['name']} (P1)" if same_name else self.p1["name"]
        self.p2_label = f"{self.p2['name']} (P2)" if same_name else self.p2["name"]

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
        self.hp_history.append({"Round": 0, "Pokemon": self.p1_label, "HP": self.current_hp["p1"]})
        self.hp_history.append({"Round": 0, "Pokemon": self.p2_label, "HP": self.current_hp["p2"]})
            
        while round_num <= 100 and self.current_hp["p1"] > 0 and self.current_hp["p2"] > 0:
            
            attacker1, defender1 = order[0]
            self._execute_turn(attacker1, defender1, round_num)
            
            if self.current_hp[defender1["slot"]] <= 0:
                winner = attacker1["slot"]  # store slot, resolved to name later
                # Append final hp states and break
                self.hp_history.append({"Round": round_num, "Pokemon": self.p1_label, "HP": self.current_hp["p1"]})
                self.hp_history.append({"Round": round_num, "Pokemon": self.p2_label, "HP": self.current_hp["p2"]})
                break
                
            attacker2, defender2 = order[1]
            self._execute_turn(attacker2, defender2, round_num)
            
            if self.current_hp[defender2["slot"]] <= 0:
                winner = attacker2["slot"]  # store slot, resolved to name later
                # Append final hp states and break
                self.hp_history.append({"Round": round_num, "Pokemon": self.p1_label, "HP": self.current_hp["p1"]})
                self.hp_history.append({"Round": round_num, "Pokemon": self.p2_label, "HP": self.current_hp["p2"]})
                break
                
            # Log end of round
            self.hp_history.append({"Round": round_num, "Pokemon": self.p1_label, "HP": self.current_hp["p1"]})
            self.hp_history.append({"Round": round_num, "Pokemon": self.p2_label, "HP": self.current_hp["p2"]})
            round_num += 1

        # Resolve winner slot -> label
        if winner == "p1":
            winner_label = self.p1_label
        elif winner == "p2":
            winner_label = self.p2_label
        else:
            winner_label = winner  # "Draw" or already a name from old code

        return {
            "battle_log": self.battle_log,
            "hp_history": self.hp_history,
            "winner": winner_label,
            "winner_slot": winner if winner in ("p1", "p2") else None,
            "p1_label": self.p1_label,
            "p2_label": self.p2_label,
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
            attacker_label = self.p1_label if attacker["slot"] == "p1" else self.p2_label
            defender_label = self.p1_label if defender["slot"] == "p1" else self.p2_label
            self.battle_log.append({
                "Round": round_num,
                "Attacker": attacker_label,
                "AttackerSlot": attacker["slot"],
                "Defender": defender_label,
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
        self.current_hp[defender["slot"]] -= damage
        if self.current_hp[defender["slot"]] < 0:
            self.current_hp[defender["slot"]] = 0
            
        # Use labels so same-name battles are distinguishable
        attacker_label = self.p1_label if attacker["slot"] == "p1" else self.p2_label
        defender_label = self.p1_label if defender["slot"] == "p1" else self.p2_label
        self.battle_log.append({
            "Round": round_num,
            "Attacker": attacker_label,
            "AttackerSlot": attacker["slot"],
            "Defender": defender_label,
            "Move": move_name,
            "Damage": damage,
            "Message": msg
        })
