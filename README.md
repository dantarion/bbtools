# bbtools
tools for parsing files for Blazblue's engine (P4A PS3/360, P4AU PS3, Blazblue Chronophantasma PC)


# The Goal

The goal here is analyze the game files of several games made by Arc System Works and produce a set of tools that produce useful information to players of the game, as well as document changes Arc System works has made to their engines over time for educational purposes.  Also, we wish to provide a mechanism to track character changes over major and minor patches to discover "secret" patch notes and provide clarity to some of the more general changes.

# The Main Targets

* Blazblue: All versions (Original CT release all the way through the upcoming Central Fiction version)
* Persona 4 Arena and Persona 4 Arena Ultimax
* Guilty Gear Xrd and Guilty Gear Xrd: Revelator (2 too)
* Dragon Ball FighterZ (new, but EAC :( )

# Secondary Targets

* Arcana Heart 3
* Dragon Ball Z: Extreme Butōden

Arcana Heart doesn't use bbscript, but it does use the same sprite format that ArcSys developed games use.
The same may be true of Extreme Butoden. Might as well make the code for these tools flexible enough to dump information and sprites for those games too.

# Parser/Rebuilder Installation Instructions

You need:

Any Python 2.7 (3+ will fail at the moment) added to your PATH (installer option) with pip (get [here](https://bootstrap.pypa.io/get-pip.py) if the installer doesn't present you with the option to install it, right click -> save link)

After that, open a command prompt as administrator to install our one dependency.  (Windows key, cmd, Ctrl+Shift+Enter)

If it didn't present you with the option to install pip, run

```
python C:\complete\path\to\get-pip.py
```

Once done or if it did give you the option and it's installed, run

```
python -m pip install astor==0.5
```

If all went well, you are good to go!

## Decompiling

For this example, I'll be using BBCF.

In the (folder where BBCF.exe is)\data\char\ folder there are a bunch of .pac files that are openable with HIPster.  The .pacs we're looking at look like ``char_xx_scr.pac``.  Extract both .bin files from a .pac of your choice (not one with boss in it if you're looking to see results).  Their names are scr_xx.bin scr_xxea.bin respectively.

scr_xx.bin is the main script file, and controls anything that's directly attached to the character (what sprite and attached collision boxes come out when, where they come out), among other things, including health, OD durations, inputs, as well as many other qualities of the character and their moves.

scr_xxea.bin is called upon by scr_xx.bin when a projectile/visual effect needs to be spawned, and the sprite/collision durations and other properties of said projectiles are found there.

To decompile a script file, it's recommended you put the bin in a new folder inside the bbtools folder with bbcf_bbtag_script_parser.py in it.  Then start up your cmd again (if it's not still open) and type in these two lines:

```
cd C:\path\to\bbtools
python bbcf_script_parser.py mynewfolder\scr_xx.bin
```

  In mynewfolder you should have a scr_xx.py file that's a decompiled version of scr_xx.bin.  For viewing said file easily, a syntax highlighting text editor like Notepad++ or Sublime Text is highly recommended, and set the syntax highlighting to python if not already set once open.

## Editing (Tips)

This is not documentation, this is just a few tips if you're new to python/bbtools.

Single quotes and double quotes are interchangeable for strings.  For example, the below two lines are identical:

```python
SpawnFireball("Hadouken")
SpawnFireball('Hadouken')
```

Whenever you see a colon that ends a line, you must indent **4 spaces** inwards, and whenever you want to end that block of code, you unindent **4 spaces**.  This is a **no-tab zone**.  This includes three types of statements: def funcName():, if, and else.

 

```python
@State #must be either @State or @Subroutine, and must be registered if @State
def fooState(): #includes def upon_420():
	Unknown1() #this statement is inside foo
	if SLOT_5 > 2:
        Unknown2() #this statement is only executed if SLOT_5 > 2, still inside foo
	else: #if SLOT_5 is not greater than 2
        def upon_3(): #still inside foo
            Unknown42(3) #inside upon_3, which is inside foo
        Unknown69('lol_im_immature') #executed immediately after defining upon_3
    Unknown420("Blazblueit") #executed after either branch of the if
	#end of foo
@State #and so on
```

As I noted in the code block above, if ANY function that is not a @State or an @Subroutine is not inside either, the code will refuse to recompile and you will be sad.

If you're in the middle of a bunch of sprite('spritename', x) calls and are unsure what happens when, anything that happens right below a sprite call until the next one happens on its first frame.

Real example:

```python
    sprite('kk202_00', 2) #frames 1-2, these comments don't exist in the real thing
    GFX_0('efkk_202_hole', -1)
    sprite('kk202_01', 2) #3-4
    sprite('kk202_02', 2) #5-6
    sprite('kk202_03', 3) #7-9
    SFX_0('004_swing_grap_1_2')
    Unknown7009(2)
    sprite('kk202_04', 2) #10-11
```

GFX_0 happens on frame 1, while SFX_0 and Unknown7009 happen on frame 7.

Also, strings (state and subroutine names, strings like 004_swing_grap_1_2 in the above snippet, etc.) have a general cap of 32 characters, provided they aren't entirely consisted of the characters 0-9 and a-f.  The latter means we know how much space the function takes, just not how it's formatted, so strings often extend beyond the 32-character limit there.

If you have any python programming-related questions, python.org should have a wonderful reference on how to format things/what basic things do in python and what's valid and what's not valid.  To recompile, the entire file has to be 100% valid python.

## Recompiling

Once you're done, take out your trusty command prompt and type in the final command that'll look like this:

```
python bbcf_script_rebuilder.py myfolder\scr_xx.py otherfolder\scr_xx.bin
```

If you had to close and reopen your command prompt, execute the cd command in the "decompiling" section before doing this, otherwise it won't work.

If it doesn't complain about your new .py file, copy and paste in place the .pac file you got it from, open the .pac that isn't a copy in HIPSter, and replace the existing .bin with your new .bin.  Feel free to play around with whatever devious creation you made.

Obviously there are different processes for different games, (gg, dbfz), but once decompiled, the process is generally the same.  BBTAG is incredibly similar to BBCF + one extra step before decompiling/after recompiling.

------

If you desperately need help and can't figure out for the life of you what you did wrong and your game keeps crashing or your code keeps not compiling (if your mod makes the game load even when doing the modded move, chances are I can't help you there), contact @Labryz#5752 on discord and I'll be glad to help you out.  If you feel you're more experienced with this tool and willing to help me with these issues, get in touch on discord and I'll add you to the list of helpers. 

# Credits

* @dantarion, main developer
* @bananaken, for helping on twitter and giving tons of insight and knowledge about these games I don't actually play
* @logichole, for labeling a billion commands less than 24 hours after the public release of boxdox-bb
* @labreezy, for labeling half of revelator and updating the parser/rebuilder to bbcf steam version, as well as getting the ball rolling on DBFZ and BBTAG.
* @geo, for helping out @labreezy with BB normal/special inputs

# Shoutouts
* AltimorTASDK for creating Xrd hitbox tools and Xrd Decrypter
* gdkchan for creating an Xrd Revelator decrypter
* asmodean for creating exah3pac
