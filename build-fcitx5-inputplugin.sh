#!/bin/bash
echo "Enter libQtCore path"
read corePath
qtVer=$(strings $corePath |grep "Qt $(echo $corePath |grep -o '[0-9]' |head -1)" |awk '{print $2}')
qtBasePkgName=$(curl -s "https://archive.archlinux.org/packages/q/qt${qtVer::1}-base/" |grep "$qtVer" |grep -oP '(?<=").*(?=")'|head -1)
work_dir=~/Downloads/build-platforminputcontext
if [ ! -d "$work_dir" ]; then
  mkdir -p $work_dir
fi
git clone https://github.com/fcitx/fcitx5-qt.git $work_dir/fcitx5-qt
mkdir $work_dir/qt-built
wget -P $work_dir "https://archive.archlinux.org/packages/q/qt${qtVer::1}-base/$qtBasePkgName"
tar --use-compress-program=unzstd -xvf "$work_dir/$qtBasePkgName" --directory $work_dir/qt-built
export PATH="$work_dir/qt-built/usr/bin/:$PATH"
export CMAKE_PREFIX_PATH=$work_dir/qt-built
sed -i -e 's/\"Enable Qt 4\" On/\"Enable Qt 4\" Off/' $work_dir/fcitx5-qt/CMakeLists.txt
sed -i -e 's/\"Enable Qt 5\" On/\"Enable Qt 5\" Off/' $work_dir/fcitx5-qt/CMakeLists.txt
sed -i -e 's/\"Enable Qt 6\" On/\"Enable Qt 6\" Off/' $work_dir/fcitx5-qt/CMakeLists.txt
sed -i -e "s/\"Enable Qt ${qtVer::1}\" Off/\"Enable Qt ${qtVer::1}\" On/" $work_dir/fcitx5-qt/CMakeLists.txt
sed -i -e 's/\"Build only plugin\" Off/\"Build only plugin\" On/' $work_dir/fcitx5-qt/CMakeLists.txt
sudo pacman -S cmake extra-cmake-modules --noconfirm
cmake $work_dir/fcitx5-qt/
make -C $work_dir/fcitx5-qt/qt${qtVer::1}/platforminputcontext/
sudo pacman -Rns cmake extra-cmake-modules --noconfirm