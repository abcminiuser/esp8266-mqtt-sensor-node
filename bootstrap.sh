set -e

COM_PORT=COM5
COM_BAUD=115200

echo "Erasing flash..."
python vendor/esptool/esptool.py --port $COM_PORT --baud $COM_BAUD erase_flash

echo "Writing flash..."
python vendor/esptool/esptool.py --port $COM_PORT --baud $COM_BAUD write_flash --flash_size=detect -fm dio 0 vendor/micropython/esp8266-20171101-v1.9.3.bin
