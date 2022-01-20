#!/bin/sh

#  compta_cc.sh
#  
#
#  Created by Maël Arveiler on 23/03/2020.
#
# Requires several packages :
#	brew install zenity
#	brew install cliclick
#

date=$(date +%Y_%m_%d_%H%M%S)
ics_file=`zenity --file-selection --title="Sélectionnez le fichier .ics"`

cd ~/Documents/compta_cc
mkdir $date
cd $date

csv_file="$(python3 ../ical2csv_places.py $ics_file)"
calendar="$(python3 ../ical2csv.py $ics_file)"


sort -o $csv_file $csv_file
sort --field-separator=";" -k3,3 -o $calendar $calendar

open -a /Applications/Safari.app "https://www.viamichelin.fr"
sleep 5

#cliclick c:270,10;sleep 0.5
#cliclick dc:300,380;sleep 0.5
#cliclick c:270,10;sleep 0.5
#cliclick dc:300,380;sleep 0.5
#cliclick c:700,500;sleep 0.5


previous=''
previous_dist=''
while read LINE ;do
if [ "$LINE" == "$previous" ]; then
    dist=$previous_dist
elif [ "$LINE" == "" ]; then
    dist=0
else
    departure="189 rue de Begles Bordeaux"
    arrival=${LINE:1}
    arrival=$(echo ${arrival%??})

    osascript -e 'set departure to "'"$departure"'"' -e 'set arrival to "'"$arrival"'"' -e 'tell application "Safari" to set URL of the front document to "https://www.viamichelin.fr/web/Itineraires?departure=" & departure & "&arrival=" & arrival'
    sleep 5
    cliclick c:425,700 w:500 dd:425,700 w:500 dm:440,700 w:500 du:440,700 w:500
    cliclick c:200,10 w:500 dc:200,100
    #cliclick dc:466,791
    #cliclick dc:466,791
    #sleep 2
    #cliclick c:200,15
    #sleep 1
    #cliclick c:200,100
    #cliclick c:200,100
    #sleep 0.5
    dist=$(pbpaste)
fi

previous=$LINE
previous_dist=$dist
echo $dist >> distances.csv
sleep .1
done < $csv_file

sleep 1
osascript 'tell application "Safari" to close front window'


paste -d';' distances.csv $calendar > merged.csv
cp $ics_file ~/Documents/compta_cc/$date
mv $csv_file ~/Documents/compta_cc/$date
mv $calendar ~/Documents/compta_cc/$date

