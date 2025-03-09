#!/bin/zsh

# This script installs a simple bowling game! Have fun!

# Ensure user running macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "This application is only supported on macOS. Exiting."
    exit 1
fi

# If pyenv installed, just install the necessary python version
if [[ -n "$(pyenv --version)" ]]; then
    echo "Pyenv is already installed."

    if [[ -z "$(pyenv versions | grep "3.8.10")" ]]; then
        pyenv install 3.8.10
    fi

    curl -L https://github.com/180D-FW-2024/Team7/archive/main.zip -o bowling.zip
    unzip bowling.zip
    rm bowling.zip
    mv Team7-main bowling
    cd bowling

    pyenv local 3.8.10
    python -m venv env
    source env/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate

    if [[ -z "$(cat ~/.zshrc | grep "play-bowling")" ]]; then
        echo "alias play-bowling='$PWD/play.sh'" >> ~/.zshrc
    fi

    echo "\nInstallation complete: Run 'play-bowling' to play.\n"

    exit
fi

# Else we need to install pyenv

# Ensure Homebrew is installed
if [[ -z "$(command -v brew)" ]]; then
    echo "Homebrew is not installed. Please install it first.\nVisit https://brew.sh"
    exit 1
fi

# Install pyenv
brew update
brew install pyenv

# Ensure zsh is default shell
if [[ "$SHELL" != *"zsh" ]]
    echo "Error: Your default shell must be Zsh. Please change your default shell to Zsh and try again."
    exit 1
fi

# For interactive shells
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init - zsh)"' >> ~/.zshrc
source ~/.zshrc

# For non-interactive login shells
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zprofile
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zprofile
echo 'eval "$(pyenv init - zsh)"' >> ~/.zprofile
source ~/.zprofile

# Ensure pyenv was installed correctly
if [[ -z "$(pyenv --version)" ]]; then
    echo "Pyenv did not install properly. Exiting."
    exit 1
fi

pyenv install 3.8.10

curl -L https://github.com/180D-FW-2024/Team7/archive/main.zip -o bowling.zip
unzip bowling.zip
rm bowling.zip
mv Team7-main bowling
cd bowling

pyenv local 3.8.10
python -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

if [[ -z "$(cat ~/.zshrc | grep "play-bowling")" ]]; then
    echo "alias play-bowling='$PWD/play.sh'" >> ~/.zshrc
fi

echo "\nInstallation complete: Run 'play-bowling' to play.\n"
