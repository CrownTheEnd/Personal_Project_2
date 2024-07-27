i was thinking it could be cool to make a battle simulator using xiv information
like having a character with set skills and finding the most optimal way of defeating an enemy

so like HP has x amount of HP. you have x,y,z moves with a,b,c damage and x,y,z cooldowns.

also need to account for buffs

its kind of like a set builder

Character information input for name, job, level.
Enemy dictionary containing templates for enemies and an option to create an enemy.

Discord bot maybe?

^^^^^^^^^^^^^^^^^^^^^^^^^^^ This Idea was repurposed into something less annoying ^^^^^^^^^^^^^^^^^^^^^^^^^^^

>I'm trying to see if i can still do a battle sim but as a discord bot and more simple. Basically I want it to:
    1: create a fighter when someone types "/create xyz <image_link>"
    2: assign a random str and speed value to it
    3: let the user queue it with "/queue" so it can battle the next in line
    4: tally its wins 

> The spd and str will reset after every battle

- Could be cool to maybe give it a buff if it wins so the next time it's used it has an advantage and interesting upsets can happen
- Top 10 leaderboard could be cool too
- maybe betting?
- grades for the random stats ie; S, A, B example; 150 HP, Attack: S, B speed

The bot can be like:
> Fighter A:
    HP: 150
    Atk: S
    Spd: B

vs

> Fighter B:
    HP:100
    Atk: A
    Spd: S

^^^^^^^^^^^^^^^^^^^^^^^^^^^ This idea was changed into something more practical ^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Speed value idea scrapped, more interesting to have it be a coinflip per turn that way you can set a wider attack range and have crazy upsets.
- In the same vein as the above point, betting multipliers based on winning odds ie; if A has 150hp and B has 100 hp then B's bet would be 1.5x while A would be .5x
(Did I just realize how a ranking system works...)

>raw brainstorming dump
    "i think im gonna need a user file if i want betting
    if you type /queue Cake the bot sends you a dm giving you info and prompting a reponse command like bet or cancel
    if you bet then it queues the fighter, otherwise it cancels
    that way the other person won't see your bet"