import random
class Enemy:
    def __init__(self, health, damage, probability_being_hit, killfunc, name, description):
        self.health = health
        self.damage = damage
        self.description = description
        self.probability_being_hit = probability_being_hit
        self.name = name
        self.killfunc = killfunc

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 1:
            return False
            #ENEMY DEAD
        return True
    
    def describe(self):
        print()
        print (self.name)
        print(self.description)
    def attack_player(self, player):
        alive = True
        if random.random() <= player.probability_being_hit:
            alive = player.take_damage(self.damage)
            print("\nThe enemy hit you!")
        else:
            print("\nThe enemy missed you!")
        return alive  
    def do_killfunc(self, room, player):
        self.killfunc(room, player)
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
    def use(self, player):
        self.durability -= 1
        if self.durability < 1:
            print("Your " + self.name + " broke!")
            player.weapon = None
        

class Player:
    def __init__(self, health, sanity, probability_being_hit):
        self.health = health
        self.sanity = sanity
        self.max_health = health
        self.probability_being_hit = probability_being_hit
        self.inventory = []
        self.weapon = None
    def display_stats(self):
        print()
        print("Health:", self.health)
        if self.sanity < 1:
            print("Sanity: INSANE")
        print("Sanity:", self.sanity)
        if self.weapon is None:
            print("Weapon: None")
        else:
            print("Weapon:", self.weapon.name)
            print("Weapon Durability:", self.weapon.durability)
    def drop_weapon(self, room, weapon):
        room.add_action(("Pick up " + weapon.name), weapon.pickup_function)
        room.add_item(weapon)
        self.weapon = None
    def set_weapon(self, room, weapon):
        if self.weapon is not None:
            self.drop_weapon(room, self.weapon)
        self.weapon = weapon
    def attack_enemy(self, enemy):
        alive = True
        if random.random() <= enemy.probability_being_hit:
            if self.weapon is None:
                weapon_damage = 5
            else:
                weapon_damage = self.weapon.damage
                self.weapon.use(self)
            alive = enemy.take_damage(weapon_damage)
            print("You hit the enemy!")
        else:
            print("You missed the enemy!")
        return alive
    def take_damage(self, damage):
        self.health -= damage
        if self.health < 1:
            return False
            #GAMEOVER
        return True
    def take_sanity(self, sanity):
        self.sanity -= sanity
    def gain_health(self, heal):
        self.health += heal
        if self.health > self.max_health:
            self.health = self.max_health
    def gain_sanity(self, sanity):
        if self.sanity > 0:
            self.sanity += sanity
            if self.sanity > 100:
                self.sanity = 100
    def add_inventory(self, item):
        if len(self.inventory) < 5:
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
        self.enemy = None
    def add_enemy(self, enemy):
        self.enemy = enemy
    def remove_enemy(self):
        self.monster = None
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
        print("\n" + self.room_name) #DISPLAY ROOM NAME
        print("\n" + self.room_description) #DISPLAY ROOM DESCRIPTION
        for i in self.items_in_room:
            i.describe_item()
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
player = Player(100, 100, 0.735)

def combat(room, player):
    enemy = room.enemy
    enemy.describe()
    player_alive = True
    enemy_alive = True
    while player_alive is True and enemy_alive is True:
        player_alive = enemy.attack_player(player)
        print("PLAYER HEALTH: ", player.health)
        if player_alive is True:
            input("Press ENTER to continue.")
            print()
            enemy_alive = player.attack_enemy(enemy)
            print("ENEMY HEALTH: ", enemy.health)
            if enemy_alive is True:
                input("Press ENTER to continue.")
    if player_alive is False:
        print("YOU DIED")
        print("GAME OVER")
        exit()
    elif enemy_alive is False:
        print("You killed the enemy!")
        room.remove_enemy()
        enemy.do_killfunc(room, player)
#ROOMS
combo = str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))

