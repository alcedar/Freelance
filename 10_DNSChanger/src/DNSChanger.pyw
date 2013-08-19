from Tkinter import *
from subprocess import *
import ttk

class DNSChanger:
	def __init__(self, root):
		self.configureGUI(root)
		self.clean()
		self.getNetworkInterfaces()

	def log(self, error):
		self._log.insert(END, error)

	def clean(self):
		self._progress["value"] = 0
		self._log.delete(0.0, END)
		root.update()

	def configureGUI(self, root):
		root.title('DNS Changer')
		root.resizable(0,0)
		root.geometry("500x600")

		Label(root, text="Network interfaces:").pack()

		self._listbox = Listbox(root, width=30, height=10)
		self._listbox.pack()

		self._entry1 = Entry(root, width=30)
		self._entry1.insert(0, '8.8.8.8')
		self._entry1.pack()

		self._button1 = Button(root, text="Change DNS", command=self.changeDNSCallback1)
		self._button1.pack()

		self._entry2 = Entry(root, width=30)
		self._entry2.pack()
		self._entry2.insert(0, '172.0.10.1')

		self._button2 = Button(root, text="Change DNS", command=self.changeDNSCallback2)
		self._button2.pack()

		self._log = Text(root, width=120, height=25)
		self._log.pack()

		self._progress = ttk.Progressbar(root, orient ="horizontal",length = 500, mode ="determinate")
		self._progress.pack()
	
	def getNetworkInterfaces(self):
		process = Popen('cmd', shell=True, stdin=PIPE, stdout=PIPE)
		out, err = process.communicate('ipconfig\n')
		self._list = []

		for line in out.split('\n'):
			if line[0] != ' ' and ' adapter ' in line and 'Tunnel ' not in line:
				item = line[line.find('adapter') + len('adapter'):-2].strip() 
				self._listbox.insert(END, item)
				self._list.append(item)
		self._listbox.config(state='disabled')
		self._progress["value"] = 0
		self._progress["maximum"] = len(self._list)

	def changeNetworkInterfacesDNS(self, dns):
		self._button1.config(state='disabled')
		self._button2.config(state='disabled')
		self.clean()
		for i, item in enumerate(self._list):
			command = "netsh interface ip set dnsservers name=\"" + item + "\" static " + dns + "\n"
			process = Popen('cmd', shell=True, stdin=PIPE, stdout=PIPE)
			#out, err = process.communicate('netsh interface ip set dnsservers name=\"Bluetooth Network Connection\" static ' + dns + '\n')
			out, err = process.communicate(command)
			self.log(out)
			self._progress["value"] = i + 1
			root.update()
		self._button1.config(state='normal')
		self._button2.config(state='normal')

	def changeDNSCallback1(self):
		dns = self._entry1.get()
		self.changeNetworkInterfacesDNS(dns)

	def changeDNSCallback2(self):
		dns = self._entry2.get()
		self.changeNetworkInterfacesDNS(dns)

if __name__ == "__main__":
	root= Tk();

	DNSChanger(root)

	root.mainloop()