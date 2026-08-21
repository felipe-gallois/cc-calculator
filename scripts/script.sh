countries=("RU" "CN")

for country in "${countries[@]}"
do
    { time uv run cccalc "$country" > "centralities_${country}.json" 2> /dev/null; } 2> "timings_${country}.txt"
done
