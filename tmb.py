import argparse
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

def CharacterCmd(characters, items, argument):
    charName = argument

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

def ItemCMD(characters, items, argument):
    itemName = argument

    print("Item was received by")
    for name, char in characters.items():
        for id, item in char.recv.items():
            if item["name"].startswith(itemName):
                print(name, "\t", item["name"], "\t", item["pivot"]["received_at"])

def main():
    parser = argparse.ArgumentParser(prog='TMBConsultor', description='Queries TMB for quick searches', epilog='Call with --help to find a list of available commands')
    parser.add_argument("action", choices=["character", "item"])
    parser.add_argument("argument", type=str)
    args = parser.parse_args()

    action, argument = args.action, args.argument

    commands = {"character" : CharacterCmd, "item" : ItemCMD}
    characters, items = ReadDataFromJson("character-json.json")

    print("Action chosen: ", action)
    commands[action](characters, items, argument)


if __name__ == "__main__":
    main()