# -*- coding: utf-8 -*-
"""NavAgents.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NjaKAXOSnUF4WLebwDlQTLzO6j-q0qNI
"""

import numpy as np

from qnetworks import BaseQNetwork
from qnetworks import DuelingQNetwork
from qnetworks import OldQNetwork

import random
from replays import PrioritizedExperienceReplay
from replays import ReplayBuffer

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


class OldAgent():
    
    def __init__(self, state_size: int, action_size: int, seed: int, hypers: dict, device: torch.device):
        #Basic details
        self.state_size = state_size
        self.action_size = action_size
        self.seed = random.seed(seed)

        self.batch_size    = hypers['BATCH_SIZE']
        self.buffer_size   = hypers['BUFFER_SIZE']
        self.gamma         = hypers['GAMMA']
        self.learning_rate = hypers['LR']
        self.tau           = hypers['TAU']
        self.update_every  = hypers['UPDATE_EVERY']
        
        self.device = device
        
        #Qnetworks: primary, target, and optimizer
        self.qnetwork_primary = OldQNetwork(state_size, action_size, seed).to(device)
        self.qnetwork_target = OldQNetwork(state_size, action_size, seed).to(device)
        self.optimizer = optim.Adam(self.qnetwork_primary.parameters(), lr=self.learning_rate)
        
        #Replay buffer
        self.memory = ReplayBuffer(action_size, self.buffer_size, self.batch_size, seed, device)
        # Initialize time step (for updating every UPDATE_EVERY steps)
        self.t_step = 0
        
    def step(self, state: np.array, action: int, reward: float, next_state: np.array, done: bool) -> None:
        #Add to the memory buffer
        self.memory.add(state, action, reward, next_state, done)
        
        # Learn every UPDATE_EVERY time steps.
        self.t_step = (self.t_step + 1) % self.update_every
        if self.t_step == 0:
            # If enough samples are available in memory, get random subset and learn
            if len(self.memory) > self.batch_size:
                experiences = self.memory.sample()
                self.learn(experiences)
                
    def act(self, state: np.array, eps: float) -> int:
        """Returns actions for given state as per current policy"""
        state = torch.from_numpy(state).float().unsqueeze(0).to(self.device)
        self.qnetwork_primary.eval()
        with torch.no_grad():
            action_values = self.qnetwork_primary(state)
        self.qnetwork_primary.train()
        
        #Epsilon-greedy action selection -- probably swap for softmax-greedy at some point
        if random.random() > eps:
            return np.argmax(action_values.cpu().data.numpy())
        return random.choice(np.arange(self.action_size))
    
    def learn(self, experiences: tuple) -> None:
        """The core of the algorithm, the actual updating of the network parameters"""
        states, actions, rewards, next_states, dones = experiences
    
        #Select next state actions using the *primary* network
        argmax_a_q_sp = self.qnetwork_primary(next_states).max(1)[1]
        #Get the next state action values using the *target* network
        q_sp = self.qnetwork_target(next_states).detach()
        #Index the q-values of the target network using the indices chosen by the primary,
        #so: primary network chooses action, target network evaluates action --> DDQN
        max_a_q_sp = q_sp[np.arange(self.batch_size), argmax_a_q_sp].unsqueeze(1) * (1 - dones)
        #Compute the target values
        target_q_sa = rewards + self.gamma * max_a_q_sp
        #Get the actual action values
        q_sa = self.qnetwork_primary(states).gather(1, actions)
        
        # Compute loss
        loss = F.mse_loss(q_sa, target_q_sa)
        # Minimize the loss
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # ------------------- update target network ------------------- #
        self.soft_update(self.qnetwork_primary, self.qnetwork_target)
        
    def soft_update(self, primary: OldQNetwork, secondary: OldQNetwork) -> None:
        """Soft update model parameters.
        θ_target = τ*θ_local + (1 - τ)*θ_target
        """
        for target_param, local_param in zip(secondary.parameters(), primary.parameters()):
            target_param.data.copy_(self.tau * local_param.data + (1.0 - self.tau) * target_param.data)

