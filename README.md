
# Team7

## Installation

1. Copy the script bowling-setup.sh to your machine
2. Run the following commands: 
```
chmod +x bowling-setup.sh
./bowling-setup.sh
source ~/.zshrc
```

## How To Play

Simply run the command ```play-bowling``` from any directory.

See the user manual here TODO insert user manual

## Contribution

1. Run python black linter on all scripts before submitting a PR.
2. Using glb model file formats. See https://docs.panda3d.org/1.10/cpp/pipeline/converting-from-blender#option-2-exporting-to-gltf. Use gltf pbr rendering.
3. Consistent variable naming where possible.
4. We will work on abstracting positioning relationships for ease of debugging.
5. For submitting a PR, complete the following steps

FOR MERGING MAIN<--YOUR_BRANCH

git add/commit files in your branch  
git stash (anything you don't want to commit)

git checkout main    
git pull  
git checkout your-branch   
git merge main (to resolve as many conflicts locally) this does YOUR_LOCAL <-- MAIN (you should do this often)   
git add/commit any more files you need to   
git push

SUBMIT PR ON GITHUB MAIN <-- YOUR_BRANCH

PR will be reviewed together.

