# Importamos las clases que se requieren para manejar los agentes (Agent) y su entorno (Model).
# Cada modelo puede contener múltiples agentes.
import random
from mesa import Agent, Model, model

# Debido a que necesitamos que existe un solo agente por celda, elegimos ''SingleGrid''.
from mesa.space import SingleGrid

# Con ''SimultaneousActivation, hacemos que todos los agentes se activen ''al mismo tiempo''.
from mesa.time import SimultaneousActivation

# Haremos uso de ''DataCollector'' para obtener información de cada paso de la simulación.
from mesa.datacollection import DataCollector

# Importamos los siguientes paquetes para el mejor manejo de valores numéricos.
import numpy as np
import pandas as pd
import math

def get_grid(model):
	width = model.agentGrid.width
	height = model.agentGrid.height
	grid = np.zeros( (width,height) )
	for i in range(width):
		for j in range(height):
			grid[i][j] = model.boxesGrid[i][j]
	return grid

class RobotAgent(Agent):
	def __init__(self, unique_id, model):
		super().__init__(unique_id, model)
		self.hasBox = False
		
	def step(self):    
		newPos = self.getNewPosition()
		# Si el robot no va cargando una caja
		if not self.hasBox:
			if (self.isBoxNearby(self.pos[0], self.pos[1])):
				self.hasBox = True
			else:
				self.model.boxesGrid[self.pos[0]][self.pos[1]] = 0
				self.pos = newPos
				self.model.boxesGrid[newPos[0]][newPos[1]] = 7
				self.model.agentMovements += 1
		# Si el robot ya tiene una caja
		else:
			if (self.isStackNearby(self.pos[0], self.pos[1])):
				self.hasBox = False
				self.model.boxesLeft -= 1
			#si no hay una caja cerca avanza
			else:
				self.model.boxesGrid[self.pos[0]][self.pos[1]] = 0
				self.pos = newPos
				self.model.boxesGrid[newPos[0]][newPos[1]] = 7
				self.model.agentMovements += 1

	# Helper para saber si hay alguna caja cerca del agente
	def isBoxNearby(self, x, y):
		if(self.model.validCoor(x+1, y) and self.model.boxesGrid[x+1][y] == 1):
			self.model.boxesGrid[x+1][y] = 0
			return True
		elif(self.model.validCoor(x-1, y) and self.model.boxesGrid[x-1][y] == 1):
			self.model.boxesGrid[x-1][y] = 0
			return True
		elif(self.model.validCoor(x, y+1) and self.model.boxesGrid[x][y+1] == 1):
			self.model.boxesGrid[x][y+1] = 0
			return True
		elif(self.model.validCoor(x, y-1) and self.model.boxesGrid[x][y-1] == 1):
			self.model.boxesGrid[x][y-1] = 0
			return True
		return False

	# Helper para saber si hay algun rack o pila de cajas cerca
	def isStackNearby(self, x, y):
		if(self.model.validCoor(x+1, y) and self.model.boxesGrid[x+1][y] == -1 ):
			self.model.boxesGrid[x+1][y] = 2
			return True
		elif(self.model.validCoor(x-1, y) and self.model.boxesGrid[x-1][y] == -1 ):
			self.model.boxesGrid[x-1][y] = 2
			return True
		elif(self.model.validCoor(x, y+1) and self.model.boxesGrid[x][y+1] == -1 ):
			self.model.boxesGrid[x][y+1] = 2
			return True
		elif(self.model.validCoor(x, y-1) and self.model.boxesGrid[x][y-1] == -1 ):
			self.model.boxesGrid[x][y-1] = 2
			return True
			
		elif(self.model.validCoor(x+1, y) and self.model.boxesGrid[x+1][y] > 1 and self.model.boxesGrid[x+1][y] < 5 ):
			self.model.boxesGrid[x+1][y] += 1
			return True
		elif(self.model.validCoor(x-1, y) and self.model.boxesGrid[x-1][y] > 1 and self.model.boxesGrid[x-1][y] < 5 ):
			self.model.boxesGrid[x-1][y] += 1
			return True
		elif(self.model.validCoor(x, y+1) and self.model.boxesGrid[x][y+1] > 1 and self.model.boxesGrid[x][y+1] < 5 ):
			self.model.boxesGrid[x][y+1] += 1
			return True
		elif(self.model.validCoor(x, y-1) and self.model.boxesGrid[x][y-1] > 1 and self.model.boxesGrid[x][y-1] < 5 ):
			self.model.boxesGrid[x][y-1] += 1
			return True
		return False

	def getNewPosition(self):
		# 0 derecha, 1 izqierda, 2 arriba, 3 abajo
		ways =[0,1,2,3]
		direction = random.choice(ways)
		
		if direction == 0:
			newPos = (self.pos[0]+1,self.pos[1])
		elif  direction == 1:
			newPos = (self.pos[0]-1,self.pos[1])
		elif  direction == 2:
			newPos = (self.pos[0],self.pos[1]+1)
		elif  direction == 3:
			newPos = (self.pos[0],self.pos[1]-1)

		if self.model.validCoor(newPos[0], newPos[1]) and self.model.boxesGrid[newPos[0]][newPos[1]] == 0:
			return newPos

		return self.pos


class BoxModel(Model):
	def __init__(self, width, height, numBoxes, numAgents):
		self.datacollector = DataCollector(model_reporters={"Grid": get_grid})
		self.width = width
		self.height = height
		self.numBoxes = numBoxes
		self.numAgents = numAgents
		self.agentMovements = 0  
		self.boxesGrid = np.zeros((width,height), int)
		self.agentGrid = SingleGrid(width, height, False)
		self.schedule = SimultaneousActivation(self)
		self.racks = math.ceil(self.numBoxes/5)
		self.boxesLeft = self.numBoxes - self.racks

		# Coloca todos los agentes en el modelo
		self.placeObjects()


	def step(self):
		""" Ejecuta un paso de la simulación."""
		self.datacollector.collect(self)
		self.schedule.step()

	def validCoor(self,x,y):
		if x >= 0 and x < self.agentGrid.width and y >= 0 and y < self.agentGrid.height:
			return True
		return False

	def placeObjects(self):
		# Coloca las cajas que servirán como rack para apilar cajas
		rackCounter = self.racks
		while rackCounter:
			posY = random.randint(0, self.height-1)
			posX = random.randint(0, self.width-1)
			if self.boxesGrid[posX][posY] == 0:
				self.boxesGrid[posX][posY] = -1
				rackCounter -= 1
				
		# Coloca las cajas 
		boxesCounter = self.boxesLeft
		while boxesCounter:
			posY = random.randint(0, self.height-1)
			posX = random.randint(0, self.width-1)
			if self.boxesGrid[posX][posY] == 0:
				self.boxesGrid[posX][posY] = 1
				boxesCounter -= 1

		# Coloca los agentes
		agentId = 0
		agentsCounter = self.numAgents
		while agentsCounter:
			posY = random.randint(0, self.height-1)
			posX = random.randint(0, self.width-1)
			if self.boxesGrid[posX][posY] == 0 and self.agentGrid.is_cell_empty((posX, posY)):
				a = RobotAgent(agentId, self)
				agentId += 1
				self.agentGrid.place_agent(a, (posX, posY))
				self.boxesGrid[posX][posY] = 7
				self.schedule.add(a)
				agentsCounter -= 1