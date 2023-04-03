# TMBHelper

TMBHelper is a command line tool which aids querying data from your guild's loot history, wishlists and priorities.

## Requirements

In order to run this program you'll need:

- Python3
- TMB JSON Blob. You can download it from TMB web page in **Guild&rarr;Export&rarr;Giant JSON blob**

## How to use

First run the program

```
python3  tmb.py --file character-json.json
```

You may download it directly from the server by providing a TMB session cookie and the JSON download url

```
python3  tmb.py --cookie eyBsts... --url https://thatsmybis.com/12345/pin-pals/export/characters-with-items/json
```

Then you'll be greeted with a prompt

```
Welcome to TMBHelper. Type help or ? to list commands

Please, type a command
```

Here you can choose between two main commands depending how you'd like to query data:
- **char**: Takes a character name. Queries loot history, wishlist and priority list of a given character.
- **item**: Takes an item name, between quotes. Queries who has received, wishlisted and the priority of a given item.

For both commands you can show only one of the three lists. E.g. You want to check only the loot history of a given character:

```
char history WatsonWarrrior
```

## Examples

Check loot history, priority list and wishlist of a given item
```
item "Voldrethar, Dark Blade of Oblivion"

Received by                             Item Name                               Date                            
WatsonWarrior                           Voldrethar, Dark Blade of Oblivion      2023-03-29                      

Wishlisted by                           Item Name                               Order                                   Received                        
RicksRet                                Voldrethar, Dark Blade of Oblivion      1                                       No                              
HaroldHunter                            Voldrethar, Dark Blade of Oblivion      1                                       No                              
WatsonWarrior                           Voldrethar, Dark Blade of Oblivion      1                                       Yes                             
                           

Prioritized to                          Item Name                               Priority                                Actual Prio                             Received                        
WatsonWarrior                           Voldrethar, Dark Blade of Oblivion      1                                       0                                       Yes
RicksRet                                Voldrethar, Dark Blade of Oblivion      2                                       1                                       Yes
HaroldHunter                            Voldrethar, Dark Blade of Oblivion      3                                       2                                       Yes
```

Check only the wishlist

```
item "Voldrethar, Dark Blade of Oblivion"
            
Wishlisted by                           Item Name                               Order                                   Received                        
RicksRet                                Voldrethar, Dark Blade of Oblivion      1                                       No                              
HaroldHunter                            Voldrethar, Dark Blade of Oblivion      1                                       No                              
WatsonWarrior                           Voldrethar, Dark Blade of Oblivion      1                                       Yes                             
```

Check a characters loot history

```
char history WatsonWarrior

Items received by WatsonWarrior
Item Name                               Date                                    Wishlisted                      
Voldrethar, Dark Blade of Oblivion      2023-03-29                              Yes     
```