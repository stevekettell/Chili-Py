
![pie3](https://github.com/user-attachments/assets/2e94f23a-5e32-4321-95d2-146a4773251f)

**WELCOME TO CHILI.PY**
A way to access your LLMs from the terminal (requires API keys).

**FEATURES**

* Works with OpenRouter and OpenAI keys
* Select from multiple models and profiles (all editable)
* Switch between models during chats (-m).
* Start new chats (-n).
* Save chats (-s).
* Keep track of your usage (-u) and balance (-b) (OpenRouter only)
* Fork chats (-f > use -r to return to last fork).


**INSTRUCTIONS FOR USE**

Tested on Linux only. May work on Windows, idk.

1. Depends on python3 (install as per the instructions for your distro).

2. Also needs > pip install requests (in terminal)

3. It is recommended to run the script in its own folder, for saving conversations.

3b. If you are not using NixOS you can delete the shell.nix file. 

4. You will need to edit the chili.py script before running:
(a) Add your API key/s.
(b) To use the 'balance' function you will need to add your initial credits. Chili.Py can only read your current usage, therefore to know your overall balance it needs to know the total credits that you have put on the account (default is 10.00 but obviously you should change this).
(c) Chili.Py comes with a preset number of profiles to use, but you can change these and add more if desired.

5. The script needs to be made executable > chmod +x chili.py

6. Run with ./chili.py

7. For NixOS users: the script needs to run in a nix-shell so that the requests function cannot alter the nix-store. To run the script on NixOS > cd wherever_you_put_it > nix-shell > ./chili.py
