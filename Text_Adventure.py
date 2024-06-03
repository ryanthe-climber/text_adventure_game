import random
class Enemy:
    def __init__(self, health, damage, probability_being_hit, name, description):
        self.health = health
        self.damage = damage
        self.description = description
        self.probability_being_hit = probability_being_hit
        self.name = name

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
            self.drop_weapon(room, weapon)
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
player = Player(100, 100, 0.5)
def combat(room, player):
    enemy = room.enemy
    player_alive = True
    enemy_alive = True
    while player_alive == True and enemy_alive == True:
        print("ENEMY HEALTH: ", enemy.health)
        print("PLAYER HEALTH: ", player.health)
        player_alive = enemy.attack_player(player)
        input("Press ENTER to continue.")
        enemy_alive = player.attack_enemy(enemy)
        print("ENEMY HEALTH: ", enemy.health)
        print("PLAYER HEALTH: ", player.health)
        input("Press ENTER to continue.")
    if player_alive is False:
        print("YOU DIED")
        print("GAME OVER")
        exit()
    elif enemy_alive is False:
        print("You killed the enemy!")
        room.remove_enemy()
#ROOMS
combo = str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9)) + str(random.randint(0, 9))

outside = Room("OUTSIDE" , "About 50 feet north of you, a large, rundown manor sits. Above the front door, a flickering lantern hangs.\nDirectly to the west, there is an old shed, with its door shut.")
hallone = Room("MANOR ENTRANCE", "To the north, there is a long hall. To the south, there is a door that leads outside. There are doorways on the east and west side of the room.")
shed = Room("SHED", "This is a shed.")
library = Room("LIBRARY", "Entering the room, you see that the whole room is full of bookshelves, each full with hundreds of books. To the north and east, there are doors. On the west side of the room, a strange book catches your eye.")
kitchen = Room("KITCHEN", "DESCRIPTION")
secret_room = Room("SECRET ROOM", "Sitting on the floor infront of you, there is a box. Behind you, there is the exit.")
workshop = Room("WORKSHOP", "DESCRIPTION")
halltwo = Room("MIDDLE OF HALL", "DESCRIPTION")
dining_room = Room("DINING ROOM", "DESCRIPTION")
bar = Room("BAR", "DESCRIPTION")
hallthree = Room("END OF HALL", "DESCRIPTION")
theater = Room("THEATER", "DESCRIPTION")
upstairshall = Room("UPSTAIRS", "DESCRIPTION")
bathroom = Room("BATHROOM", "DESCRIPTION")
bedroom = Room("BEDROOM", "DESCRIPTION")

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
letter_opener = Weapon("Letter Opener", "There is a letter opener on the ground.", pickup_letteropener, 3, 10)
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
    print("You open the box.")
    return room
secret_room.add_action("Open box", open_box)

#WORKSHOP
scaryguy = Enemy(50, 25, 0.75, "SCARY GUY", "He is a very scary guy.")
workshop.add_enemy(scaryguy)

#GAMELOOP
    #REMOVE
print("\nCOMBO IS", combo)
print("When you open your eyes, you find yourself lying beneath a large oak tree in a dark forest. You search your memory, trying to remember how you got here. Rubbing the large bump on your head and failing to recall, you get up and start walking. You discover that you have nothing on you except your clothes. As you wander through the forest, you see a faint light through the trees. Continuing to push through the densely packed trees, you come upon a clearing.")
input("\npress enter to continue")

current_room = outside
current_room.describe_room()
while True:
    if player.sanity < 100:
        player.sanity -= 10
    player.display_stats()
    new_room = current_room.action_selection(player)
    if new_room is not current_room:
        current_room = new_room
        if current_room.enemy is not None:
            current_room.enemy.describe()
            combat(current_room, player)
        current_room.describe_room()