#BaseAgent: DDQN using the BaseQNetwork and uniform experience replay
class BaseAgent():
    def __init__(self, state_size: int, action_size: int, seed: int, hypers: dict, device: torch.device):
        #Basic details
        self.state_size = state_size
        self.action_size = action_size
        self.seed = random.seed(seed)
        
        self.batch_size    = hypers['BATCH_SIZE']
        self.buffer_size   = hypers['BUFFER_SIZE']
        self.gamma         = hypers['GAMMA']
        self.learning_rate = hypers['LR']
        self.tau           = hypers['TAU']
        self.update_every  = hypers['UPDATE_EVERY']
        
        self.device = device
        
        #Qnetworks: primary, target, and optimizer
        self.qnetwork_primary = BaseQNetwork(state_size, action_size, seed).to(device)
        self.qnetwork_target = BaseQNetwork(state_size, action_size, seed).to(device)
        self.optimizer = optim.Adam(self.qnetwork_primary.parameters(), lr=self.learning_rate)
        
        #Replay buffer
        self.memory = ReplayBuffer(action_size, self.buffer_size, self.batch_size, seed, device)
        # Initialize time step (for updating every UPDATE_EVERY steps)
        self.t_step = 0
        
    def step(self, state: np.array, action: int, reward: float, next_state: np.array, done: bool) -> None:
        #Add to the memory buffer
        self.memory.add(state, action, reward, next_state, done)
        
        # Learn every UPDATE_EVERY time steps.
        self.t_step = (self.t_step + 1) % self.update_every
        if self.t_step == 0:
            # If enough samples are available in memory, get random subset and learn
            if len(self.memory) > self.batch_size:
                experiences = self.memory.sample()
                self.learn(experiences)
                
    def act(self, state: np.array, eps: float) -> int:
        """Returns actions for given state as per current policy"""
        state = torch.from_numpy(state).float().unsqueeze(0).to(self.device)
        self.qnetwork_primary.eval()
        with torch.no_grad():
            action_values = self.qnetwork_primary(state)
        self.qnetwork_primary.train()
        
        #Epsilon-greedy action selection 
        if random.random() > eps:
            return np.argmax(action_values.cpu().data.numpy())
        return random.choice(np.arange(self.action_size))
    
    def learn(self, experiences: tuple) -> None:
        """The core of the algorithm, the actual updating of the network parameters"""
        states, actions, rewards, next_states, dones = experiences
    
        #Select next state actions using the *primary* network
        argmax_a_q_sp = self.qnetwork_primary(next_states).max(1)[1]
        #Get the next state action values using the *target* network
        q_sp = self.qnetwork_target(next_states).detach()
        #Index the q-values of the target network using the indices chosen by the primary,
        #so: primary network chooses action, target network evaluates action --> DDQN
        max_a_q_sp = q_sp[np.arange(self.batch_size), argmax_a_q_sp].unsqueeze(1) * (1 - dones)
        #Compute the target values
        target_q_sa = rewards + self.gamma * max_a_q_sp
        #Get the actual action values
        q_sa = self.qnetwork_primary(states).gather(1, actions)
        
        # Compute loss
        loss = F.mse_loss(q_sa, target_q_sa)
        # Minimize the loss
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # ------------------- update target network ------------------- #
        self.soft_update(self.qnetwork_primary, self.qnetwork_target)
        
    def soft_update(self, primary: BaseQNetwork, secondary: BaseQNetwork) -> None:
        """Soft update model parameters.
        θ_target = τ*θ_local + (1 - τ)*θ_target
        """
        for target_param, local_param in zip(secondary.parameters(), primary.parameters()):
            target_param.data.copy_(self.tau * local_param.data + (1.0 - self.tau) * target_param.data)

