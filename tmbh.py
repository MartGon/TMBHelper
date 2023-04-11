import argparse
import cmd
import json
import datetime
import requests
import tmb

def Find(dict, key):
    for k, v in dict.items():
        if k.startswith(key):
            return v
    return None

class TMBHelperCMD(cmd.Cmd):
    intro = "Welcome to TMBHelper. Type help or ? to list commands"
    prompt = "\nPlease, type a command\n\n"

    def do_char(self, args):
        'Retrieve information regarding a character loot history, wishlist or prios.\nUsage: char [history/wishlist/prio] charname'
        characters = self.characters

        args = self.parse(args)
        if len(args) == 0:
            print("Wrong number of arguments. Usage: char [history/wishlist/prio] charname")
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
                sort_by = lambda x : datetime.datetime.strptime(x["received_at"], "%Y-%m-%d %H:%M:%S").date()
                extra = {"is_wishlisted" : lambda x : "Yes" if x["id"] in char.wishlist else "No"}
                history = self.get_char_items(char.recv.items(), sort_by, True, extra)

                print("Items received by {0}".format(char.name))
                self.print_list(history, ["Item Name", "Date", "Wishlisted"], ['itemName','sort_by', 'is_wishlisted'])

            if action is None or action == "wishlist":
                extra = {"is_received" : lambda x : "Yes" if x["is_received"] else "No"}
                wishlist = self.get_char_items(char.wishlist.items(), lambda x : x["order"], False, extra)

                print("Items wishlisted by {0}".format(char.name))
                self.print_list(wishlist, ["Item Name", "Order", "Received"], ['itemName','sort_by', 'is_received'])

            if action is None or action == "prio":
                extra = {"is_received" : lambda i : "Yes" if i["is_received"] else "No", "updated_prio" : lambda i : i["updated_prio"]}
                prios = self.get_char_items(char.prios.items(), lambda x : x["order"], False, extra)

                print("Items prioritized to {0}".format(char.name))
                self.print_list(prios, ["Item Name", "Priority", "Actual Prio", "Received"], ['itemName','sort_by', 'updated_prio', 'is_received'])

    def get_char_items(self, itemList, sort_by, reverse=True, extra={}):
        items = []
        for id, item in itemList:
            i = {"itemName" : item["name"], "sort_by" : sort_by(item)}
            for k, e in extra.items():
                i[k] = e(item)
            items.append(i)
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
        'Retrieve information regarding a specific item in loot history, wishlist or prios.\nUsage: item [history/wishlist/prio] "itemName"'

        args = self.parse(args)
        if len(args) == 0:
            print('Wrong number of arguments. Usage: item [history/wishlist/prio] "itemName"')
            return

        action, itemName = self.get_action_and_name(args)
        
        if action is None or action == "history":
            sort_by = lambda x : datetime.datetime.strptime(x["received_at"], "%Y-%m-%d %H:%M:%S").date()
            history = self.get_items(itemName, lambda x : x.recv.items(), sort_by)
            self.print_list(history, ["Received by", "Item Name", "Date"], ['character', 'itemName','sort_by'])

        if action is None or action == "wishlist":
            extra = {"is_received" : lambda i, c : "Yes" if i["is_received"] else "No"}
            wishlist = self.get_items(itemName, lambda x : x.wishlist.items(), lambda x : x["order"], False, extra)
            self.print_list(wishlist, ["Wishlisted by", "Item Name", "Order", "Received"], ['character', 'itemName','sort_by', 'is_received'])

        if action is None or action == "prio":
            extra = {"is_received" : lambda i, c : "Yes" if i["is_received"] else "No", "updated_prio" : lambda i, c : i["updated_prio"]}
            prios = self.get_items(itemName, lambda x : x.prios.items(), lambda x : x["order"], False, extra)
            self.print_list(prios, ["Prioritized to", "Item Name", "Priority", "Actual Prio", "Received"], ['character', 'itemName','sort_by', 'updated_prio', 'is_received'])

    def get_items(self, itemName, itemList, sort_by, reverse=True, extra={}):
        items = []
        for name, char in self.characters.items():
            for id, item in itemList(char):
                if itemName.lower() in item["name"].lower() :
                    i = {"character" : name, "itemName" : item["name"], "sort_by" : sort_by(item)}
                    for k, e in extra.items():
                        i[k] = e(item, char)
                    items.append(i)
                    
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
    
def main():
    parser = argparse.ArgumentParser(prog='TMBConsultor', description='Queries TMB for quick searches', epilog='Call with --help to find a list of available commands')
    parser.add_argument("--cookie")
    parser.add_argument("--url")
    parser.add_argument("--file", default="character-json.json")
    args = parser.parse_args()

    # Download data from server if url and cookie are provided
    if args.url and args.cookie:
        print("Downloading data from server")
        cookies = {"thats_my_bis_session": args.cookie}
        r = requests.get(args.url, cookies=cookies)
        if r.status_code == 200:
            if "Content-Type" in r.headers and "json" in r.headers["Content-Type"]:
                print("Data downloaded successfully!")
                json_data = r.content
            else:
                print("Content Type was not correct. Try with a working Cookie/URL")
                return
        else:
            print("Error during request. Status code: ", r.status_code)
            return
    # Try to read from a file otherwise
    else:
        json_data = open(args.file).read()


    characters, items = tmb.ReadDataFromJson(json_data)
    cmd = TMBHelperCMD()
    cmd.characters = characters
    cmd.cmdloop()


if __name__ == "__main__":
    main()