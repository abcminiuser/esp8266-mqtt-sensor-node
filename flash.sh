set -e

COM_PORT=COM5
COM_BAUD=115200

function put {
	echo Writing ${1} to ${2}...
	python vendor/ampy/ampy/cli.py --port $COM_PORT --baud $COM_BAUD put $1 $2
}

put src/main.py main.py
put src/config.py config.py
put src/sensors sensors
