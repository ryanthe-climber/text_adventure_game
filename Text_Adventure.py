import random
class Enemy:
    def __init__(self, health, damage, probability_being_hit, description):
        self.health = health
        self.damage = damage
        self.description = description
        self.probability_being_hit = probability_being_hit

    def attack_player(self, player):
        if random.random() <= player.probability_being_hit:
            player.health -= self.damage
            print("\nThe enemy hit you!")
        else:
            print("\nThe enemy missed you!")    

class Item:
    def __init__(self, name, description, function):
        self.name = name
        self.description = description
        self.pickup_function = function

    def describe_item(self):
        print(self.description)
    
    def add_usefunction(self, function):
        self.use = function
    
    def add_dropfunction(self, function):
        self.drop = function

class Weapon(Item):
    def __init__(self, name, description, function, durability, damage):
        super().__init__(name, description, function)
        self.durability = durability
        self.damage = damage

class Player:
    def __init__(self, health, sanity, probability_being_hit):
        self.health = health
        self.sanity = sanity
        self.max_health = health
        self.probability_being_hit = probability_being_hit
        self.inventory = []
        self.weapon = None
    
    def drop_weapon(self, room, weapon):
        room.add_action(("Pick up " + weapon.name), weapon.pickup_function)
        room.add_item(weapon)
        self.weapon = None
    def set_weapon(self, weapon, room):
        if self.weapon is not None:
            self.drop_weapon(room, weapon)
        self.weapon = weapon
    def attack_enemy(self, weapon, enemy):
        if random.random() <= enemy.probability_being_hit:
            enemy.health -= weapon.damage
            weapon.durability -= 1
            print("You hit the enemy!")
        else:
            print("You missed the enemy!")
    def take_damage(self, damage):
        self.health -= damage
        if self.health < 1:
            return True
            #GAMEOVER
        return False
    def gain_health(self, heal):
        self.health += heal
        if self.health > self.max_health:
            self.health = self.max_health
    def add_inventory(self, item):
        if len(self.inventory) < 10:
            self.inventory.append(item)
        else:
            print("\nYour inventory is full.\nDrop an item in order to pick another one up.")
    def remove_inventory(self, item):
        self.inventory.remove(item)

def manage_inventory(room, player, text):
    if len(player.inventory) < 1:
        print("\nYou have nothing in your inventory.")
        return room
    else:
        new_room = None
        while new_room is None:
            print("INVENTORY:")
            for i in range(len(player.inventory)):
                print(i + 1, "-", player.inventory[i].name)
            print("x - Exit inventory")
            choice = input("Choose an item:\n--> ")
            if choice == "x":
                new_room = room
            elif not choice.isdigit():
                print("Enter a number between 1 and", len(player.inventory))
                continue
            else:
                choice = int(choice)
                if choice > len(player.inventory):
                    print("Enter a number between 1 and", len(player.inventory))
                    continue
                else:
                    print("\nWhat do you want to do with the " + player.inventory[choice - 1].name + "?")
                    print("1 - Use")
                    print("2 - Drop")
                    print("x - Exit")
                    choice2 = input("--> ")
                    if choice2 == "1":
                        new_room = player.inventory[choice - 1].use(room, player, player.inventory[choice - 1])
                    elif choice2 == "2":
                        new_room = player.inventory[choice - 1].drop(room, player, player.inventory[choice - 1])
                    elif choice2 == "x":
                        continue
                    else:
                        print("Enter 1, 2, or x.\n")
        return new_room

class Room:
    default_action_text = ["Inventory"]
    default_action_functions = [manage_inventory]
    def __init__(self, name, description):
        self.room_name = name
        self.room_description = description
        self.action_text = Room.default_action_text.copy()
        self.action_function = Room.default_action_functions.copy()
        self.items_in_room =[]
    def add_item(self, item):
        self.items_in_room.append(item)
    def remove_item(self, item):
        self.items_in_room.remove(item)
    def add_action(self, action, function):
        self.action_text.append(action)
        self.action_function.append(function)
    def remove_action(self, action):
        action_index = self.action_text.index(action)
        self.action_text.pop(action_index)
        self.action_function.pop(action_index)
    def describe_room(self):
        print(self.room_name) #DISPLAY ROOM NAME
        print(self.room_description) #DISPLAY ROOM DESCRIPTION
        for i in self.items_in_room:
            i.describe_item
    def action_selection(self, player):
        for i in range(len(self.action_text)):
            print(i + 1, "-", self.action_text[i])
        while True:
            choice = input("Choose an action:\n--> ")
            if not choice.isdigit():
                print("Enter a number between 1 and", len(self.action_text))
            else:
                choice = int(choice)
                if choice > len(self.action_text):
                    print("Enter a number between 1 and", len(self.action_text))
                else:
                    print()
                    new_room = self.action_function[choice - 1](self, player, self.action_text[choice - 1])
                    print()
                    return new_room



#CONFIG
#STANDARD DROP FUNCTION
def drop_item(room, player, item):
    player.remove_inventory(item)
    room.add_action(("Pick up " + item.name), item.pickup_function)
    room.add_item(item)
    return room

#FUNCTION FORMAT
"""
def function_name(room, player, text):
    print("function_text")
    room.remove_action(text)
    return room
"""
player = Player(100, 100, 0.5)
enemy = Enemy(100, 25, 0.75, "This is a very scary monster.")
roomA = Room("RoomA", "This is room a.")
roomB = Room("RoomB", "This is room b")

def combat(player, enemy):
    player_alive = True
    enemy_alive = True
    while player_alive == True and enemy_alive == True:
        print("ENEMY HEALTH: ", enemy.health)
        print("PLAYER HEALTH: ", player.health)
        enemy.attack_player(player)
        input("Press ENTER to continue.")
        player.attack_enemy(player.weapon, enemy)
        print("ENEMY HEALTH: ", enemy.health)
        print("PLAYER HEALTH: ", player.health)
        input("Press ENTER to continue.")
        

#ROOM A

def eat_food(room, player, item):
    player.gain_health(10)
    player.remove_inventory(item)
    print("\nYou feel better already.")

def get_key(room, player, text):
    print("You pick up the key.")
    player.add_inventory(key)
    room.remove_action(text)
    return room
key = Item("Key", "There is a key.", get_key)
key.add_dropfunction(drop_item)

def get_food(room, player, text):
    print("You pick up the food.")
    player.add_inventory(food)
    room.remove_action(text)
    return room
food = Item("Food", "There is food.", get_food)
food.add_usefunction(eat_food)
food.add_dropfunction(drop_item)
def goto_roomB(room, player, text):
    return roomB

roomA.add_action("Pick up key", get_key)

roomA.add_action("Pick up food", get_food)

roomA.add_action("Go to room b", goto_roomB)

#ROOM B
def get_sword(room, player, text):
    player.set_weapon(sword, room)
    print("\nYou pick up the sword")
sword = Weapon("Sword", "There is a sword.", get_sword, 4, 25)

def goto_roomA(room, player, text):
    return roomA

roomB.add_action("Go to room a", goto_roomA)
#GAMELOOP
player.take_damage(20)
current_room = roomA
current_room.describe_room()
player.set_weapon(sword)
combat(player, enemy)
while True:
    print("Health =", player.health)
    new_room = current_room.action_selection(player)
    if new_room is not current_room:
        current_room = new_room
        current_room.describe_room()
        #monster.shit