# PZ-scripts-to-item-tag
Automatically convert the entire scripts folder into its tags, then output a page file for pzwiki.net

## How to use this repository:

1. Create a directory called `resources` in the same directory as this `README` file.
2. Find the `scripts` folder in your Project Zomboid install, and copy the folder to the `resources` folder.
3. Download the appropriate `ItemName_XX.txt` from [this git.](https://github.com/TheIndieStone/ProjectZomboidTranslations/)
4. Rename the translation file to `translate.txt` place it into the `resources` folder.
3. Run `main.py` and the results will be output to `output/completed_output.txt`. You now have an updated version of the items spawned by various room definitions, formatted for the Project Zomboid wiki!
    
**NOTICE FOR THOSE SUBMITTING MERGE REQUESTS: DO NOT INCLUDE LUA FILES FROM PROJECT ZOMBOID!**

Those files should not be distributed without permission from The Indie Stone. 