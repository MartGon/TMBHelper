import argparse
import cmd
import json

class Item:
    
    def __init__(self, item_json):
        self.name = item_json["name"]

class Character:

    def __init__(self, char_json):
        self.name = char_json["name"]
        self.recv = Character.extract_items_info(char_json["received"])
        self.wishlist = Character.extract_items_info(char_json["wishlist"])
        self.prios = Character.extract_items_info(char_json["prios"])
    
    def extract_items_info(recv_json):
        recv = {}
        for i in recv_json:
            recv[i["id"]] = i
        return recv
    
    def printRecv(self):
        for k, v in self.recv.items():
            print("Item name: ", v["name"])

def ReadDataFromJson(json_path):

    characters = {}
    items = {}
    with open(json_path) as f:
        res = json.load(f)

        for character in res:
            characters[character["name"]] = (Character(character))
    
    return characters, items

def Find(dict, key):
    for k, v in dict.items():
        if k.startswith(key):
            return v
    return None

class TMBHelperCMD(cmd.Cmd):
    intro = "Welcome to TMBHelper. Type help or ? to list commands"
    prompt = "\nPlease, type a command\n\n"

    def do_character(self, argument):
        'Retrieve information regarding a character loot history, wishlist or prios'
        charName = argument
        characters = self.characters

        char = None
        if charName in characters:
            char = characters[charName]
        else:
            char = Find(characters, charName)

        if char is None:
            print("Character not found: ", charName)
            return

        if char:
            print(char.name)
            char.printRecv()

    def do_item(self, args):
        'Retrieve information regarding a specific item in loot history, wishlist or prios'

        args = self.parse(args)
        print(args)
        if len(args) == 0:
            print("Need arguments")
            return
        
        action = None
        itemName = args[0]
        if args[0] in ['wishlist', 'prio', 'history']:
            action = args[0]
            itemName = args[1]
        
        characters = self.characters
        print("{0:<12s}\t{1:<32s}\t{2:<32s}".format("Received by", "Name", "Date"))
        for name, char in characters.items():
            for id, item in char.recv.items():
                if item["name"].lower().startswith(itemName.lower()):
                    #print(name, "\t\t\t", item["name"], "\t\t\t", item["pivot"]["received_at"])
                    print("{0:<12s}\t{1:<32s}\t{2:<32s}".format(name, item["name"], item["pivot"]["received_at"]))

    def do_exit(self, argument):
        'Exits the program'
        print("Exitting...")
        exit(0)
    
    def parse(self, args):
        char = '"' if '"' in args else ' '
        return list(map(lambda x : x.strip(), filter(lambda x : bool(x), args.split(char))))

global characters

def main():
    parser = argparse.ArgumentParser(prog='TMBConsultor', description='Queries TMB for quick searches', epilog='Call with --help to find a list of available commands')
    parser.add_argument("--file", default="character-json.json")
    args = parser.parse_args()

    characters, items = ReadDataFromJson(args.file)
    cmd = TMBHelperCMD()
    cmd.characters = characters
    cmd.cmdloop()


if __name__ == "__main__":
    main()