#!/usr/bin/sudo /bin/bash
if [ ! -e "pip.pyz" ]; then
  sudo -u young bash -c "curl -L -O https://bootstrap.pypa.io/pip/pip.pyz"
fi

dependencies="python-filelock python-sympy python-networkx python-pillow python-mpmath python-markupsafe python-jinja"
array=(${dependencies// / })
for var in ${array[@]}
do
  if [ -z "$(pacman -Qs $var)" ]; then
    pacman -S $var --noconfirm
  fi
done

python pip.pyz install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu  --break-system-packages
python pip.pyz cache purge
sudo pacman -Scc --noconfirm