outside = Room("OUTSIDE" , "About 50 feet north of you, a large, rundown manor sits. Above the front door, a flickering lantern hangs.\nDirectly to the west, there is an old shed, with its door shut.")
hallone = Room("MANOR ENTRANCE", "To the north, there is a long hall. To the south, there is a door that leads outside. There are doorways on the east and west side of the room.")
shed = Room("SHED", "")
library = Room("LIBRARY", "Entering the room, you see that the whole room is full of bookshelves, each full with hundreds of books. To the north and east, there are doors. On the west side of the room, a strange book catches your eye.")
kitchen = Room("KITCHEN", "When you get into the room, it becomes clear that this is a kitchen. There is an oven, some cabinets, a fridge, and a sink. The the north and west there are doors.")
secret_room = Room("SECRET ROOM", "Sitting on the floor infront of you, there is a box. Behind you, there is the exit.")
workshop = Room("WORKSHOP", "In this room, there is a workbench with tools on it, and on the floor, some mangled contraption that looks at though it has been torn apart. To the east and south there are doors.")
halltwo = Room("MIDDLE OF HALL", "You are now in the middle of the long hallway. There is nothing special, but there are doors to east and west, and the hall continues to the north and south.")
dining_room = Room("DINING ROOM", "This room has a very long table yet only two chairs at either end. There are doors to the east, south, and west.")
bar = Room("BAR", "To the east side of the room, there is a bar. Sitting on top of it, there is a bottle of suspicious liquid. To the west, there is the exit.")
hallthree = Room("END OF HALL", "This is the end of the hall. to the west, there is a door. To the east, there are stairs. To the south, the hallway continues. Next to the stairs, there is a suit of armor holding a sword.")
theater = Room("THEATER", "There is a large stage at the back of the room. On the screen, there is a large, yellow number " + combo[1] + ".")
upstairshall = Room("UPSTAIRS", "This is a hallway at the top of the stairs. There are doors to the east and west, and there are stairs to the north.")
bathroom = Room("BATHROOM", "This is a bathroom. There is a large bathtub, and a cabinet above the sink. To the east there is the exit.")
bedroom = Room("BEDROOM", "In this room, there is a large bed. Under the covers, there is a lump. To the west, there is the exit.")

#OUTSIDE

def investigate_shed(room, player, text):
    print("There is a combination lock on the door. It is four digits, each a different color. From left to right:\nRed, Yellow, Green, Blue.")
    guess = input("Enter a four digit combination --> ")
    if guess == combo:
        print("\nThe lock clicks open, and you walk in.")
        return shed
    else:
        print("\nThe lock doesn't budge.")
    return room
outside.add_action("Investigate the shed", investigate_shed)

def go_manor(room, player, text):
    print("You walk up to the front door. Surprisingly, it is unlocked. You walk inside.")
    return hallone
outside.add_action("Go to the manor" , go_manor)

#HALL ONE
def pickup_letteropener(room, player, text):
    print("\nYou pick up the letter opener.")
    room.remove_item(letter_opener)
    player.set_weapon(room, letter_opener)
    room.remove_action(text)
    return room
letter_opener = Weapon("Letter Opener", "There is a letter opener on the ground.", pickup_letteropener, 2, 10)
hallone.add_item(letter_opener)
hallone.add_action("Pick up letter opener", pickup_letteropener)

def hallone_gonorth(room, player, text):
    if player.sanity > 99:
        return halltwo
    else:
        return halltwo
hallone.add_action("Go north", hallone_gonorth)
def hallone_goeast(room, player, text):
    if player.sanity > 99:
        return kitchen
    else:
        return kitchen
hallone.add_action("Go east", hallone_goeast)
def hallone_gosouth(room, player, text):
    if player.sanity > 99:
        return outside
    else:
        return outside
hallone.add_action("Go south", hallone_gosouth)
def hallone_gowest(room, player, text):
    if player.sanity > 99:
        return library
    else:
        return library
hallone.add_action("Go west", hallone_gowest)

#SHED

#LIBRARY
def library_gonorth(room, player, text):
        return workshop
library.add_action("Go north", library_gonorth)
def library_goeast(room, player, text):
    if player.sanity > 99:
        return hallone
    else:
        return halltwo
library.add_action("Go east", library_goeast)
def investigate_bookshelf(room, player, text):
    print("\nYou walk over to the bookshelf, and get a closer look at the book. The text on the spine looks like english, but it also seems to be moving. You can't quite make it out")
    while True:
        choice = input("\nTake the book out?\n(yes/no): ")
        if choice == "yes":
            print("\nAs you reach to pull out the book, you hear something behind you. You look back, and there is nothing.")
            print("-10 SANITY")
            player.sanity -= 10
            print("Turning back to the book and pulling on it, it slides halfway and then stops. Suddenly, a hidden door next to you swings open. You walk in.")
            return secret_room
        elif choice == "no":
            print("\nYou leave the book alone.")
            return room
        else:
            print("Enter 'yes' or 'no'")
library.add_action("Investigate bookshelf", investigate_bookshelf)


#KITCHEN
def investigate_cabinet(room, player, text):
    print("There is nothing in the cabinet.")
    return room
