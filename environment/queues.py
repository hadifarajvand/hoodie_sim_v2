from .task import Task
from utils import merge_dicts
import queue
import math
class TaskQueue():
    def __init__(self, queue_type:str="generic", node_id:int|None=None)->None:
        self.queue_type = queue_type
        self.node_id = node_id
        self.reset()
        
    def reset(self)->None:
        self.current_time=0
        self.queue_length = 0
        self.queue = queue.Queue()
        self.current_task = Task()
        self.arrivals_this_step = 0
        self.departures_this_step = 0
        self.drops_this_step = 0
    
    def add_task(self,
                 task:Task,
                 current_time:int|None=None)->None:
        if current_time is not None:
            task.queue_enter_time = current_time
        if self.is_empty():
            self.current_task = task.copy()
        else:
            self.queue.put(task.copy())
        self.queue_length += task.get_size()
        self.arrivals_this_step += 1
        recorder = getattr(Task, "trace_recorder", None)
        if recorder is not None:
            recorder.note_queue_enter(task, episode_id=getattr(recorder, "_episode_id", None), time=current_time if current_time is not None else self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        
    def is_empty(self) -> bool:
        return self.queue.empty() and self.current_task.is_empty() 
    
    def current_task_is_timed_out(self)->bool:
        return self.current_time > self.current_task.get_timeout()

    def get_first_non_empty_element(self) ->int:
        self.current_time +=1
        rewards =  0
        if self.current_task.is_empty():
            if self.queue.empty():
                return rewards
            else:
                self.current_task = self.queue.get()
                recorder = getattr(Task, "trace_recorder", None)
                if recorder is not None and self.current_task.service_start_time is None:
                    self.current_task.service_start_time = self.current_time
                    recorder.note_service_start(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        while self.current_task_is_timed_out():
            self.queue_length -= self.current_task.get_remaining_size()
            rewards += self.current_task.drop_task(drop_time=self.current_time, reason="timeout")
            self.drops_this_step += 1
            recorder = getattr(Task, "trace_recorder", None)
            if recorder is not None:
                recorder.note_drop(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type, reason="timeout")
            if self.queue.empty():
                return rewards
            else:
                self.current_task = self.queue.get()
                recorder = getattr(Task, "trace_recorder", None)
                if recorder is not None and self.current_task.service_start_time is None:
                    self.current_task.service_start_time = self.current_time
                    recorder.note_service_start(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        return rewards
    
    def get_waiting_time(self):
        raise NotImplementedError("Waiting time is not implemented for this queue (Probably public queue)")
    def get_queue_length(self):
        return self.queue_length

    def get_pending_tasks(self):
        tasks = []
        if not self.current_task.is_empty():
            tasks.append(self.current_task)
        tasks.extend(list(self.queue.queue))
        return tasks

    def get_trace_queue_length(self):
        total = 0.0
        if not self.current_task.is_empty():
            total += self.current_task.get_remaining_size()
        for item in list(self.queue.queue):
            total += item.get_remaining_size()
        return total

class ProcessingQueue(TaskQueue):
    def __init__(self,computational_capacity):
        super().__init__(queue_type="private")
        self.computational_capacity = computational_capacity
        self.waiting_time =0
    def reset(self):
        super().reset()
        self.waiting_time =0      
    
    def update_waiting_time(self,task):
        process_per_time_period = self.computational_capacity / task.get_density()
        time_to_process_task = math.ceil(task.get_size()/process_per_time_period)
        timeout_time = max(0,task.get_relative_timeout()-self.waiting_time)
        self.waiting_time += min(timeout_time,time_to_process_task)

    def _task_processing_time(self, task):
        process_per_time_period = self.computational_capacity / task.get_density()
        return math.ceil(task.get_remaining_size() / process_per_time_period)

    def get_waiting_time(self):
        if self.current_task.is_empty():
            return 0
        waiting = self._task_processing_time(self.current_task)
        for task in list(self.queue.queue):
            waiting += self._task_processing_time(task)
        return waiting
        
    def add_task(self,task, current_time=None):
        super().add_task(task, current_time=self.current_time if current_time is None else current_time)
        self.update_waiting_time(task)
        
        
    def step(self):
        if self.waiting_time>0:
            self.waiting_time -=1
        rewards = self.get_first_non_empty_element()
        if self.current_task.is_empty():
            return rewards
        recorder = getattr(Task, "trace_recorder", None)
        if recorder is not None and self.current_task.service_start_time is None:
            self.current_task.service_start_time = self.current_time
            recorder.note_service_start(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        rewards += self.current_task.process(self.computational_capacity,self.current_time)
        if self.current_task.is_empty():
            self.departures_this_step += 1
            recorder = getattr(Task, "trace_recorder", None)
            if recorder is not None:
                recorder.note_service_end(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        return rewards
    
    

class OffloadingQueue(TaskQueue):
    def __init__(self,offloading_capacities):   
        super().__init__(queue_type="offloading")
        self.offloading_capacities = offloading_capacities
        self.reset()
    def reset(self):
        super().reset()
        self.waiting_time =0
    
    def update_waiting_time(self, task):
        target_server_id = task.get_target_server_id()
        offloading_capacity = self.offloading_capacities[target_server_id]
        time_to_transmit_task =  math.ceil(task.get_size()/ offloading_capacity)
        timeout_time = max(0,task.get_relative_timeout()- self.waiting_time)
        self.waiting_time += min(timeout_time,time_to_transmit_task)

    def _task_transmission_time(self, task):
        target_server_id = task.get_target_server_id()
        offloading_capacity = self.offloading_capacities[target_server_id]
        return math.ceil(task.get_remaining_size() / offloading_capacity)

    def get_waiting_time(self):
        if self.current_task.is_empty():
            return 0
        waiting = self._task_transmission_time(self.current_task)
        for task in list(self.queue.queue):
            waiting += self._task_transmission_time(task)
        return waiting
        
    
    def add_task(self,task, current_time=None):
        super().add_task(task, current_time=self.current_time if current_time is None else current_time)
        self.update_waiting_time(task)
        
    def step(self):
        if self.waiting_time>0:
            self.waiting_time -=1
        transmited_task = None
        reward = self.get_first_non_empty_element()
        if self.current_task.is_empty():
            return transmited_task,reward

        target_server_id = self.current_task.get_target_server_id()
        offloading_capacity = self.offloading_capacities[target_server_id]
        recorder = getattr(Task, "trace_recorder", None)
        if recorder is not None and self.current_task.service_start_time is None:
            self.current_task.service_start_time = self.current_time
            recorder.note_service_start(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        transmited_task = self.current_task.transmit(offloading_capacity)
        if transmited_task is not None:
            self.departures_this_step += 1
        return transmited_task,reward
    
class PublicQueue(TaskQueue):
    def __init__(self, node_id=None, source_id=None):
        super().__init__(queue_type="public", node_id=node_id)
        self.source_id = source_id
    def step(self,computational_capacity):
        reward = 0
        if self.current_task.is_empty():
            return reward
        recorder = getattr(Task, "trace_recorder", None)
        if recorder is not None and self.current_task.service_start_time is None:
            self.current_task.service_start_time = self.current_time
            recorder.note_service_start(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        reward, task_processed = self.current_task.public_process(computational_capacity,self.current_time)
        self.queue_length -= task_processed
        if self.current_task.is_empty():
            self.departures_this_step += 1
            if recorder is not None:
                recorder.note_service_end(self.current_task, episode_id=getattr(recorder, "_episode_id", None), time=self.current_time, node_id=self.node_id if self.node_id is not None else -1, queue_type=self.queue_type)
        return reward

    def estimate_waiting_time(self, computational_capacity: float) -> int:
        if self.is_empty():
            return 0
        waiting = 0
        for task in self.get_pending_tasks():
            waiting += math.ceil(task.get_remaining_size() * task.get_density() / computational_capacity)
        return waiting
                    

class PublicQueueManager():
    def __init__(self,
                 id,
                 computational_capacity,
                 supporting_servers):
        self.id = id
        self.computational_capacity = computational_capacity
        self.supporting_servers = supporting_servers
        self.public_queues ={}
        for server_id in self.supporting_servers:
            self.public_queues[server_id] = PublicQueue(node_id=self.id, source_id=server_id)
       
    
    def reset(self):
        for _,q in self.public_queues.items():
            q.reset()
    
    def get_public_queue_server_length(self,server_id):
        return self.public_queues[server_id].queue_length
    
    def get_priorities(self):
        active_queues = 0
        for _,q in self.public_queues.items():
            if not q.is_empty():
                active_queues += 1
        return active_queues
    def get_active_queues(self):
        active_queues =0
        for _,q in self.public_queues.items():
            if not q.is_empty():
                active_queues +=1
        return active_queues
        
    def add_tasks(self,recieved_tasks=[], current_time:int|None=None):
        for task in recieved_tasks:
            assert task.get_target_server_id() == self.id
            origin_server_id = task.get_origin_server_id()
            self.public_queues[origin_server_id].add_task(task, current_time=current_time)
    
    def step(self):
        drop_rewards ={}
        for server_id in self.supporting_servers:
            drop_rewards[server_id]= self.public_queues[server_id].get_first_non_empty_element()

        finished_rewards = {}
        active_queues= self.get_active_queues()
        total_priority = self.get_priorities()
        if active_queues!=0:
            distributed_computational_capacity = self.computational_capacity/active_queues
        else:
            distributed_computational_capacity = 0
       
        for server_id in self.supporting_servers:
            finished_rewards[server_id]= self.public_queues[server_id].step(distributed_computational_capacity)
         
        rewards = merge_dicts(drop_rewards,finished_rewards)
        return rewards
    
    
    def get_queue_lengths(self):
        queue_lengths = {}
        for server_id in self.supporting_servers:
            queue_lengths[server_id] = self.public_queues[server_id].get_queue_length()
        return queue_lengths

    def get_queue_snapshots(self):
        snapshots = {}
        for server_id in self.supporting_servers:
            snapshots[server_id] = self.public_queues[server_id].get_pending_tasks()
        return snapshots

    def estimate_waiting_time(self, source_id, candidate_becomes_active: bool = False):
        queue = self.public_queues[source_id]
        if queue.is_empty():
            return 0
        active_queues = self.get_active_queues()
        if candidate_becomes_active and queue.is_empty():
            active_queues += 1
        if active_queues == 0:
            return 0
        distributed_capacity = self.computational_capacity / active_queues
        return queue.estimate_waiting_time(distributed_capacity)
