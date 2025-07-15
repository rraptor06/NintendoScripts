import os

class Settings:
	field_types = {
		"pid": int,
		"nnid": str
	}
	
	def __init__(self, filename=None):
		self.settings = {}
		if filename:
			self.load(filename)
		
	def __getitem__(self, name): 
		return self.settings[name]
	
	def __setitem__(self, name, value):
		if name not in self.field_types:
			raise KeyError("Unknown setting: %s" % name)
		self.settings[name] = self.field_types[name](value)
		
	def copy(self):
		copy = Settings()
		copy.settings = self.settings.copy()
		return copy

	def load(self, filename="config.cfg"):
		config_path = os.path.join(os.path.dirname(__file__), filename)
		with open(config_path, "r", encoding="utf-8") as f:
			linenum = 1
			for line in f:
				line = line.strip()
				if line:
					if "=" in line:
						field, value = line.split("=", 1)
						self[field.strip()] = value.strip()
					else:
						raise ValueError("Syntax error at line %i" % linenum)
				linenum += 1
		return self
