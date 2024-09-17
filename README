INSTRUCTIONS FOR USE 

1. Depends on python3 (install as per the instructions for your distro).

2. Also needs > pip install requests

3. It is recommended to put the script in its own folder, for saving conversations (mkdir chili).

3b. If you are not using NixOS you can delete the shell.nix file. 

4. You will need to edit the chili.py script:
(a) Add your API key/s
(b) If you want to use the 'balance' function you will need to add your initial credits. Chili.Py can only read your current usage, therefore to know your overall balance it needs to know the total credits that you have put on the account.
(c) Chili.Py comes with a preset number of profiles to use, but you can change these and add more if desired. 

5. The script needs to be executable > chmod +x chili.py

6. Run with ./chili.py

7. For NixOS users: the script needs to run in a nix-shell (so that the requests function cannot alter the nix-store). To run the script on NixOS > cd chili > nix-shell > ./chili.py