kitchen.add_action("Investigate cabinet", investigate_cabinet)
def pickup_fridgefood(room, player, text):
    print("\nYou pick up the food.")
    room.remove_item(fridge_food)
    player.add_inventory(fridge_food)
    room.remove_action(text)
    return room
fridge_food = Item("Food", "There is food in the fridge.", pickup_fridgefood)
def use_food(room, player, text):
    player.gain_health(25)
    player.remove_inventory(fridge_food)
fridge_food.add_usefunction(use_food)
fridge_food.add_dropfunction(drop_item)

def investigate_fridge(room, player, text):
    print("You open the fridge, and inside there is food.")
    room.add_item(fridge_food)
    room.add_action("Pick up the food.", pickup_fridgefood)
    room.remove_action(text)
    return room
kitchen.add_action("Investigate fridge", investigate_fridge)

def kitchen_gonorth(room, player, text):
    if player.sanity > 99:
        return dining_room
    else:
        return hallone
kitchen.add_action("Go north", kitchen_gonorth)
def kitchen_gowest(room, player, text):
    if player.sanity > 99:
        return hallone
    else:
        return workshop
kitchen.add_action("Go west", kitchen_gowest)

#SECRET ROOM
def secretroom_leave(room, player, text):
        return library
secret_room.add_action("Leave room", secretroom_leave)
def open_box(room, player, text):
    print("Inside the box, painted in old red paint, is the number " + combo[0] + ".")
    return room
secret_room.add_action("Open box", open_box)

#WORKSHOP
def pickup_saw(room, player, text):
    print("\nYou picked up the saw.")
    room.remove_item(saw)
    player.set_weapon(room, saw)
    room.remove_action(text)
    return room
saw = Weapon("Saw", "There is a saw on the ground.", pickup_saw, 5, 20)
workshop.add_action("Pick up saw", pickup_saw)
def scaryguy_killfunc(room, player):
    print("It dropped a saw!")
    room.add_item(saw)
scaryguy = Enemy(20, 34, 0.67, scaryguy_killfunc, "GHOST FACE", "                    \n     ███████████    \n   ██████████████▒  \n  ████████████▓███  \n ▓████████████████░ \n █████████████████▒ \n ██     ████     ██ \n █░     ████     ██ \n ███░ ██████░  ████ \n ████ ███████ ▓████ \n  ▓░  ███████░ ░██  \n   ▓▓         ░▓▒   \n    ██  ░▒  █ █░    \n     ▓ █▓ ░██ ▓     \n       █████▓       \n                    ")
workshop.add_enemy(scaryguy)

def workshop_goeast(room, player, text):
        return halltwo
workshop.add_action("Go east", workshop_goeast)
def workshop_gosouth(room, player, text):
    if player.sanity > 99:
        return library
    else:
        return hallthree
workshop.add_action("Go south", workshop_gosouth)

#HALLTWO
def halltwo_gonorth(room, player, text):
        return hallthree
halltwo.add_action("Go north", halltwo_gonorth)
def halltwo_goeast(room, player, text):
    if player.sanity > 99:
        return dining_room
    else:
        return kitchen
halltwo.add_action("Go east", halltwo_goeast)
def halltwo_gosouth(room, player, text):
    if player.sanity > 99:
        return hallone
    else:
        return bar
halltwo.add_action("Go south", halltwo_gosouth)
def halltwo_gowest(room, player, text):
    if player.sanity > 99:
        return workshop
    else:
        return outside
halltwo.add_action("Go west", halltwo_gowest)

#DINING ROOM
def pickup_diningfood(room, player, text):
    print("\nYou pick up the food.")
    room.remove_item(dining_food)
    player.add_inventory(dining_food)
    room.remove_action(text)
    return room
dining_food = Item("Food", "There is food on the table.", pickup_diningfood)
dining_room.add_item(dining_food)
dining_room.add_action("Pick up the food.", pickup_diningfood)
def use_diningfood(room, player, text):
    player.gain_health(25)
    player.remove_inventory(dining_food)
dining_food.add_usefunction(use_diningfood)
dining_food.add_dropfunction(drop_item)

def dining_room_goeast(room, player, text):
        return bar
dining_room.add_action("Go east", dining_room_goeast)
def dining_room_gosouth(room, player, text):
        return kitchen
dining_room.add_action("Go south", dining_room_gosouth)
def dining_room_gowest(room, player, text):
    if player.sanity > 99:
        return halltwo
    else:
        return theater
dining_room.add_action("Go west", dining_room_gowest)