#Basic DDQN Agent with Prioritized Experience Replay
class PriorityAgent():
    def __init__(self, state_size: int, action_size: int, seed: int, hypers: dict, device: torch.device):
        #Basic details
        self.state_size = state_size
        self.action_size = action_size
        self.seed = random.seed(seed)
        
        self.alpha         = hypers['ALPHA']
        self.beta          = hypers['BETA']
        self.batch_size    = hypers['BATCH_SIZE']
        self.buffer_size   = hypers['BUFFER_SIZE']
        self.gamma         = hypers['GAMMA']
        self.learning_rate = hypers['LR']
        self.tau           = hypers['TAU']
        self.update_every  = hypers['UPDATE_EVERY']
        
        self.device = device
        
        #Qnetworks: primary, target, and optimizer
        self.qnetwork_primary = BaseQNetwork(state_size, action_size, seed).to(device)
        self.qnetwork_target = BaseQNetwork(state_size, action_size, seed).to(device)
        self.optimizer = optim.Adam(self.qnetwork_primary.parameters(), lr=self.learning_rate)
        
        #Replay buffer
        self.memory = PrioritizedExperienceReplay(action_size, self.buffer_size, self.batch_size, self.alpha, seed, device)
        # Initialize time step (for updating every UPDATE_EVERY steps)
        self.t_step = 0
        
    def step(self, state: np.array, action: int, reward: float, next_state: np.array, done: bool) -> None:
        #Determine the TD_error to save for learning
        state = torch.from_numpy(state).float().to(self.device)
        action = torch.tensor(action, dtype=torch.long).to(self.device)
        next_state = torch.from_numpy(next_state).float().to(self.device)
        
        #Select next state actions using the *primary* network
        argmax_a_q_sp = self.qnetwork_primary(next_state).argmax()
        #Get the next state action values using the *target* network
        q_sp = self.qnetwork_target(next_state).detach()
        
        #Index the q-values of the target network using the indices chosen by the primary,
        #so: primary network chooses action, target network evaluates action --> DDQN
        max_a_q_sp = q_sp[argmax_a_q_sp] * (1 - done)
        #Compute the target values
        target_q_sa = reward + self.gamma * max_a_q_sp
        #Get the actual action values
        q_sa = self.qnetwork_primary(state)[action]
        
        # Compute the TD_error
        TD_error = target_q_sa - q_sa
        
        #Add to the memory buffer
        self.memory.add(state, action, reward, next_state, done, torch.abs(TD_error))
        
        # Learn every UPDATE_EVERY time steps.
        self.t_step = (self.t_step + 1) % self.update_every
        if self.t_step == 0:
            # If enough samples are available in memory, get random subset and learn
            if len(self.memory) > self.batch_size:
                indices, probabilities, experiences = self.memory.sample()
                self.learn(indices, probabilities, experiences)
                
    def act(self, state: np.array, eps: float) -> int:
        """Returns actions for given state as per current policy"""
        state = torch.from_numpy(state).float().unsqueeze(0).to(self.device)
        self.qnetwork_primary.eval()
        with torch.no_grad():
            action_values = self.qnetwork_primary(state)
        self.qnetwork_primary.train()
        
        #Epsilon-greedy action selection 
        if random.random() > eps:
            return np.argmax(action_values.cpu().data.numpy())
        return random.choice(np.arange(self.action_size))
                
    def learn(self, indices: np.array, probabilities: torch.tensor, experiences: tuple) -> None:
        """The core of the algorithm, the actual updating of the network parameters"""
        
        states, actions, rewards, next_states, dones = experiences
    
        #Select next state actions using the *primary* network
        argmax_a_q_sp = self.qnetwork_primary(next_states).max(1)[1]
        #Get the next state action values using the *target* network
        q_sp = self.qnetwork_target(next_states).detach()
        #Index the q-values of the target network using the indices chosen by the primary,
        #so: primary network chooses action, target network evaluates action --> DDQN
        max_a_q_sp = q_sp[np.arange(self.batch_size), argmax_a_q_sp].unsqueeze(1) * (1 - dones)
        #Compute the target values
        target_q_sa = rewards + self.gamma * max_a_q_sp
        #Get the actual action values
        q_sa = self.qnetwork_primary(states).gather(1, actions)
        
        # Compute the new TD_errors
        TD_errors = target_q_sa - q_sa
        
        # Update the TD_errors for the sampled experiences
        new_priorities = torch.abs(TD_errors)
        self.memory.update(indices, new_priorities)
        
        # Compute Importance Sampling weights
        weights_is = torch.pow((self.buffer_size * probabilities), -self.beta)
        norm_weights = (weights_is/weights_is.max()).to(self.device)
        
        #Normalize actual & target values
        normed_q_sa = norm_weights * q_sa
        normed_target = norm_weights * target_q_sa
        
        # Compute loss
        loss = F.mse_loss(normed_q_sa, normed_target)
        
        # Minimize the loss
        self.optimizer.zero_grad()
        loss.backward()
        #Clip gradients if necessary, not yet active
        #torch.nn.utils.clip_grad_norm_(self.qnetwork_primary.parameters(), self.max_gradient_norm)
        self.optimizer.step()
        
        # ------------------- update target network ------------------- #
        self.soft_update(self.qnetwork_primary, self.qnetwork_target)
        
    def soft_update(self, primary: BaseQNetwork, secondary: BaseQNetwork) -> None:
        """Soft update model parameters.
        θ_target = τ*θ_local + (1 - τ)*θ_target
        """
        for target_param, local_param in zip(secondary.parameters(), primary.parameters()):
            target_param.data.copy_(self.tau * local_param.data + (1.0 - self.tau) * target_param.data)
            
