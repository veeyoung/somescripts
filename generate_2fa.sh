echo -n "please enter secret:"
read secret
code=$(oathtool -b --totp "$secret")
echo "your code is $code"
echo $code | xclip -sel clip
echo "*** Code copied to clipboard too ***"
