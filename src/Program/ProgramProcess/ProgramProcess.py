from typing import Dict, List, Optional
import subprocess, signal
import os
import time

from Program.BaseUtils import BaseUtils
# from ProgramConfig import ProgramConfig

class ProgramProcess(BaseUtils, dict):
		
	def printContent(self, data):
		for proc, cont in data:
			print(self.BLUE + self.LIGTH + str(proc) + self.END + ":")
			for key, value in cont.items():
				print(" " + str(key) + " = " + str(value))

	def addDataProcess(self, data:dict):
		for proc, cont in data.items():
			self[proc] = cont.copy()
			self[proc].pop("name")

	def startProcess(self, process_name:str):
		if process_name not in self:
			raise ValueError(self.ERROR + " The process name does not exist")
		config = self[process_name]
		
		command = config.get("command", "").split()
		if not command:
			raise ValueError(self.ERROR + " cannot execute process without command")
		
		working_directory = config.get("working_dir", None)
		if working_directory:
			working_directory = os.path.expanduser(working_directory)
		else:
			working_directory = None

		print(working_directory)

		env = os.environ.copy()
		if "env" in config and isinstance(config["env"], dict):
			env.update(config["env"])

		stdout = subprocess.PIPE
		stderr = subprocess.PIPE
		if config.get("stdout", ""):
			stdout = open(os.path.expanduser(config["stdout"]), "a")
		if config.get("stderr", ""):
			stderr = open(os.path.expanduser(config["stderr"]), "a")

		try:
			process = subprocess.Popen(
				command,
				cwd=working_directory,
				env=env,
				stdout=stdout,
				stderr=stderr,
				shell=config.get("shell", False),
				preexec_fn=os.setsid if config.get("umask") else None
			)
			self[process_name]["_process"] = process
			self[process_name]["_pid"] = process.pid
			self[process_name]["_status"] = "running"
			self[process_name]["_start_time"] = time.time() #cambiar por el del parametro solo para prueba
			print(f"{self.GREEN}{self.LIGTH}Process{self.END} '{process_name}' initialized (PID: {process.pid})")

		except Exception as err:
			raise ValueError(self.ERROR + " in process initialization " + process_name + ":" + err)
			

	def stopProcess(self, process_name:str):
		if process_name not in self or "_process" not in self[process_name]:
			raise ValueError(self.ERROR + "Process" + process_name + "it is not running")
		process = self[process_name]["_process"]
		
		try:
			process.terminate()
			try:
				process.wait(timeout=5)
			except:
				process.kill()
				process.wait()
			self[process_name]["_status"] = "stopped"
			self[process_name]["_stop_time"] = time.time() #lo mismo que arriba loco
			print(f"{self.YELLOW} Process {self.END} '{process_name}' stopped")
			return True
		except Exception as err:
			raise ValueError(self.ERROR + " stopping process: " + process_name + ":" + err)

	def __init__(self, ProgramConfig: dict):
		if not ProgramConfig:
			raise ValueError(self.ERROR + " Null parameter in constructor")
		self.addDataProcess(ProgramConfig)
		self.printContent(self.items())
		self.startProcess("ls")
		self.stopProcess("ls")


