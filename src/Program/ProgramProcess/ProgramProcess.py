from typing import Dict, List, Optional
import subprocess, signal

from Program.BaseUtils import BaseUtils
# from ProgramConfig import ProgramConfig

FLAG_NAME	=	1 << 0
FLAG_ADD	=	1 << 1

class ProgramProcess(BaseUtils, dict):

	def __applyFunc(self, data, func, flags):
		for key_lv1, value_lv1 in data:
			if flags & FLAG_NAME:
				print(self.BLUE + self.LIGTH + str(key_lv1) + self.END + ":")
			if flags == FLAG_ADD:
				self.addProcess(key_lv1)
			for key_lv2, value_lv2 in value_lv1.items():
				if flags != FLAG_ADD:
					func(value_lv1, key_lv2, value_lv2, key_lv1)
				if flags == FLAG_ADD and key_lv2 != "name":
					self.updateProcess(key_lv1, {key_lv2:value_lv2})

	def printContent(self, data, key, value, nameProcess):
		print(" " + str(key) + " = " + str(value))

	def addProcess(self, key):
		self[key] = {}

	def updateProcess(self, key, value):
		self[key].update(value)

	def createProcess(self):
		None

	def __init__(self, ProgramConfig: dict):
		if not ProgramConfig:
			raise ValueError(self.ERROR + " Null parameter in constructor")
		self.__applyFunc(ProgramConfig.items(), self.printContent, FLAG_ADD)
		self.__applyFunc(self.items(), self.printContent, FLAG_NAME)


