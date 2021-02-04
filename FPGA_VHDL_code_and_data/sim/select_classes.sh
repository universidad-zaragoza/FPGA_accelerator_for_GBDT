#!/bin/bash

# $1 --> selected class num
# $2 --> file

# Start and end of the pixels of every class
start=$(grep -n "PIXELS OF CLASS" "$2" | grep " 0$" | cut -d ":" -f 1)
end=$(($(grep -n "wait;" "$2" | cut -d ":" -f 1) - 1))

# Remove the coments for every class
sed -i ''${start}','${end}' s/^--//' "$2"

# Comment every class
sed -i ''${start}','${end}' s/^/--/' "$2"

# Start and end of the pixels of the selected class
start=$(grep -n "PIXELS OF CLASS" "$2" | grep " $1$" | cut -d ":" -f 1)
new_end=$(grep -n "PIXELS OF CLASS" "$2" | grep " $(($1 + 1))$" | cut -d ":" -f 1)
if [ "$new_end" ]
then
    end=$new_end
fi

# Remove the coments for the selected class
sed -i ''${start}','${end}' s/^--//' "$2"

