SHELL := /bin/bash
################################################################################
#                               BOLD COLORS                                    #
################################################################################

END = \033[m
RED = \033[31m
GREEN = \033[32m
YELLOW = \033[33m
BLUE = \033[34m
PURPLE = \033[35m
CIAN = \033[36m

################################################################################
#  FONT                                                                        #
################################################################################

LIGTH = \033[1m
DARK = \033[2m
ITALIC = \033[3m

################################################################################
#                               VARIABLES                                      #
################################################################################
CONFIG_DIR = ../configs
PYTHON = python
APP_NAME = taskmaster

CONFIG_FILES = $(wildcard $(CONFIG_DIR)/*.yaml)
CONFIG_NAMES = $(notdir $(basename $(CONFIG_FILES)))

.DEFAULT_GOAL := help

SHOW_CONFIGS = \
	printf "$(BLUE)$(LIGTH)Available configurations:$(END)\n"; \
	for config in $(CONFIG_NAMES); do \
		echo "  $$config"; \
	done

help:
	printf "$(BLUE)$(LIGTH)Available targets:$(END)\n"
	echo "  make test-<config>     # Run specific test (e.g.: make test-ls_config)"
	echo "  make list              # List available configurations"
	echo "  make clean             # Clean up residual files"
	echo ""
	$(SHOW_CONFIGS)
list:
	$(SHOW_CONFIGS)

test-%:
	@if [ -f "$(CONFIG_DIR)/$*.yaml" ]; then \
		printf "$(BLUE)$(LIGTH)Running test for:$(END) $*"; \
		$(PYTHON) main.py -c "$(CONFIG_DIR)/$*.yaml"; \
	else \
		printf "$(RED)$(LIGTH)[ERROR]$(END) Configuration $*.yaml not found in $(CONFIG_DIR)\n"; \
		$(SHOW_CONFIGS); \
	fi
update:
	@pid=$$(ps -ef | grep "[t]askmaster main.py" | awk '{print $$2}' | head -n 1); \
	if [ -n "$$pid" ]; then \
		printf "$(BLUE)$(LIGTH)Sending SIGHUP to process $$pid$ $(END)\n"; \
		kill -1 $$pid; \
	else \
		printf "$(RED)$(LIGTH)[ERROR]$(END) No taskmaster main.py process found\n"; \
	fi

clear:
	printf "$(BLUE)$(LIGTH)files deleted from test worker$(END)\n"
	rm -rf fail_time_out* fails* success* takes_too_long_to_die* work*

.PHONY: help list test update clear
.SILENT: