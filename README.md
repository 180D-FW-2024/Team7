# Team7

[Panda3d Tutorial](https://youtube.com/playlist?list=PL1P11yPQAo7oEAGuPcqMnn9ZWHLWP3-Lc&si=_vDtTTLGbpZNZa94)

Basic Guidelines:

1. Run python black linter on all scripts before submitting a PR.
2. Using glb model file formats. See https://docs.panda3d.org/1.10/cpp/pipeline/converting-from-blender#option-2-exporting-to-gltf. Use gltf pbr rendering.
3. Consistent variable naming where possible.
4. We will work on abstracting posititioning relationships for ease of debugging.
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





