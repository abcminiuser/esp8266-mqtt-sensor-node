COM_PORT           ?= COM5
COM_BAUD           ?= 115200

ESPTOOL_FLASH_MODE ?= dio 0
ESPTOOL_FLASH_SIZE ?= detect


VPATH              += src/

SRC                 = main.py \
                      config.py \
                      sensors/bmp280.py \
                      sensors/si7021.py

MICROPYTHON_BIN     = vendor/micropython/esp8266-20171101-v1.9.3.bin


ESP_TOOL            = python vendor/esptool/esptool.py
AMPY_TOOL           = python vendor/adafruit-ampy/ampy/cli.py


# Flash application to an ESP8266 over serial already running Micropython
flash: $(SRC:%=%.ampy)

# Flash Micropython to an ESP8266 over serial
bootstrap:
	@echo "Erasing flash..."
	@$(ESP_TOOL) --port $(COM_PORT) --baud $(COM_BAUD) erase_flash

	@echo "Writing flash..."
	@$(ESP_TOOL) --port $(COM_PORT) --baud $(COM_BAUD) write_flash --flash_size=$(ESPTOOL_FLASH_SIZE) -fm $(ESPTOOL_FLASH_MODE) $(MICROPYTHON_BIN)

	@echo "Done, reset board before attempting to flash application."


%.ampy: %
	@echo "Flashing $<..."
	@if [[ "$(dir $@)" != "./" ]]; then \
		$(AMPY_TOOL) --port $(COM_PORT) --baud $(COM_BAUD) put $(dir $<); \
	fi
	@$(AMPY_TOOL) --port $(COM_PORT) --baud $(COM_BAUD) put $< $(@:%.ampy=%)


.PHONY: flash bootstrap
