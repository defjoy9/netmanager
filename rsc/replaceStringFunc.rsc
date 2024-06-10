# Function that replaces all special characters in a string with the '-' character.
# Here it's used to convert date and time to more readable format.
# Example: from jul/16//2018 11:33:22 to jul-16--2018-11-33-22
:global replaceStringFunc do={
    :local textBefore $text
    :local textAfter
    :local znaki {" "="-";"/"="-";":"="-";}

    :for i from=0 to=([:len $textBefore] -1) do={ 
        :local char [:pick $textBefore $i]

        :foreach zly,dobry in=$znaki do={
            :if ($char=$zly) do={
                :set $char $dobry;
            }
        }
        :set textAfter ($textAfter . $char)
    }
    :return $textAfter
}


:global replaceStringFunc do={
    :local textBefore $text
    :local textAfter
    :local znaki {" "="-";"/"="-";":"="-";}

    :for i from=0 to=([:len $textBefore] -1) do={ 
        :local char [:pick $textBefore $i]

        :foreach zly,dobry in=$znaki do={
            :if ($char=$zly) do={
                :set $char $dobry;
            }
        }
        :set textAfter ($textAfter . $char)
    }
    :return $textAfter
}