#DuelingAgent: DDQN using the DuelingQNetwork and uniform experience replay
class DuelingAgent():
    def __init__(self, state_size: int, action_size: int, seed: int, hypers: dict, device: torch.device):
        #Basic details
        self.state_size = state_size
        self.action_size = action_size
        self.seed = random.seed(seed)
        
        self.batch_size    = hypers['BATCH_SIZE']
        self.buffer_size   = hypers['BUFFER_SIZE']
        self.gamma         = hypers['GAMMA']
        self.learning_rate = hypers['LR']
        self.tau           = hypers['TAU']
        self.update_every  = hypers['UPDATE_EVERY']
        
        self.device = device
        
        #Qnetworks: primary, target, and optimizer
        self.qnetwork_primary = DuelingQNetwork(state_size, action_size, seed).to(device)
        self.qnetwork_target = DuelingQNetwork(state_size, action_size, seed).to(device)
        self.optimizer = optim.Adam(self.qnetwork_primary.parameters(), lr=self.learning_rate)
        
        #Replay buffer
        self.memory = ReplayBuffer(action_size, self.buffer_size, self.batch_size, seed, device)
        # Initialize time step (for updating every UPDATE_EVERY steps)
        self.t_step = 0
        
    def step(self, state: np.array, action: int, reward: float, next_state: np.array, done: bool) -> None:
        #Add to the memory buffer
        self.memory.add(state, action, reward, next_state, done)
        
        # Learn every UPDATE_EVERY time steps.
        self.t_step = (self.t_step + 1) % self.update_every
        if self.t_step == 0:
            # If enough samples are available in memory, get random subset and learn
            if len(self.memory) > self.batch_size:
                experiences = self.memory.sample()
                self.learn(experiences)
                
    def act(self, state: np.array, eps: float) -> int:
        """Returns actions for given state as per current policy"""
        state = torch.from_numpy(state).float().unsqueeze(0).to(self.device)
        self.qnetwork_primary.eval()
        with torch.no_grad():
            action_values = self.qnetwork_primary(state)
        self.qnetwork_primary.train()
        
        #Epsilon-greedy action selection 
        if random.random() > eps:
            return np.argmax(action_values.cpu().data.numpy())
        return random.choice(np.arange(self.action_size))
    
    def learn(self, experiences: tuple) -> None:
        """The core of the algorithm, the actual updating of the network parameters"""
        states, actions, rewards, next_states, dones = experiences
    
        #Select next state actions using the *primary* network
        argmax_a_q_sp = self.qnetwork_primary(next_states).max(1)[1]
        #Get the next state action values using the *target* network
        q_sp = self.qnetwork_target(next_states).detach()
        #Index the q-values of the target network using the indices chosen by the primary,
        #so: primary network chooses action, target network evaluates action --> DDQN
        max_a_q_sp = q_sp[np.arange(self.batch_size), argmax_a_q_sp].unsqueeze(1) * (1 - dones)
        #Compute the target values
        target_q_sa = rewards + self.gamma * max_a_q_sp
        #Get the actual action values
        q_sa = self.qnetwork_primary(states).gather(1, actions)
        
        # Compute loss
        loss = F.mse_loss(q_sa, target_q_sa)
        # Minimize the loss
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # ------------------- update target network ------------------- #
        self.soft_update(self.qnetwork_primary, self.qnetwork_target)
        
    def soft_update(self, primary: DuelingQNetwork, secondary: DuelingQNetwork) -> None:
        """Soft update model parameters.
        θ_target = τ*θ_local + (1 - τ)*θ_target
        """
        for target_param, local_param in zip(secondary.parameters(), primary.parameters()):
            target_param.data.copy_(self.tau * local_param.data + (1.0 - self.tau) * target_param.data)
            
