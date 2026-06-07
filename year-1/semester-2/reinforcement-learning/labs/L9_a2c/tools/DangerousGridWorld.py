import gym; gym.logger.set_level(40)
import random, numpy

class GridWorld( gym.Env ):

	def __init__( self, deterministic=False ):

		#numpy.random.seed(1)

		#
		self.map_size = 7
		self.action_space = 4
		self.state_number = self.map_size*self.map_size
		self.observation_space = self.state_number#[ i for i in range(self.state_number) ]
		self.actions = {0: 'L', 1: 'R', 2: 'U', 3: 'D'}

		#
		self.start_state = 0
		self.goal_state = 48
		self.walls = [8, 9, 16, 21, 23, 30, 36, 37] + [10, 17, 24, 31, 38]
		self.death = [6, 13, 20, 27, 34, 41] + [11, 18, 25, 32, 39]
		self.probability = 0.9

		#
		if deterministic: self.probability = 1

		#
		self.robot_state = self.start_state

		#
		self.R = [ -0.1 for i in range( self.state_number ) ]
		for i in self.death: self.R[i] = -1
		self.R[self.goal_state] = 5
		
		#
		self.available_action = {}

		for state in range( self.state_number ):

			self.available_action[state] = [0, 0, 0, 0]
			x, y = self.state_to_pos(state)

			# Check Left
			new_state = self.pos_to_state(x-1, y)
			if new_state == None or new_state in self.walls: self.available_action[state][0] = state
			else: self.available_action[state][0] = self.pos_to_state(x-1, y)

			# Check Right
			new_state = self.pos_to_state(x+1, y)
			if new_state == None or new_state in self.walls: self.available_action[state][1] = state
			else: self.available_action[state][1] = self.pos_to_state(x+1, y)

			# Check Up
			new_state = self.pos_to_state(x, y-1)
			if new_state == None or new_state in self.walls: self.available_action[state][2] = state
			else: self.available_action[state][2] = self.pos_to_state(x, y-1)
			
			# Check Down
			new_state = self.pos_to_state(x, y+1)
			if new_state == None or new_state in self.walls: self.available_action[state][3] = state
			else: self.available_action[state][3] = self.pos_to_state(x, y+1)

			
	def get_full_transition_table( self, state, action ):

		transition_table = [ 0 for _ in range(self.state_number) ]
		possible_actions = sum( [1 if el != None else 0 for el in self.available_action[state]] )
		residual_probability = 1


		transition_table[self.available_action[state][action]] = self.probability
		residual_probability -= self.probability
		possible_actions -= 1
		residual_probability = round(residual_probability / possible_actions, 2)

		for idx, possible_state in enumerate(self.available_action[state]):
			if idx != action: 
				transition_table[possible_state] += residual_probability
			
		return transition_table

		if self.available_action[state][action] != None: 
			transition_table[self.available_action[state][action]] = self.probability
			residual_probability -= self.probability
			possible_actions -= 1

		residual_probability = round(residual_probability / possible_actions, 2)
		for possible_state in self.available_action[state]:
			if possible_state not in [None, self.available_action[state][action]]:
				transition_table[possible_state] = residual_probability

		return transition_table


	def transition_prob( self, state, action, next_state ):

		# 
		if state in self.walls: return 0

		transition_table = self.get_full_transition_table( state, action )

		return transition_table[next_state]


	def sample( self, action, state=None ):

		if state == None: state = self.robot_state
		transition_table = self.get_full_transition_table( state, action )

		if sum(transition_table) != 1:
			r = 1 - sum(transition_table)
			transition_table[ transition_table.index( max(transition_table) )] += r

		next_state = numpy.random.choice(numpy.arange(0, self.state_number), p=transition_table)

		return next_state


	def render( self ):
		
		#
		for i in range( self.state_number ):

			#
			if i in self.walls: print( "[W]", end=" " )
			elif i in self.death: print( "[X]", end=" " )
			elif i == self.goal_state: print( "[G]", end=" " )
			elif i == self.start_state: print( "[S]", end=" " )
			elif i == self.robot_state: print( "[R]", end=" " )
			else: print( "[ ]", end=" " )
			if (i+1) % self.map_size == 0: print()


	def render_policy( self, policy ):

		for i in range( self.state_number ):

			if i in self.walls: print( "[W]", end=" " )
			elif i in self.death: print( "[X]", end=" " )
			elif i == self.goal_state: print( "[G]", end=" " )
			else: print( f" {self.actions[policy[i]]} ", end=" " )
			if (i+1) % self.map_size == 0: print()

	
	def render_values( self, values ):

		for i in range( self.state_number ):

			if i in self.walls: print( " [W] ", end="\t" )
			elif i in self.death: print( " [X] ", end="\t" )
			elif i == self.goal_state: print( " [G] ", end="\t" )
			else: print( f" {round(values[i], 2)} ", end="\t" )
			if (i+1) % self.map_size == 0: print()


	def values_to_policy( self, values ):

		policy = []
		
		for state in range( self.observation_space ):
			max_candidate = -numpy.inf
			max_action = 0
			for action, next_state in enumerate(self.available_action[state]):
				if next_state != state and values[next_state] > max_candidate: 
					max_candidate = values[next_state]
					max_action = action
			policy.append(max_action)

		return policy


	
	def evaluate_policy( self, policy, iteartions=100 ):

		reward_list = []

		for _ in range(iteartions):
			max_step = 100
			self.robot_state = self.start_state
			ep_reward = self.R[self.robot_state]
			while not self.is_terminal( self.robot_state ):
				self.robot_state = self.sample( policy[self.robot_state] )
				ep_reward += self.R[self.robot_state]
				max_step -= 1
				if max_step <= 0: break
			reward_list.append( ep_reward )

		return round(numpy.mean(reward_list), 2) 
			
	
	def is_terminal( self, state ):
		if state in self.death: return True
		if state == self.goal_state: return True
		return False


	def state_to_pos( self, state ):
		return divmod(state, self.map_size)[1], divmod(state, self.map_size)[0]


	def pos_to_state(self, y, x):
		if x not in range(0, self.map_size) or y not in range(0, self.map_size): return None
		return x * self.map_size + y


	def random_initial_state( self ):

		state = numpy.random.randint(0, 48)
		if state not in self.walls and state not in self.death: return state
		return self.random_initial_state()


	def sample_episode( self, policy, max_length=25 ):

		episode = []

		robot_state = self.random_initial_state()

		while True:
			max_length -= 1

			action_probabilities = policy[robot_state]

			if sum(action_probabilities) != 1:
				r = 1 - sum(action_probabilities)
				action_probabilities[ action_probabilities.index( max(action_probabilities) )] += r

			action = numpy.random.choice( numpy.arange(0, self.action_space), p=action_probabilities)
			new_state = self.sample( action, robot_state )
			reward = self.R[new_state]		

			episode.append([robot_state, action, reward])
			robot_state = new_state

			if self.is_terminal(robot_state) or max_length < 0: break

		return episode