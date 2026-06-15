import numpy as np
from .queues import ProcessingQueue,OffloadingQueue,PublicQueueManager
from .action_model import TwoStageAction


class Server():
    def __init__(self, 
                 id :int, 
                 private_queue_computational_capacity :float,
                 public_queues_computational_capacity :float,
                 outbound_connections,
                 inbound_connections,
                 cloud_node_id: int | None = None,
                 cloud_offloading_capacity: float | None = None,
                 vertical_offloading_rate: float | None = None):
        self.id=id
        self.private_queue_computational_capacity = private_queue_computational_capacity
        self.public_queues_computational_capacity = public_queues_computational_capacity
       
        
        self.processing_queue = ProcessingQueue(self.private_queue_computational_capacity)
        
        outbound_connections = np.array(outbound_connections)
        self.offloading_servers = np.where(outbound_connections!=0)[0]
        self.offloading_capacities = {s:outbound_connections[s] for s in self.offloading_servers}
        vertical_rate = float(vertical_offloading_rate) if vertical_offloading_rate is not None else (float(cloud_offloading_capacity) if cloud_offloading_capacity is not None else None)
        if cloud_node_id is not None and vertical_rate is not None:
            self.offloading_capacities[int(cloud_node_id)] = vertical_rate
        self.offloading_queue = OffloadingQueue(offloading_capacities = self.offloading_capacities, vertical_offloading_rate=vertical_rate)

        inbound_connections = np.array(inbound_connections)
        self.supporting_servers =  np.where(inbound_connections!=0)[0]
        self.public_queue_manager = PublicQueueManager(id=self.id,
                                                       computational_capacity=  self.public_queues_computational_capacity,
                                                       supporting_servers= self.supporting_servers)
        self.current_time=0

    def reset(self):
            self.current_time=0
            self.processing_queue.reset()
            self.public_queue_manager.reset()
            self.offloading_queue.reset()   
    
    def get_waiting_times(self):
        return  self.processing_queue.get_waiting_time(),self.offloading_queue.get_waiting_time()
    
    def add_offloaded_tasks(self,offloaded_tasks, current_time=None):
        self.public_queue_manager.add_tasks(offloaded_tasks, current_time=current_time)

    def step(self,action=None,local_task=None,current_time=None):
        action_decision: TwoStageAction | None = action if isinstance(action, TwoStageAction) else None
        if local_task:
            local_task.set_origin_server_id(self.id)
            local_task.selected_action = action_decision.raw_action_id if action_decision is not None else action
            local_task.processing_node = self.id if action_decision is None or action_decision.first_stage_decision == "local" else None
            if action_decision is None or action_decision.first_stage_decision == "local":
                self.processing_queue.add_task(local_task, current_time=current_time)
            else:
                local_task.routing_metadata["paper_destination_nodes"] = list(action_decision.paper_destination_nodes)
                local_task.routing_metadata["paper_d_nk_2"] = [0 for _ in action_decision.paper_d_nk_2]
                local_task.routing_metadata["paper_destination_node_id"] = None
                local_task.routing_metadata["dm2_pending"] = True
                local_task.routing_metadata["dm2_timing"] = "offloading_queue_exit"
                local_task.routing_metadata["requires_separate_dm2_at_offloading_queue_exit"] = True
                self.offloading_queue.add_task(local_task, current_time=current_time)
                
        local_reward = self.processing_queue.step()
        transmited_task,offloaded_reward  = self.offloading_queue.step()
        foreign_rewards =  self.public_queue_manager.step()
        total_rewards=  foreign_rewards
        total_rewards[self.id] = local_reward + offloaded_reward
        return transmited_task,total_rewards
    
    def get_features(self):
        private_waiting_time,public_waiting_time = self.get_waiting_times()
        public_queues = self.public_queue_manager.get_queue_lengths()
        return np.array([private_waiting_time,
                         public_waiting_time]),public_queues
    
    def get_number_of_features(self):
        features,_  = self.get_features()
        return len(features)
    def get_number_of_actions(self):
        return 2 + len(self.offloading_servers)
    
    def get_offliading_servers(self):
        return self.offloading_servers
    
    
    def get_active_queues(self):
        active_queues  =self.public_queue_manager.get_active_queues()
        return active_queues

    def get_active_load(self) -> int:
        active = 0
        if not self.processing_queue.current_task.is_empty():
            active += 1
        if not self.offloading_queue.current_task.is_empty():
            active += 1
        active += self.public_queue_manager.get_active_queues()
        return active

    def get_public_queue_snapshots(self):
        return self.public_queue_manager.get_queue_snapshots()

    def estimate_public_queue_wait(self, source_id):
        return self.public_queue_manager.estimate_waiting_time(source_id)
    
    
    def get_supporting_servers(self):
        return self.supporting_servers
