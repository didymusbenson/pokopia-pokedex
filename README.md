# TLDR
This is an MCP that you can ask about Pokopia mons and get answers. What it doesn't know, you can train it to do.

Current knowledge base (easily expandable): 
* Habitats, habitat recipes, Pokemon found in each
* Pokemon and their special abilities
* Areas to find pokemon

Planned Improvements: 
* Crafting recipes
* Unlock progression
* Basically everything else

# Details

This is a fork of the WintersRain coppermind, a lightweight chromaDB-backed MCP "brain" for maintaining context between AI tools.

You can read the full details on [the original repo](https://github.com/WintersRain/coppermind), or in [BORING_README.md](BORING_README.md) - It's not actually boring, it's pretty dang suite.

Multiple copperminds can be configured to run in isolation, I set this one up as "POKEDEX" and fed it a bunch of tables for Pokopia. Because this is an AI tool, I'll make setup easy for you

```
Install this MCP server for me globally. Look at the /data directory for the POKEDEX. Set me up to be able to read and write to the Pokedex coppermind.
```

Let Claude, Codex, Gemini, whatever do the rest for you.

As I run into things I need quick answers for, I'll be adding more data to my Pokedex, but don't let that stop you from cloning today and feeding it your own data. I'm working on a similar setup for a few other games and will try to find a way to package these better. 