#BAR
def pickup_bottle(room, player, text):
    print("\nYou pick up the bottle of suspicious liquid.")
    room.remove_item(bottle)
    player.add_inventory(bottle)
    room.remove_action(text)
    return room
bottle = Item("Bottle", "There is a bottle of suspicious liquid.", pickup_bottle)
bar.add_item(bottle)
bar.add_action("Pick up bottle", pickup_bottle)
def use_bottle(room, player, text):
    player.take_sanity(20)
    player.remove_inventory(bottle)
bottle.add_usefunction(use_bottle)
bottle.add_dropfunction(drop_item)

def bar_gowest(room, player, text):
    if player.sanity > 99:
        return dining_room
    else:
        return workshop
bar.add_action("Leave", bar_gowest)

#HALLTHREE
def pickup_sword(room, player, text):
    print("\nYou picked up the sword.")
    room.remove_item(sword)
    player.set_weapon(room, sword)
    room.remove_action(text)
    return room
sword = Weapon("Sword", "There is a sword on the ground.", pickup_sword, 10, 30)
def knight_killfunc(room, player):
    print("It dropped a sword!")
    room.add_item(sword)
    hallthree.add_action("Pick up sword", pickup_sword)
knight = Enemy(40, 34, 0.67, knight_killfunc, "SUIT OF ARMOR", "He looks super scary.")
def try_take_sword(room, player, text):
    print("You try to pull the sword from the armor, but he starts to move.")
    room.remove_action(text)
    hallthree.add_enemy(knight)
    combat(room, player)
    return room
hallthree.add_action("Take the sword", try_take_sword)
def hallthree_goeast(room, player, text):
        return upstairshall
hallthree.add_action("Go upstairs", hallthree_goeast)
def hallthree_gosouth(room, player, text):
    if player.sanity > 99:
        return halltwo
    else:
        return dining_room
hallthree.add_action("Go south", hallthree_gosouth)
def hallthree_gowest(room, player, text):
    if player.sanity > 99:
        return theater
    else:
        return library
hallthree.add_action("Go west", hallthree_gowest)

#THEATER
def meanguy_killfunc(room, player):
    print("You killed the mean monster.")
meanguy = Enemy(40, 34, 0.67, meanguy_killfunc, "MEAN MONSTER", "He is really, really mean.")
theater.add_enemy(meanguy)

def theater_goeast(room, player, text):
        return hallthree
theater.add_action("Leave", theater_goeast)

#UPSTAIRS
def upstairshall_gonorth(room, player, text):
        return halltwo
upstairshall.add_action("Go downstairs", upstairshall_gonorth)
def upstairshall_goeast(room, player, text):
        return bedroom
upstairshall.add_action("Go east", upstairshall_goeast)
def upstairshall_gowest(room, player, text):
        return bathroom
upstairshall.add_action("Go west", upstairshall_gowest)

#BATHROOM
def pickup_pills(room, player, text):
    print("\nYou pick up the pills.")
    room.remove_item(pills)
    player.add_inventory(pills)
    room.remove_action(text)
    return room
pills = Item("Pills", "There are pills.", pickup_pills)
def use_pills(room, player, text):
    player.gain_sanity(100)
    player.remove_inventory(pills)
pills.add_usefunction(use_pills)
pills.add_dropfunction(drop_item)

def investigate_bathroom_cabinet(room, player, text):
    print("You open the cabinet, and inside there are pills.")
    room.add_item(pills)
    room.add_action("Pick up the pills.", pickup_pills)
    room.remove_action(text)
    return room
bathroom.add_action("Investigate cabinet", investigate_bathroom_cabinet)

def bathroom_gowest(room, player, text):
        return upstairshall
bathroom.add_action("Leave", bathroom_gowest)

#BEDROOM
def bedroom_goeast(room, player, text):
        return upstairshall
bedroom.add_action("Leave", bedroom_goeast)

#GAMELOOP
    #REMOVE
print("\nCOMBO IS", combo)
print("When you open your eyes, you find yourself lying beneath a large oak tree in a dark forest. You search your memory, trying to remember how you got here. Rubbing the large bump on your head and failing to recall, you get up and start walking. You discover that you have nothing on you except your clothes. As you wander through the forest, you see a faint light through the trees. Continuing to push through the densely packed trees, you come upon a clearing.")
input("\npress enter to continue")

current_room = outside
current_room.describe_room()
while True:
    if player.sanity < 100:
        player.take_sanity(10)
    player.display_stats()
    new_room = current_room.action_selection(player)
    if new_room is not current_room:
        current_room = new_room
        if current_room.enemy is not None:
            combat(current_room, player)
        current_room.describe_room()