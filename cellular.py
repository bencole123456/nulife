import Tkinter
import random
import math

import numpy as np

from PIL import Image,ImageTk,ImageOps, ImageEnhance, ImageDraw


class App():
	def __init__(self):
	
		self.seed_value = np.random.randint(2 ** 32)
		
		print (self.seed_value)
	
		np.random.seed(self.seed_value)
	
		self.grid_x = 384 * 2
		self.grid_y = 384 * 2
				
		self.display_x = 700
		self.display_y = 700
		
		self.save_images = False

		if self.save_images:	
			try:
				os.makedirs("pics/" + str(self.seed_value))
			except OSError as exc: 
				if exc.errno == errno.EEXIST and os.path.isdir(path):
					pass
	
		
		self.top = Tkinter.Tk()
		self.w = Tkinter.Canvas(self.top, width = self.display_x * 2, height = self.display_y);self.w.pack()
		self.im = Image.new("RGB",(self.grid_x,self.grid_y),"white")
		self.p = ImageTk.PhotoImage(self.im)

		self.im_graph = Image.new("RGB",(5000,1000),"white")
		self.im_graph_draw = ImageDraw.Draw(self.im_graph)
		self.p_graph = ImageTk.PhotoImage(self.im_graph.resize((700,700),Image.ANTIALIAS))

												
		self.timer = None
		self.reset()
		self.bit = self.w.create_image(0,0, image = self.p, anchor=Tkinter.NW)
		self.bit_graph = self.w.create_image(self.display_x,0, image = self.p_graph,anchor=Tkinter.NW)
		self.b = Tkinter.Button(text="Start",command = self.calc_rules);self.b.pack()


	def reset(self):
	
		self.sets = {}
	
		self.generation = 0
		self.last_generation = 0
		
		self.old_rule_count = 0
		
		self.old_sums = None
	
		if self.timer:
			self.top.after_cancel(self.timer)
			self.timer = None
	
		self.grid_and_rules = np.zeros( (self.grid_x,self.grid_y,19), dtype=np.uint8)
		
		d = [0.0,
			 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,
			 0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]	

		do = [1.0,
			 1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,
			 1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]	


		s = self.grid_x / 4 #np.random.randint(6,7)
			 
			 	
		for x in xrange(s,self.grid_x ,s * 2):
			for y in xrange(s,self.grid_y ,s * 2):

				for r in xrange(19):
					d[r] = np.random.random() * do[r]	 
		
				for r in xrange(19):
					self.grid_and_rules[(x - s):(x + s),(y - s):(y + s),r] =  np.random.random((s * 2,s * 2)) < d[r]


		self.color_me()
		

	def calc_rules(self):
	
		for counter in xrange(1):
		
			accum = np.zeros( (self.grid_x,self.grid_y,19), dtype=np.uint8 )
			
			temp = self.grid_and_rules

						
			for x in xrange(1,19):
				temp[:,:,x] *= temp[:,:,0]

			for dy in [-1,0,1]:
				for dx in [-1,0,1]:
		
					left = np.roll(temp,dx,axis = 0)
					up = np.roll(left,dy,axis = 1)
					
					accum += up

			grid = accum[:,:,0]
			
			for x in xrange(1,19):

				temp[:,:,x] = (accum[:,:,x] > 0) & (grid > 0) & (((accum[:,:,x] == (grid )) )| ((temp[:,:,0] == 0)))
						
			on_rules = temp[:,:,1:10]
			off_rules = temp[:,:,10:]
			
			accum2 = np.zeros( (self.grid_x,self.grid_y), dtype=np.uint8 )
									
			for x in xrange(0,9):
				accum2 |= (grid == (on_rules[:,:,x] * (x + 1))) & (temp[:,:,0] == 1) & (grid > 0) 
				accum2 |= ((grid + 1) == (off_rules[:,:,x] * (x + 1))) & (temp[:,:,0] == 0) 
			
			self.grid_and_rules[:,:,0] = accum2
			self.grid_and_rules[:,:,1:10] = on_rules
			self.grid_and_rules[:,:,10:] = off_rules			
									
		self.generation += 1
		
		self.color_me()
		
		self.timer = self.top.after_idle(self.calc_rules)

	def color_me(self):
			
		new_keys = 0
	
		colors = np.zeros( (self.grid_x,self.grid_y,3), dtype=np.uint8 )
				
		lookup = [0,
					10,11,12,1,2,3,
					13,14,15,4,5,6,
					16,17,18,7,8,9]
		
		color_lookups = [tuple([0,0,0])] * 19

		for x in xrange(1,7):
			colors[:,:,1] += self.grid_and_rules[:,:,lookup[x]] * 2 ** (x )
			color_lookups[lookup[x]] = tuple([0,42 * (x),0])

		for x in xrange(7,13):
			colors[:,:,2] += self.grid_and_rules[:,:,lookup[x]] * 2 ** (x - 6)
			color_lookups[lookup[x]] = tuple([0,0,42 * (x - 6)])

		for x in xrange(13,19):			
			colors[:,:,0] += self.grid_and_rules[:,:,lookup[x]] * 2 ** (x - 12)
			color_lookups[lookup[x]] = tuple([42 * (x - 12),0,0])
				
				
		colors[:,:,0] *= self.grid_and_rules[:,:,0] + 1
		colors[:,:,1] *= self.grid_and_rules[:,:,0] + 1
		colors[:,:,2] *= self.grid_and_rules[:,:,0] + 1		
		
		if self.generation % 50 == 0:

			rule_sets = self.grid_and_rules[:,:]		
			rule_sets = rule_sets.reshape(-1,rule_sets.shape[2])
			unique_rule_sets = np.unique(rule_sets.view(rule_sets.dtype.descr * rule_sets.shape[1]))
		
			sums = [0] * 19
		
			if self.old_rule_count > 0:	
			
				gen_diff = self.generation - self.last_generation
				
				gen_mod = self.generation % 5000
				
				if gen_mod < (self.last_generation % 5000):
					self.im_graph_draw.rectangle((0,0,5000,1000),fill="white")
				
				self.im_graph_draw.line((gen_mod - gen_diff, 1000 - self.old_rule_count,gen_mod,1000 - len(unique_rule_sets)),fill="purple")

			
				for x in xrange(19):
					sums[x] = (np.sum(self.grid_and_rules[:,:,x]) * 1000) / (self.grid_x * self.grid_y)
										
					self.im_graph_draw.line((gen_mod - gen_diff, 1005 - self.old_sums[x] ,gen_mod,1005 - sums[x]),fill=color_lookups[x])
			else:
				for x in xrange(19):
					sums[x] = (np.sum(self.grid_and_rules[:,:,x]) * 1000) / (self.grid_x * self.grid_y)
				
			self.old_rule_count = len(unique_rule_sets)
			
			self.old_sums = sums
		
			self.last_generation = self.generation
		
			self.p_graph = ImageTk.PhotoImage(self.im_graph.resize((700,700),Image.ANTIALIAS))

			self.bit_graph = self.w.create_image(self.display_x,0, image = self.p_graph,anchor=Tkinter.NW)

		
		temp = self.im

		colors[(colors == 0).all(axis = -1)] = [0,0,0]

		self.im = Image.fromarray(colors)
									
		temp2 = Image.blend(temp,self.im,1.0)
				
		self.p = ImageTk.PhotoImage(temp2.resize((self.display_x,self.display_y),Image.ANTIALIAS))

		self.im = Image.blend(temp,self.im,1.0)
				
		self.bit = self.w.create_image(0,0, image = self.p, anchor=Tkinter.NW)
		
		if self.save_images and self.generation % 5 == 0:								
			self.im.resize((384*2,384*2),Image.ANTIALIAS).save("pics/" + str(self.seed_value) + "image." + str(self.generation/5) + ".jpeg")

app=App()
app.top.mainloop()

