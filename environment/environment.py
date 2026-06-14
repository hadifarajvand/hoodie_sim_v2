from .server import Server
from .cloud import Cloud
from .task_generator import TaskGenerator
from .matchmaker import Matchmaker
from .action_model import TopologyAdapter
from utils import merge_dicts,dict_to_array,remove_diagonal_and_reshape
from phase1_tracing import TraceRecorder
from .task import Task
import numpy as np
import torch
import math
from collections import deque
class Environment():
    def __init__(self, 
                 static_frequency,
                 number_of_servers,
                 private_cpu_capacities,
                 public_cpu_capacities,
                 connection_matrix,
                 cloud_computational_capacity,
                 episode_time,
                 task_arrive_probabilities,
                 task_size_mins,
                 task_size_maxs,
                 task_size_distributions,
                timeout_delay_mins,
                timeout_delay_maxs,
                timeout_delay_distributions,
                priotiry_mins,
                priotiry_maxs,
                priotiry_distributions,
                computational_density_mins,
                computational_density_maxs,
                computational_density_distributions,
                 drop_penalty_mins,
                 drop_penalty_maxs,
                 drop_penalty_distributions,
                 number_of_clouds=1,
                 paper_state_window=4,
                 trace_recorder:TraceRecorder|None=None) -> None:
        self.number_of_servers = number_of_servers
        self.number_of_clouds = number_of_clouds
        self.paper_state_window = paper_state_window
        self.current_time = 0
        self.episode_time_end = episode_time +max(timeout_delay_maxs)
        self.connection_matrix=  connection_matrix
        self.topology = TopologyAdapter.from_connection_matrix(connection_matrix, cloud_node_id=number_of_servers)
        self.trace_recorder = trace_recorder
        self.paper_state_history = [deque(maxlen=self.paper_state_window) for _ in range(self.number_of_servers)]
        self.last_public_queue_vector = [np.full(self.number_of_servers + 1, np.nan, dtype=np.float32) for _ in range(self.number_of_servers)]
        self.last_paper_queue_arrivals = [0 for _ in range(self.number_of_servers + self.number_of_clouds)]
        Task.trace_recorder = trace_recorder
        get_column = lambda m, i: [row[i] for row in m]
        self.task_generators = [TaskGenerator(id=i,
                                              episode_time=episode_time,
                                              task_arrive_probability=task_arrive_probabilities[i],
                                              size_min=task_size_mins[i],
                                              size_max = task_size_maxs[i],
                                                size_distribution = task_size_distributions[i],
                                                timeout_delay_min = timeout_delay_mins[i],
                                                timeout_delay_max = timeout_delay_maxs[i],
                                                timeout_delay_distribution = timeout_delay_distributions[i],
                                                priotiry_min = priotiry_mins[i],
                                                priotiry_max = priotiry_maxs[i],
                                                priotiry_distribution = priotiry_distributions[i],
                                                computational_density_min = computational_density_mins[i],
                                                computational_density_max = computational_density_maxs[i],
                                                computational_density_distribution = computational_density_distributions[i],
                                                drop_penalty_min = drop_penalty_mins[i],
                                                drop_penalty_max = drop_penalty_maxs[i],
                                                drop_penalty_distribution = drop_penalty_distributions[i])
                                for i in range(number_of_servers)]         
        self.servers = [Server( id=i,
                                private_queue_computational_capacity=  private_cpu_capacities[i],
                                public_queues_computational_capacity= public_cpu_capacities[i],
                                outbound_connections=  self.connection_matrix[i],
                                inbound_connections=get_column(self.connection_matrix,i)) 
                        for i in range(number_of_servers)]
       
        self.matchmakers = [Matchmaker(id=s.id,
                                       offloading_servers=s.get_offliading_servers(),
                                       cloud_id=self.number_of_servers,
                                       topology=self.topology)
                            for s in self.servers]
        self.cloud = Cloud(number_of_servers=number_of_servers,
                           computational_capacity=cloud_computational_capacity)
        
        previous_recorder = Task.trace_recorder
        Task.trace_recorder = None
        self.number_of_task_features=  self.task_generators[0].generate().get_number_of_features()
        Task.trace_recorder = previous_recorder
        self.number_of_server_features = self.servers[0].get_number_of_features()
        self.number_of_features = self.number_of_task_features + self.number_of_server_features
        self.static_frequency = static_frequency
        self.static_counter = 0
        self.episode_id = 0
        
        self.max_reward = max(drop_penalty_maxs)
        self.max_waiting_time = max(timeout_delay_maxs)
        self.get_task_features_maxs()
        self.reset()
    def reset(self):
        
        
        
        if self.static_frequency:
            if self.static_counter % self.static_frequency ==0:
                np.random.seed(42)
                torch.manual_seed(42)
                self.static_counter+=1
        self.current_time = 0
        for task_generator in self.task_generators:
            task_generator.reset()
        for server in self.servers:
            server.reset()
        self.cloud.reset()
        self.reset_transmitted_tasks()
        self.paper_state_history = [deque(maxlen=self.paper_state_window) for _ in range(self.number_of_servers)]
        self.last_public_queue_vector = [np.full(self.number_of_servers + 1, np.nan, dtype=np.float32) for _ in range(self.number_of_servers)]
        self.last_paper_queue_arrivals = [0 for _ in range(self.number_of_servers + self.number_of_clouds)]
        self.last_action_decisions = [None for _ in range(self.number_of_servers)]
        if self.trace_recorder is not None:
            self.trace_recorder.start_episode(self.episode_id)
        self.tasks= [t.step() for t in self.task_generators]
        self._refresh_paper_state_history()
        
        observations = self.pack_observation()
        done = False
        info = {}
        self.actions  =[{
                'local':0,
                'horisontal':0,
                'cloud':0
            }
            for _ in range(self.number_of_servers)]
        return observations,done, info
    def reset_transmitted_tasks(self):
        self.horisontal_transmitted_tasks = [[] for _ in range(self.number_of_servers+self.number_of_clouds)]
    
    def scale_rewards(self,reward):
        return reward/self.max_reward
    
    def get_task_features_maxs(self):
        self.feature_maxes = self.task_generators[0].get_maxs()
        for g in self.task_generators:
            np.maximum(self.feature_maxes, g.get_maxs(), out=self.feature_maxes)  # Compare and store the max values

    def scale_task_features(self,task_features):
        return task_features/self.feature_maxes
    def scale_waiting_times(self,waiting_times):
        return waiting_times/self.max_waiting_time
    def pack_observation(self):
        server_observations = np.zeros((self.number_of_servers,self.number_of_features))
        public_queues_legth  = [np.array([]) for key in range(self.number_of_servers+self.number_of_clouds)]
        assert len(self.tasks) == self.number_of_servers
        for s in range(self.number_of_servers):
            if self.tasks[s]:
                task_features = self.tasks[s].get_features()
            else:
                task_features = np.zeros(self.number_of_task_features)
            task_features = self.scale_task_features(task_features)
            waiting_times,server_public_queues = self.servers[s].get_features()     
            waiting_times = self.scale_waiting_times(waiting_times)       
            server_features = np.concatenate([task_features,waiting_times])
            server_observations[s] = server_features
        
            for q in server_public_queues:
                public_queues_legth[q] = np.append(public_queues_legth[q], server_public_queues[q])

        cloud_public_queues = self.cloud.get_features()
        for q in cloud_public_queues:
            public_queues_legth[q] = np.append(public_queues_legth[q], cloud_public_queues[q])      
            
        local_observations = []
        for i in range(len(server_observations)):
            local_observations.append(np.append(server_observations[i],public_queues_legth[i]))

        active_queues = [np.array([]) for _ in range(self.number_of_servers) ]
        for s in self.servers:
            server_active_queues = s.get_active_queues()
            supporting_servers  = s.get_supporting_servers()
            for target_server in supporting_servers:
                active_queues[target_server] = np.append( active_queues[target_server],server_active_queues)
            
        cloud_active_queeus = self.cloud.get_active_queues()
        supporting_servers  = self.cloud.get_supporting_servers()

        for target_server in supporting_servers:
            active_queues[target_server] = np.append( active_queues[target_server],cloud_active_queeus)
            
        return local_observations,active_queues
    
    def add_action_info(self,action,server_id,task):
        if task:
            if action ==server_id:
                self.actions[server_id]['local'] +=1
            elif action == self.number_of_servers:
                self.actions[server_id]['cloud'] +=1
            else:
                self.actions[server_id]['horisontal'] +=1
    def step(self,actions):


        tasks_arrived = [0 if t is None else 1 for t in self.tasks]
        
        assert len(actions) == self.number_of_servers
        if self.current_time >=self.episode_time_end:
            done = True
        else:
            done = False
        self.current_time +=1
        
        for s in self.servers:
            s.add_offloaded_tasks(self.horisontal_transmitted_tasks[s.id], current_time=self.current_time)
        self.cloud.add_offloaded_tasks(self.horisontal_transmitted_tasks[-1], current_time=self.current_time)
        self.last_paper_queue_arrivals = [0 for _ in range(self.number_of_servers + self.number_of_clouds)]
        for server_id in range(self.number_of_servers):
            self.last_paper_queue_arrivals[server_id] = int(tasks_arrived[server_id]) + len(self.horisontal_transmitted_tasks[server_id])
        self.last_paper_queue_arrivals[-1] = len(self.horisontal_transmitted_tasks[-1])
        self.reset_transmitted_tasks()
        
        rewards = self.cloud.step()
        
        for server_id in range(self.number_of_servers):
            action_decision = self.matchmakers[server_id].decode_action(server_id, actions[server_id], strict=True)
            self.last_action_decisions[server_id] = action_decision
            action = action_decision.legacy_target_node_id
            self.add_action_info(action,server_id,self.tasks[server_id])
            transmited_task, server_reward = self.servers[server_id].step(action,self.tasks[server_id],current_time=self.current_time)
            rewards = merge_dicts(rewards,server_reward)
            if transmited_task:
                origin_server_id = transmited_task.get_origin_server_id()
                assert origin_server_id == server_id
                target_server_id = transmited_task.get_target_server_id()
                
                self.horisontal_transmitted_tasks[target_server_id].append(transmited_task) 

        self.tasks= [t.step() for t in self.task_generators]     
               
        observations = self.pack_observation()
        rewards  = dict_to_array(rewards,self.number_of_servers)
        rewards = self.scale_rewards(rewards)
        rewards = -rewards
        
        # tasks_dropped = 
        
        info  ={}
        info['rewards'] = rewards
        info['tasks_arrived'] = np.array(tasks_arrived)
        info['tasks_dropped'] = -np.ceil(rewards)
        if self.trace_recorder is not None:
            self._record_queue_traces()
        
        return observations,rewards, done, info

    def _compute_active_load_vector(self):
        load = np.zeros(self.number_of_servers + 1, dtype=np.float32)
        for server in self.servers:
            load[server.id] = float(server.get_active_load())
        load[self.number_of_servers] = float(self.cloud.get_active_load())
        return load

    def _refresh_paper_state_history(self):
        active_load_vector = self._compute_active_load_vector()
        public_queue_vector = np.full(self.number_of_servers + 1, np.nan, dtype=np.float32)
        for server in self.servers:
            public_queues = server.public_queue_manager.get_queue_lengths()
            for source_id, queue_length in public_queues.items():
                public_queue_vector[source_id] = float(queue_length)
        cloud_queues = self.cloud.get_features()
        for source_id, queue_length in cloud_queues.items():
            public_queue_vector[source_id] = float(queue_length)
        for agent_id in range(self.number_of_servers):
            self.paper_state_history[agent_id].append(active_load_vector.copy())
            self.last_public_queue_vector[agent_id] = public_queue_vector.copy()
        return active_load_vector, public_queue_vector

    def get_paper_state(self, agent_id: int):
        task = self.tasks[agent_id]
        server = self.servers[agent_id]
        x_n_t = 0 if task is None or task.is_empty() else 1
        eta_n = None if task is None else float(task.get_size())
        w_priv_n, w_off_n = server.get_waiting_times()
        l_pub_n_prev = self.last_public_queue_vector[agent_id]
        active_load_vector = self._compute_active_load_vector()
        history = list(self.paper_state_history[agent_id])
        while len(history) < self.paper_state_window:
            history.insert(0, np.full(self.number_of_servers + 1, np.nan, dtype=np.float32))
        L_t = np.asarray(history, dtype=np.float32)
        predicted_next_load = active_load_vector.copy()
        unavailable_fields = []
        approximation_warnings = []
        if eta_n is None:
            unavailable_fields.append("eta_n")
        if w_priv_n is None:
            unavailable_fields.append("w_priv_n")
        if w_off_n is None:
            unavailable_fields.append("w_off_n")
        if np.isnan(l_pub_n_prev).all():
            unavailable_fields.append("l_pub_n_prev")
        if L_t.size == 0:
            unavailable_fields.append("L(t)")
        approximation_warnings.append("predicted_next_load uses persistence_baseline")
        state_vector = np.concatenate(
            [
                np.asarray([
                    np.nan if eta_n is None else eta_n,
                    np.nan if w_priv_n is None else float(w_priv_n),
                    np.nan if w_off_n is None else float(w_off_n),
                ], dtype=np.float32),
                l_pub_n_prev.astype(np.float32).reshape(-1),
                L_t.astype(np.float32).reshape(-1),
                predicted_next_load.astype(np.float32).reshape(-1),
            ]
        )
        return {
            "episode_id": self.episode_id,
            "time": self.current_time,
            "agent_id": agent_id,
            "x_n_t": x_n_t,
            "task_id": None if task is None or task.is_empty() else task.task_id,
            "eta_n": eta_n,
            "w_priv_n": float(w_priv_n) if w_priv_n is not None else None,
            "w_off_n": float(w_off_n) if w_off_n is not None else None,
            "l_pub_n_prev": l_pub_n_prev,
            "active_load_vector": active_load_vector,
            "L_t": L_t,
            "predicted_next_load": predicted_next_load,
            "predicted_next_load_method": "persistence_baseline",
            "paper_lstm_forecast": False,
            "unavailable_fields": unavailable_fields,
            "approximation_warnings": approximation_warnings,
            "state_vector": state_vector,
            "state_dim": int(state_vector.shape[0]),
        }

    def _record_queue_traces(self):
        if self.trace_recorder is None:
            return
        episode_id = self.episode_id
        total_queue_length = 0.0
        for server in self.servers:
            node_u_n_t = int(self.last_paper_queue_arrivals[server.id]) if server.id < len(self.last_paper_queue_arrivals) else None
            q = server.processing_queue
            self.trace_recorder.note_queue_trace(
                episode_id=episode_id,
                time=self.current_time,
                node_id=server.id,
                queue_type="private",
                queue_length=q.get_trace_queue_length(),
                paper_u_n_t=node_u_n_t,
                arrivals=q.arrivals_this_step,
                departures=q.departures_this_step,
                drops=q.drops_this_step,
                cpu_allocated=server.private_queue_computational_capacity,
            )
            total_queue_length += q.get_queue_length()
            q.arrivals_this_step = 0
            q.departures_this_step = 0
            q.drops_this_step = 0
            oq = server.offloading_queue
            self.trace_recorder.note_queue_trace(
                episode_id=episode_id,
                time=self.current_time,
                node_id=server.id,
                queue_type="offloading",
                queue_length=oq.get_trace_queue_length(),
                paper_u_n_t=node_u_n_t,
                arrivals=oq.arrivals_this_step,
                departures=oq.departures_this_step,
                drops=oq.drops_this_step,
                cpu_allocated=server.public_queues_computational_capacity,
            )
            total_queue_length += oq.get_queue_length()
            oq.arrivals_this_step = 0
            oq.departures_this_step = 0
            oq.drops_this_step = 0
            for source_id, pq in server.public_queue_manager.public_queues.items():
                self.trace_recorder.note_queue_trace(
                    episode_id=episode_id,
                    time=self.current_time,
                    node_id=server.id,
                    queue_type=f"public:{source_id}",
                    queue_length=pq.get_trace_queue_length(),
                    paper_u_n_t=node_u_n_t,
                    arrivals=pq.arrivals_this_step,
                    departures=pq.departures_this_step,
                    drops=pq.drops_this_step,
                    cpu_allocated=server.public_queues_computational_capacity,
                )
                total_queue_length += pq.get_queue_length()
                pq.arrivals_this_step = 0
                pq.departures_this_step = 0
                pq.drops_this_step = 0
        cloud_queue_length = 0.0
        for pq in self.cloud.public_queue_manager.public_queues.values():
            cloud_queue_length += pq.get_trace_queue_length()
        self.trace_recorder.note_queue_trace(
            episode_id=episode_id,
            time=self.current_time,
            node_id=self.number_of_servers,
            queue_type="cloud",
            queue_length=cloud_queue_length,
            paper_u_n_t=int(self.last_paper_queue_arrivals[-1]) if self.last_paper_queue_arrivals else None,
            arrivals=int(self.last_paper_queue_arrivals[-1]) if self.last_paper_queue_arrivals else 0,
            departures=0,
            drops=0,
            cpu_allocated=self.cloud.computational_capacity,
        )
        
    
    def get_server_dimensions(self,id):
        
        local_observations, active_queues = self.pack_observation()
        local_observations = local_observations[id]
        active_queues  =  active_queues[id]
        return (len(local_observations),
                len(active_queues),
                self.matchmakers[id].get_number_of_actions()
        )
    def get_task_features(self):
        return self.task_generators[0].get_number_of_features()
    
    def get_episode_actions(self):
        return self.actions
    
    def get_foreign_cpus(self,id):
        available_servers = np.array(self.matchmakers[id].get_rows())
        available_servers = available_servers[available_servers!=id]
        available_servers = available_servers[available_servers!=self.number_of_servers]
        public_cpus = np.array([s.public_queues_computational_capacity for s in self.servers])
        
        available_public_cpus = public_cpus[available_servers]
        
        available_public_cpus = np.append(available_public_cpus, self.cloud.computational_capacity)
        return available_public_cpus