#Dueling DDQN Agent with Prioritized Experience Replay
class DuelingPriorityAgent():
    def __init__(self, state_size: int, action_size: int, seed: int, hypers: dict, device: torch.device):
        #Basic details
        self.state_size = state_size
        self.action_size = action_size
        self.seed = random.seed(seed)
        
        self.alpha         = hypers['ALPHA']
        self.beta          = hypers['BETA']
        self.batch_size    = hypers['BATCH_SIZE']
        self.buffer_size   = hypers['BUFFER_SIZE']
        self.gamma         = hypers['GAMMA']
        self.learning_rate = hypers['LR']
        self.tau           = hypers['TAU']
        self.update_every  = hypers['UPDATE_EVERY']
        
        self.device = device
        
        #Qnetworks: primary, target, and optimizer
        self.qnetwork_primary = DuelingQNetwork(state_size, action_size, seed).to(device)
        self.qnetwork_target = DuelingQNetwork(state_size, action_size, seed).to(device)
        self.optimizer = optim.Adam(self.qnetwork_primary.parameters(), lr=self.learning_rate)
        
        #Replay buffer
        self.memory = PrioritizedExperienceReplay(action_size, self.buffer_size, self.batch_size, self.alpha, seed, device)
        # Initialize time step (for updating every UPDATE_EVERY steps)
        self.t_step = 0
        
    def step(self, state: np.array, action: int, reward: float, next_state: np.array, done: bool) -> None:
        #Determine the TD_error to save for learning
        state = torch.from_numpy(state).float().to(self.device)
        action = torch.tensor(action, dtype=torch.long).to(self.device)
        next_state = torch.from_numpy(next_state).float().to(self.device)
        
        #Select next state actions using the *primary* network
        argmax_a_q_sp = self.qnetwork_primary(next_state).argmax()
        #Get the next state action values using the *target* network
        q_sp = self.qnetwork_target(next_state).detach()
        
        #Index the q-values of the target network using the indices chosen by the primary,
        #so: primary network chooses action, target network evaluates action --> DDQN
        max_a_q_sp = q_sp[argmax_a_q_sp] * (1 - done)
        #Compute the target values
        target_q_sa = reward + self.gamma * max_a_q_sp
        #Get the actual action values
        q_sa = self.qnetwork_primary(state)[action]
        
        # Compute the TD_error
        TD_error = target_q_sa - q_sa
        
        #Add to the memory buffer
        self.memory.add(state, action, reward, next_state, done, torch.abs(TD_error))
        
        # Learn every UPDATE_EVERY time steps.
        self.t_step = (self.t_step + 1) % self.update_every
        if self.t_step == 0:
            # If enough samples are available in memory, get random subset and learn
            if len(self.memory) > self.batch_size:
                indices, probabilities, experiences = self.memory.sample()
                self.learn(indices, probabilities, experiences)
                
    def act(self, state: np.array, eps: float) -> int:
        """Returns actions for given state as per current policy"""
        state = torch.from_numpy(state).float().unsqueeze(0).to(self.device)
        self.qnetwork_primary.eval()
        with torch.no_grad():
            action_values = self.qnetwork_primary(state)
        self.qnetwork_primary.train()
        
        #Epsilon-greedy action selection 
        if random.random() > eps:
            return np.argmax(action_values.cpu().data.numpy())
        return random.choice(np.arange(self.action_size))
                
    def learn(self, indices: np.array, probabilities: torch.tensor, experiences: tuple) -> None:
        """The core of the algorithm, the actual updating of the network parameters"""
        
        states, actions, rewards, next_states, dones = experiences
    
        #Select next state actions using the *primary* network
        argmax_a_q_sp = self.qnetwork_primary(next_states).max(1)[1]
        #Get the next state action values using the *target* network
        q_sp = self.qnetwork_target(next_states).detach()
        #Index the q-values of the target network using the indices chosen by the primary,
        #so: primary network chooses action, target network evaluates action --> DDQN
        max_a_q_sp = q_sp[np.arange(self.batch_size), argmax_a_q_sp].unsqueeze(1) * (1 - dones)
        #Compute the target values
        target_q_sa = rewards + self.gamma * max_a_q_sp
        #Get the actual action values
        q_sa = self.qnetwork_primary(states).gather(1, actions)
        
        # Compute the new TD_errors
        TD_errors = target_q_sa - q_sa
        
        # Update the TD_errors for the sampled experiences
        new_priorities = torch.abs(TD_errors)
        self.memory.update(indices, new_priorities)
        
        # Compute Importance Sampling weights
        weights_is = torch.pow((self.buffer_size * probabilities), -self.beta)
        norm_weights = (weights_is/weights_is.max()).to(self.device)
        
        #Normalize actual & target values
        normed_q_sa = norm_weights * q_sa
        normed_target = norm_weights * target_q_sa
        
        # Compute loss
        loss = F.mse_loss(normed_q_sa, normed_target)
        
        # Minimize the loss
        self.optimizer.zero_grad()
        loss.backward()
        #Clip gradients if necessary, not yet active
        #torch.nn.utils.clip_grad_norm_(self.qnetwork_primary.parameters(), self.max_gradient_norm)
        self.optimizer.step()
        
        # ------------------- update target network ------------------- #
        self.soft_update(self.qnetwork_primary, self.qnetwork_target)
        
    def soft_update(self, primary: DuelingQNetwork, secondary: DuelingQNetwork) -> None:
        """Soft update model parameters.
        θ_target = τ*θ_local + (1 - τ)*θ_target
        """
        for target_param, local_param in zip(secondary.parameters(), primary.parameters()):
            target_param.data.copy_(self.tau * local_param.data + (1.0 - self.tau) * target_param.data)