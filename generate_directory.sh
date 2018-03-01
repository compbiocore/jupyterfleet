#!/bin/bash

echo "<div id=\"outline-container-orgff25f82\" class=\"outline-2\">"
echo "<table border=\"2\" cellspacing=\"0\" cellpadding=\"6\" rules=\"groups\" frame=\"hsides\">"


echo "<colgroup>"
echo "<col  class=\"org-left\" />"

echo "<col  class=\"org-left\" />"

echo "</colgroup>"
echo "<tbody>"
echo "<tr>"
echo "<td class=\"org-left\">Jupyter Link</td>"
echo "<td class=\"org-left\">Name</td>"
echo "</tr>"

echo "<tr>"
echo "<td class=\"org-left\">&#xa0;</td>"
echo "<td class=\"org-left\">&#xa0;</td>"
echo "</tr>"

getArray() {
    array=() # Create array
    while IFS= read -r line # Read a line
    do
        IP+=("$line") # Append line to the array
    done < "$1"
}
getArray "ips_newline_port.txt"

getArray() {
    array=() # Create array
    while IFS= read -r line # Read a line
    do
        NAME+=("$line") # Append line to the array
    done < "$1"
}
# These 3 lines referred to the specific file format we had for one of our workshop response forms, where the user's full name was the 3rd column
cat "registration_tiny.csv" | cut -d ',' -f3 > "temp.csv" # extract only the name field
tail -n +2 "temp.csv" > cleaned_registration.csv # drop the header row - must use temp file or it deletes everything
rm temp.csv # delete temp file

# "cleaned_registration.csv" is the list of names taken from the Google response form for the workshop or otherwise generated
# Each name should be on its own line, with no header (or uncomment and modify the 'tail -n +2' line above to remove a header)
# It's possible that you'll need to manually edit this file if first and last names are separated initially (I've seen it both in one col and split between two)
# In that case just paste them together
getArray "cleaned_registration.csv"
rm cleaned_registration.csv

NAMEindices=${!NAME[*]}
for i in $NAMEindices; do
 	tempNAME=`echo "${NAME[$i]}" | tr -d '"'`
 	tempIP=`echo "${IP[$i]}" | tr -d '"'`
 	echo "<tr>"
 	echo "<td class=\"org-left\"><a href=\"http://"$tempIP"\">http://"$tempIP"</a></td>"
 	echo "<td class=\"org-left\">"$tempNAME"</td>"
 	echo "</tr>"
done

lengthDIFFERENCE=`expr ${#IP[@]} - ${#NAME[@]}` # compute how many spare IPs there are (there should always be ~5 spare IPs in case an instance dies)
lengthDIFFERENCE=`expr $lengthDIFFERENCE - 1` # account for 0-indexing

for j in `seq 0 $lengthDIFFERENCE`; do
    tempIP=`echo ${IP[${#NAME[@]} + j]}`
    echo "<tr>"
 	echo "<td class=\"org-left\"><a href=\"http://"$tempIP"\">http://"$tempIP"</a></td>"
 	echo "<td class=\"org-left\"><b>"Unassigned"</b></td>"
 	echo "</tr>"
done 

echo "</tr>"
echo "</tbody>"
echo "</table>"
echo "</div>"


