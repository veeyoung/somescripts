#!/bin/bash

# Check if there are M3U files in the directory
list=(./*.m3u)
if [ ${#list[@]} -eq 0 ]; then
    echo "No M3U files found in the current directory."
    exit 1
fi

# Display the list of M3U files
length=${#list[@]}
i=1
for file in "${list[@]}"; do
    echo "$i:   $file"
    ((i++))
done

# Prompt the user to enter an index or exit
if [ $length -gt 1 ]; then
    read -p "Enter list index (1-$length) or enter 'q' to exit: " user_input
    # Check if the user wants to exit
    if [ "$user_input" == "q" ]; then
        echo "Exiting the script."
        exit 0
    fi
    # Validate user input
    if ! [[ $user_input =~ ^[0-9]+$ ]] || [ $user_input -lt 1 ] || [ $user_input -gt $length ]; then
        echo "Invalid input. Please enter a valid index or 'q' to exit."
        exit 1
    fi
    i=$user_input
else
    i=1
fi

# Play the selected M3U file using mpv
mpv --script-opts=iptv=1 "${list[$i-1]}"
