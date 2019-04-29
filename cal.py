from sys import argv
from datetime import date
from re import compile

DAYS_WAIT = 14
WARN_NOTE = 60

#formato para strings (caja negra (Y), retorna str con colores y atributos (linux))
def fstr(src,att='n',font='default',back='default',end=True):
	F = {'n':'0','b':'1','s':'2','i':'3','u':'4','r':'7','h':'8','c':'9'}
	C = {'black':30,'red':31,'green':32,'yellow':33,'blue':34,'magenta':35,
		 'cyan':36,'white':37,'default':39}
	try:
	    pre = "\033[" + ';'.join(map(lambda f: F[f], att))
	    pre += ';' + str(C[font]) + ';' + str(C[back]+10) + 'm'
	except:
	    pre = ''
	return pre + str(src) + '\033[0m'*end

class Calendar:
	def __init__(self, nf):
		dates = []
		with open(nf) as f:
			for l in f:
				#evita las lineas-comentarios (empiezan con '#') y lineas vacias (solo con '\n')
				if l[0] == '#' or len(l) == 1: continue
				dy,nm,ev = l.strip().split(',')
				dates.append(tuple((nm, dy.split('/'), ev)))
			dates.sort(key=lambda (n,d,e): int(d[0])*40 + int(d[1]))
		#dates = lista => {nombre,fecha,resultado}
		self.dates = dates

	def __len__(self):
		return len(self.dates)

	def filt_reg(self, regex):
		regex = compile(regex)
		self.dates = filter(lambda x: regex.search(x[0]), self.dates)
		return self.dates

	def filt_day(self, days):
		trans = {'Mon':'lu', 'Tue':'ma', 'Wed': 'mi', 'Thu': 'ju',
				 'Fri':'vi', 'Sat':'sa', 'Sun':'do'}
		days = days.split(',')
		self.dates = filter(lambda x: trans[date(2019, int(x[1][0]), int(x[1][1])).strftime('%a')] in days, self.dates)
		return self.dates

	def filt_con(self, cont):
		today = str(date.today()).split('-')[1:]
		for i,(nm,(m,d),ev) in enumerate(self.dates):
			wait = (int(m)*30 + int(d)) - (int(today[0])*30 + int(today[1]))
			if wait >= 0:
				self.dates = self.dates[i : min(i + int(cont),len(self.dates))]
				return self.dates

	def show(self, regex=None):
		finish = 0
		today = str(date.today()).split('-')[1:]
		for nm,(m,d),ev in self.dates:
			#dias que quedan para el evento
			wait = (int(m)*30 + int(d)) - (int(today[0])*30 + int(today[1]))

			#si el evento ya paso
			if wait <= 0:
				dy = fstr(m+'/'+d, 'c')
				finish += 1
				if ev == '': ev = '??'
				else: ev = fstr(ev, 'n', 'green' if int(ev) >= WARN_NOTE else 'red')
			#si quedan "pocos" dias
			elif wait < DAYS_WAIT:
				dy = fstr(m+'/'+d, 'n','red')
			#si quedan "varios" dias
			elif wait >= DAYS_WAIT:
				dy = fstr(m+'/'+d, 'n','green')
			print "{0}\t{1}\t{2}".format(nm, dy, ev)

		if len(self): print fstr("+-----> " + str(100*finish/len(self)) + "% completed", 'b')
		else: print fstr("not found!", 'b', 'red')

#archivo
cal = Calendar(argv[-1])

#filtrar por dias
if '-d' in argv:
	cal.filt_day(argv[argv.index('-d') + 1])

#filtrar por regex
if '-r' in argv:
	cal.filt_reg(argv[argv.index('-r') + 1])

#filtrar por cantidad
if '-c' in argv:
	cal.filt_con(argv[argv.index('-c') + 1])

#mostrar
cal.show()
