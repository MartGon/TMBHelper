import argparse
import cmd
import json
import datetime

class Item:
    
    def __init__(self, item_json):
        self.name = item_json["name"]

class Character:

    def __init__(self, char_json):
        self.name = char_json["name"]
        self.recv = Character.extract_items_info(char_json["received"], ["received_at", "is_offspec", "officer_note"])
        self.wishlist = Character.extract_items_info(char_json["wishlist"], ["is_received", "order"])
        self.prios = Character.extract_items_info(char_json["prios"], ["is_received", "order"])
    
    def extract_items_info(recv_json, pivot_keys):
        recv = {}
        for i in recv_json:
            item = {"name" : i["name"], "id" : i["id"]}
            for pk in pivot_keys:
                if pk in i["pivot"]:
                    item[pk] = i["pivot"][pk]

            recv[i["id"]] = item
        return recv

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

    def do_char(self, args):
        'Retrieve information regarding a character loot history, wishlist or prios'
        characters = self.characters

        args = self.parse(args)
        if len(args) == 0:
            print("")
            return
        
        action, charName = self.get_action_and_name(args)

        char = None
        if charName in characters:
            char = characters[charName]
        else:
            char = Find(characters, charName)

        if char is None:
            print("Character not found: ", charName)
            return

        if char:
            if action is None or action == "history":
                history = self.get_char_items(char.recv.items(), lambda x : datetime.datetime.strptime(x["received_at"], "%Y-%m-%d %H:%M:%S").date(), True, lambda x : "Yes" if x["id"] in char.wishlist else "No")

                print("Items received by {0}".format(char.name))
                self.print_list(history, ["Item Name", "Date", "Wishlisted"], ['itemName','sort_by', 'extra'])

            if action is None or action == "wishlist":
                wishlist = self.get_char_items(char.wishlist.items(), lambda x : x["order"], False, lambda x : "Yes" if x["is_received"] else "No")

                print("Items wishlisted by {0}".format(char.name))
                self.print_list(wishlist, ["Item Name", "Order", "Received"], ['itemName','sort_by', 'extra'])

            if action is None or action == "prio":
                prios = self.get_char_items(char.prios.items(), lambda x : x["order"], False, lambda x : "Yes" if x["is_received"] else "No")

                print("Items prioritized to {0}".format(char.name))
                self.print_list(prios, ["Item Name", "Priority", "Received"], ['itemName','sort_by', 'extra'])

    def get_char_items(self, itemList, sort_by, reverse=True, extra=lambda x : None):
        items = []
        for id, item in itemList:
                items.append({"itemName" : item["name"], "sort_by" : sort_by(item), "extra" : extra(item)})
        items.sort(key = lambda x : x["sort_by"], reverse=reverse)
        return items
    
    def get_action_and_name(self, args):
        action = None
        name = args[0]
        if args[0] in ['wishlist', 'prio', 'history']:
            action = args[0]
            name = args[1]
        return action, name

    def do_item(self, args):
        'Retrieve information regarding a specific item in loot history, wishlist or prios\n [history, wishlist, prio]'

        args = self.parse(args)
        if len(args) == 0:
            print("")
            return

        action, itemName = self.get_action_and_name(args)
        
        if action is None or action == "history":
            history = self.get_items(itemName, lambda x : x.recv.items(), lambda x : datetime.datetime.strptime(x["received_at"], "%Y-%m-%d %H:%M:%S").date())
            self.print_list(history, ["Received by", "Item Name", "Date"], ['character', 'itemName','sort_by'])

        if action is None or action == "wishlist":
            wishlist = self.get_items(itemName, lambda x : x.wishlist.items(), lambda x : x["order"], False, lambda x : "Yes" if x["is_received"] else "No")
            self.print_list(wishlist, ["Wishlisted by", "Item Name", "Order", "Received"], ['character', 'itemName','sort_by', 'extra'])

        if action is None or action == "prio":
            prios = self.get_items(itemName, lambda x : x.prios.items(), lambda x : x["order"], False, lambda x : "Yes" if x["is_received"] else "No")
            self.print_list(prios, ["Prioritized to", "Item Name", "Priority", "Received"], ['character', 'itemName','sort_by', 'extra'])

    def get_items(self, itemName, itemList, sort_by, reverse=True, extra=lambda x : None):
        items = []
        for name, char in self.characters.items():
            for id, item in itemList(char):
                if itemName.lower() in item["name"].lower() :
                    items.append({"character" : name, "itemName" : item["name"], "sort_by" : sort_by(item), "extra" : extra(item)})
        items.sort(key = lambda x : x["sort_by"], reverse=reverse)
        return items
    
    def print_list(self, itemList, columns, keys):
        for col in columns:
            print("{0:<32s}\t".format(col), end='')
        print()

        for v in itemList:
            for k in keys:
                print("{0:<32s}\t".format(str(v[k])), end='')
            print()
        print()

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