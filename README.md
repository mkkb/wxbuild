Cloning:

    git clone --branch <branchname> https://github.com/mkkb/wxbuild.git



 

Creating environment:

    conda env create -f environment.yml


To make vispy compatible:

    Made a fork:
        https://docs.github.com/en/get-started/quickstart/fork-a-repo

    Updated branch, commit corresponding to the 0.7.3 tag
        git checkout -b my-branch 3b5915a21a


Other cmds tending to be forgotten:
    
    conda env remove -n ENV_NAME
    conda env create -f environment.yml

Other usefull resources:

    https://stackoverflow.com/questions/59864503/direct-link-to-github-in-requirements-txt-while-using-conda